from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures"
_TAREFAS = pytest.StashKey[dict]()


@pytest.fixture
def contratacoes_api() -> list[dict]:
    """Três contratações reais devolvidas pela API do PNCP (MG, 15/10/2026)."""
    dados = json.loads((FIXTURES / "pncp" / "contratacoes_proposta_mg.json").read_text(encoding="utf-8"))
    return dados["data"]


@pytest.fixture
def conexao():
    """Conexão com o banco de verdade (testes de integração). Pula se não houver DATABASE_URL."""
    psycopg = pytest.importorskip("psycopg")
    url = os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL não definida: rode dentro do Docker (docker compose run --rm dev pytest)")
    try:
        conn = psycopg.connect(url, autocommit=True)
    except psycopg.OperationalError as exc:
        pytest.skip(f"banco indisponível: {exc}")
    yield conn
    conn.close()


def pytest_collection_modifyitems(config, items):
    tarefas = {}
    for item in items:
        marca = item.get_closest_marker("estagiaria")
        if marca is not None:
            tarefas[item.nodeid] = marca.kwargs.get("issue")
    config.stash[_TAREFAS] = tarefas


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    tarefas = config.stash.get(_TAREFAS, {})
    pendentes = defaultdict(list)
    for relatorio in terminalreporter.stats.get("xfailed", []):
        if relatorio.nodeid in tarefas:
            pendentes[tarefas[relatorio.nodeid]].append(relatorio.nodeid.split("::")[-1])
    if pendentes:
        terminalreporter.section("Tarefas pendentes da estagiária (TODO(estagiaria))")
        for issue, testes in sorted(pendentes.items(), key=lambda kv: str(kv[0])):
            terminalreporter.write_line(f"  #{issue}: {len(testes)} teste(s) esperando: {', '.join(testes)}")
