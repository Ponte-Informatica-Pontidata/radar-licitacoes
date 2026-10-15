"""Caso de uso: consultar licitações com proposta aberta."""

from __future__ import annotations

from datetime import datetime

from radar.dominio.modelos import LicitacaoAberta
from radar.persistencia.repositorio import RepositorioLicitacoes

LIMITE_MAXIMO = 500


class ServicoLicitacoes:
    def __init__(self, repositorio: RepositorioLicitacoes) -> None:
        self.repositorio = repositorio

    def abertas(
        self,
        uf: str | None = None,
        texto: str | None = None,
        referencia: datetime | None = None,
        limite: int = 100,
    ) -> list[LicitacaoAberta]:
        """Regras: UF em maiúsculas, texto sem espaços sobrando e limite entre 1 e 500."""
        uf = (uf.strip().upper() or None) if uf else None
        texto = (texto.strip() or None) if texto else None
        limite = max(1, min(limite, LIMITE_MAXIMO))
        return self.repositorio.listar_abertas(uf=uf, texto=texto, referencia=referencia, limite=limite)
