"""Repository com Postgres (psycopg 3, SQL explícito, sem ORM)."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime

import psycopg

from radar.dominio.modelos import Codigo, Contratacao, LicitacaoAberta, link_pncp

SQL_LISTAR_ABERTAS = """
    select c.numero_controle_pncp,
           o.razao_social          as orgao,
           u.municipio_nome        as municipio,
           u.uf_sigla              as uf,
           m.nome                  as modalidade,
           c.objeto_compra         as objeto,
           c.valor_total_estimado,
           c.data_encerramento_proposta,
           c.cnpj_orgao,
           c.ano_compra,
           c.sequencial_compra
      from radar.contratacao c
      join radar.orgao o              on o.cnpj = c.cnpj_orgao
      join radar.unidade u            on u.cnpj_orgao = c.cnpj_orgao and u.codigo_unidade = c.codigo_unidade
      join radar.dominio_modalidade m on m.codigo = c.modalidade_id
     where c.data_encerramento_proposta >= coalesce(%(referencia)s::timestamptz, now())
       and (%(uf)s::text is null or u.uf_sigla = %(uf)s::text)
       and (%(texto)s::text is null or c.objeto_compra ilike '%%' || %(texto)s::text || '%%')
     order by c.data_encerramento_proposta, c.numero_controle_pncp
     limit %(limite)s
"""

# Domínios citados por uma contratação: (tabela, atributo da Contratacao)
DOMINIOS_DA_CONTRATACAO = [
    ("dominio_modalidade", "modalidade"),
    ("dominio_modo_disputa", "modo_disputa"),
    ("dominio_situacao_compra", "situacao_compra"),
    ("dominio_instrumento_convocatorio", "instrumento_convocatorio"),
    ("dominio_amparo_legal", "amparo_legal"),
]

SQL_UPSERT_CONTRATACAO = """
    insert into radar.contratacao (
        numero_controle_pncp, cnpj_orgao, codigo_unidade, ano_compra, sequencial_compra, numero_compra,
        processo, modalidade_id, modo_disputa_id, situacao_compra_id, instrumento_convocatorio_id,
        amparo_legal_codigo, srp, objeto_compra, informacao_complementar, valor_total_estimado,
        valor_total_homologado, data_publicacao_pncp, data_abertura_proposta, data_encerramento_proposta,
        data_atualizacao, link_sistema_origem
    ) values (
        %(numero_controle_pncp)s, %(cnpj_orgao)s, %(codigo_unidade)s, %(ano_compra)s, %(sequencial_compra)s,
        %(numero_compra)s, %(processo)s, %(modalidade_id)s, %(modo_disputa_id)s, %(situacao_compra_id)s,
        %(instrumento_convocatorio_id)s, %(amparo_legal_codigo)s, %(srp)s, %(objeto_compra)s,
        %(informacao_complementar)s, %(valor_total_estimado)s, %(valor_total_homologado)s,
        %(data_publicacao_pncp)s, %(data_abertura_proposta)s, %(data_encerramento_proposta)s,
        %(data_atualizacao)s, %(link_sistema_origem)s
    )
    on conflict (numero_controle_pncp) do update set
        situacao_compra_id = excluded.situacao_compra_id,
        objeto_compra = excluded.objeto_compra,
        informacao_complementar = excluded.informacao_complementar,
        valor_total_estimado = excluded.valor_total_estimado,
        valor_total_homologado = excluded.valor_total_homologado,
        data_abertura_proposta = excluded.data_abertura_proposta,
        data_encerramento_proposta = excluded.data_encerramento_proposta,
        data_atualizacao = excluded.data_atualizacao,
        carregado_em = now()
    where radar.contratacao.data_atualizacao is distinct from excluded.data_atualizacao
"""


class RepositorioPostgres:
    def __init__(self, conexao: psycopg.Connection) -> None:
        self.conexao = conexao

    def listar_abertas(
        self,
        *,
        uf: str | None = None,
        texto: str | None = None,
        referencia: datetime | None = None,
        limite: int = 100,
    ) -> list[LicitacaoAberta]:
        parametros = {"uf": uf, "texto": texto, "referencia": referencia, "limite": limite}
        with self.conexao.cursor() as cur:
            cur.execute(SQL_LISTAR_ABERTAS, parametros)
            linhas = cur.fetchall()
        return [
            LicitacaoAberta(
                numero_controle_pncp=r["numero_controle_pncp"],
                orgao=r["orgao"],
                municipio=r["municipio"],
                uf=r["uf"],
                modalidade=r["modalidade"],
                objeto=r["objeto"],
                valor_total_estimado=r["valor_total_estimado"],
                data_encerramento_proposta=r["data_encerramento_proposta"],
                link_pncp=link_pncp(r["cnpj_orgao"], r["ano_compra"], r["sequencial_compra"]),
            )
            for r in linhas
        ]

    def salvar_contratacoes(self, contratacoes: Iterable[Contratacao]) -> int:
        lista = list(contratacoes)
        if not lista:
            return 0
        with self.conexao.transaction(), self.conexao.cursor() as cur:
            cur.executemany(
                """insert into radar.orgao (cnpj, razao_social, esfera_id, poder_id)
                   values (%s, %s, %s, %s) on conflict (cnpj) do nothing""",
                list(
                    {(c.orgao.cnpj, c.orgao.razao_social, c.orgao.esfera_id, c.orgao.poder_id) for c in lista}
                ),
            )
            cur.executemany(
                """insert into radar.unidade (cnpj_orgao, codigo_unidade, nome_unidade, uf_sigla, uf_nome,
                                              municipio_nome, codigo_ibge)
                   values (%s, %s, %s, %s, %s, %s, %s) on conflict (cnpj_orgao, codigo_unidade) do nothing""",
                list(
                    {
                        (
                            u.cnpj_orgao,
                            u.codigo_unidade,
                            u.nome_unidade,
                            u.uf_sigla,
                            u.uf_nome,
                            u.municipio_nome,
                            u.codigo_ibge,
                        )
                        for u in (c.unidade for c in lista)
                    }
                ),
            )
            for tabela, atributo in DOMINIOS_DA_CONTRATACAO:
                codigos: set[Codigo] = {getattr(c, atributo) for c in lista if getattr(c, atributo)}
                if codigos:
                    cur.executemany(
                        f"insert into radar.{tabela} (codigo, nome) values (%s, %s) on conflict (codigo) do nothing",
                        [(cod.codigo, cod.nome or "(sem nome no PNCP)") for cod in codigos],
                    )
            cur.executemany(SQL_UPSERT_CONTRATACAO, [_parametros(c) for c in lista])
            # rowcount soma as linhas realmente inseridas ou atualizadas: uma contratação que voltou
            # igual (mesma data_atualizacao) não conta, porque o upsert é idempotente
            alteradas = cur.rowcount
        return alteradas


def _parametros(c: Contratacao) -> dict:
    return {
        "numero_controle_pncp": c.numero_controle_pncp,
        "cnpj_orgao": c.orgao.cnpj,
        "codigo_unidade": c.unidade.codigo_unidade,
        "ano_compra": c.ano_compra,
        "sequencial_compra": c.sequencial_compra,
        "numero_compra": c.numero_compra,
        "processo": c.processo,
        "modalidade_id": c.modalidade.codigo,
        "modo_disputa_id": c.modo_disputa.codigo if c.modo_disputa else None,
        "situacao_compra_id": c.situacao_compra.codigo if c.situacao_compra else None,
        "instrumento_convocatorio_id": c.instrumento_convocatorio.codigo
        if c.instrumento_convocatorio
        else None,
        "amparo_legal_codigo": c.amparo_legal.codigo if c.amparo_legal else None,
        "srp": c.srp,
        "objeto_compra": c.objeto_compra,
        "informacao_complementar": c.informacao_complementar,
        "valor_total_estimado": c.valor_total_estimado,
        "valor_total_homologado": c.valor_total_homologado,
        "data_publicacao_pncp": c.data_publicacao_pncp,
        "data_abertura_proposta": c.data_abertura_proposta,
        "data_encerramento_proposta": c.data_encerramento_proposta,
        "data_atualizacao": c.data_atualizacao,
        "link_sistema_origem": c.link_sistema_origem,
    }
