"""Repository em memória: mesmo contrato do Postgres, usado nos testes unitários."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime

from radar.dominio.modelos import Contratacao, LicitacaoAberta


class RepositorioMemoria:
    def __init__(self, contratacoes: Iterable[Contratacao] = ()) -> None:
        self.contratacoes: dict[str, Contratacao] = {c.numero_controle_pncp: c for c in contratacoes}

    def listar_abertas(
        self,
        *,
        uf: str | None = None,
        texto: str | None = None,
        referencia: datetime | None = None,
        limite: int = 100,
    ) -> list[LicitacaoAberta]:
        agora = referencia or datetime.now(UTC)
        abertas = [
            c
            for c in self.contratacoes.values()
            if c.data_encerramento_proposta is not None
            and c.data_encerramento_proposta >= agora
            and (uf is None or c.unidade.uf_sigla == uf)
            and (texto is None or texto.lower() in c.objeto_compra.lower())
        ]
        abertas.sort(key=lambda c: (c.data_encerramento_proposta, c.numero_controle_pncp))
        return [
            LicitacaoAberta(
                numero_controle_pncp=c.numero_controle_pncp,
                orgao=c.orgao.razao_social,
                municipio=c.unidade.municipio_nome,
                uf=c.unidade.uf_sigla,
                modalidade=c.modalidade.nome or str(c.modalidade.codigo),
                objeto=c.objeto_compra,
                valor_total_estimado=c.valor_total_estimado,
                data_encerramento_proposta=c.data_encerramento_proposta,
                link_pncp=c.link_pncp,
            )
            for c in abertas[:limite]
        ]

    def salvar_contratacoes(self, contratacoes: Iterable[Contratacao]) -> int:
        n = 0
        for c in contratacoes:
            self.contratacoes[c.numero_controle_pncp] = c
            n += 1
        return n
