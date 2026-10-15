"""Abre conexões com o Postgres (local no Docker ou Supabase em produção)."""

from __future__ import annotations

import psycopg
from psycopg.rows import dict_row

from radar.config import obter_configuracao


def conectar(url: str | None = None, *, autocommit: bool = False) -> psycopg.Connection:
    return psycopg.connect(
        url or obter_configuracao().database_url,
        row_factory=dict_row,
        autocommit=autocommit,
    )
