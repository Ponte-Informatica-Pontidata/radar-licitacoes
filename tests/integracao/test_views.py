"""Especificação executável das views do painel (issue #5).

As views são criadas por uma migration NOVA (supabase migration new ...). Enquanto não existem,
o banco responde "relation does not exist" (UndefinedTable) e o teste fica como XFAIL.
"""

from __future__ import annotations

import psycopg
import pytest

from apoio import todo_estagiaria

pytestmark = pytest.mark.integracao

COLUNAS_ABERTAS = [
    "numero_controle_pncp",
    "orgao",
    "municipio",
    "uf",
    "modalidade",
    "objeto_compra",
    "valor_total_estimado",
    "data_encerramento_proposta",
    "dias_para_encerrar",
    "link_pncp",
]
COLUNAS_RESUMO = ["uf", "modalidade", "quantidade", "valor_total_estimado", "valor_medio_estimado"]


def colunas(conexao, view: str) -> list[str]:
    cursor = conexao.execute(f"select * from radar.{view} limit 0")
    return [c.name for c in cursor.description]


@todo_estagiaria(issue=5, raises=psycopg.errors.UndefinedTable)
def test_view_licitacoes_abertas(conexao):
    assert colunas(conexao, "vw_licitacoes_abertas") == COLUNAS_ABERTAS
    na_view = conexao.execute("select count(*) from radar.vw_licitacoes_abertas").fetchone()[0]
    direto = conexao.execute(
        "select count(*) from radar.contratacao where data_encerramento_proposta >= now()"
    ).fetchone()[0]
    assert na_view == direto
    link = conexao.execute("select link_pncp from radar.vw_licitacoes_abertas limit 1").fetchone()
    if link:
        assert link[0].startswith("https://pncp.gov.br/app/editais/")


@todo_estagiaria(issue=5, raises=psycopg.errors.UndefinedTable)
def test_view_resumo_modalidade_uf(conexao):
    assert colunas(conexao, "vw_resumo_modalidade_uf") == COLUNAS_RESUMO
    soma = conexao.execute("select sum(quantidade) from radar.vw_resumo_modalidade_uf").fetchone()[0]
    total = conexao.execute("select count(*) from radar.contratacao").fetchone()[0]
    assert soma == total
