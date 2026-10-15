"""Adapter: traduz o JSON do PNCP para o modelo de domínio.

Por que um Adapter? Só este módulo conhece os nomes de campo da API (camelCase, objetos
aninhados como `orgaoEntidade` e `unidadeOrgao`). Se o PNCP mudar um campo — e isso acontece —,
o conserto fica aqui e o resto do sistema nem percebe.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from radar.dominio.modelos import Codigo, Contratacao, Orgao, Unidade

FUSO_BRASILIA = ZoneInfo("America/Sao_Paulo")


def para_data(valor: str | None) -> datetime | None:
    """O PNCP manda datas SEM fuso (ex.: '2026-10-15T08:59:00'). Elas estão no horário de Brasília."""
    if not valor:
        return None
    return datetime.fromisoformat(valor).replace(tzinfo=FUSO_BRASILIA)


def para_decimal(valor: Any) -> Decimal | None:
    # str() antes de Decimal evita herdar a imprecisão do float (0.1 vira 0.1, e não 0.1000000000000000055...)
    return None if valor is None else Decimal(str(valor))


def para_codigo(codigo: Any, nome: str | None) -> Codigo | None:
    return None if codigo is None else Codigo(int(codigo), nome)


class AdaptadorPncp:
    def contratacao(self, bruto: dict[str, Any]) -> Contratacao:
        orgao_json = bruto.get("orgaoEntidade") or {}
        unidade_json = bruto.get("unidadeOrgao") or {}
        amparo_json = bruto.get("amparoLegal") or {}

        orgao = Orgao(
            cnpj=orgao_json["cnpj"],
            razao_social=orgao_json.get("razaoSocial") or "",
            esfera_id=orgao_json.get("esferaId"),
            poder_id=orgao_json.get("poderId"),
        )
        unidade = Unidade(
            cnpj_orgao=orgao.cnpj,
            codigo_unidade=str(unidade_json.get("codigoUnidade")),
            nome_unidade=unidade_json.get("nomeUnidade"),
            uf_sigla=unidade_json.get("ufSigla"),
            uf_nome=unidade_json.get("ufNome"),
            municipio_nome=unidade_json.get("municipioNome"),
            codigo_ibge=unidade_json.get("codigoIbge"),
        )
        return Contratacao(
            numero_controle_pncp=bruto["numeroControlePNCP"],
            orgao=orgao,
            unidade=unidade,
            ano_compra=int(bruto["anoCompra"]),
            sequencial_compra=int(bruto["sequencialCompra"]),
            modalidade=Codigo(int(bruto["modalidadeId"]), bruto.get("modalidadeNome")),
            objeto_compra=bruto.get("objetoCompra") or "",
            numero_compra=bruto.get("numeroCompra"),
            processo=bruto.get("processo"),
            modo_disputa=para_codigo(bruto.get("modoDisputaId"), bruto.get("modoDisputaNome")),
            situacao_compra=para_codigo(bruto.get("situacaoCompraId"), bruto.get("situacaoCompraNome")),
            instrumento_convocatorio=para_codigo(
                bruto.get("tipoInstrumentoConvocatorioCodigo"), bruto.get("tipoInstrumentoConvocatorioNome")
            ),
            amparo_legal=para_codigo(amparo_json.get("codigo"), amparo_json.get("nome")),
            srp=bruto.get("srp"),
            informacao_complementar=bruto.get("informacaoComplementar"),
            valor_total_estimado=para_decimal(bruto.get("valorTotalEstimado")),
            valor_total_homologado=para_decimal(bruto.get("valorTotalHomologado")),
            data_publicacao_pncp=para_data(bruto.get("dataPublicacaoPncp")),
            data_abertura_proposta=para_data(bruto.get("dataAberturaProposta")),
            data_encerramento_proposta=para_data(bruto.get("dataEncerramentoProposta")),
            data_atualizacao=para_data(bruto.get("dataAtualizacao")),
            link_sistema_origem=bruto.get("linkSistemaOrigem"),
        )
