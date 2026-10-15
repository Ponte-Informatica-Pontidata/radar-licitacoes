"""Contrato da persistência (padrão Repository).

Os serviços dependem DESTE contrato, e não do Postgres. Por isso dá para testar os serviços com
um repositório em memória (rápido, sem banco) e trocar a implementação sem mexer na regra de negócio.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Protocol

from radar.dominio.modelos import Contratacao, LicitacaoAberta


class RepositorioLicitacoes(Protocol):
    def listar_abertas(
        self,
        *,
        uf: str | None = None,
        texto: str | None = None,
        referencia: datetime | None = None,
        limite: int = 100,
    ) -> list[LicitacaoAberta]:
        """Contratações com proposta aberta em `referencia` (padrão: agora), da mais urgente para a menos."""
        ...

    def salvar_contratacoes(self, contratacoes: Iterable[Contratacao]) -> int:
        """Grava as contratações e devolve quantas foram inseridas ou atualizadas de fato.

        Uma contratação que já existe com a mesma data_atualizacao não conta (upsert idempotente).
        """
        ...
