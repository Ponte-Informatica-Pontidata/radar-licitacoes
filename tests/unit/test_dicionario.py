"""O dicionário de dados (dados/DICIONARIO.md) precisa cobrir todas as colunas dos CSVs."""

from __future__ import annotations

import csv
from pathlib import Path

from apoio import todo_estagiaria

RAIZ = Path(__file__).resolve().parents[2]


def colunas_do_csv(tabela: str) -> list[str]:
    pasta = RAIZ / "dados" / "csv"
    arquivo = pasta / f"{tabela}.csv"
    if not arquivo.exists():
        arquivo = pasta / f"{tabela}_parte1.csv"
    with arquivo.open(encoding="utf-8", newline="") as f:
        return next(csv.reader(f))


def colunas_documentadas(tabela: str) -> dict[str, str]:
    """Lê a tabela markdown da seção `### `tabela`` e devolve {coluna: descrição}."""
    texto = (RAIZ / "dados" / "DICIONARIO.md").read_text(encoding="utf-8")
    secao = texto.split(f"### `{tabela}`", 1)[1].split("\n### ", 1)[0]
    documentadas = {}
    for linha in secao.splitlines():
        if linha.startswith("| `"):
            partes = [p.strip() for p in linha.strip().strip("|").split("|")]
            documentadas[partes[0].strip("`")] = partes[-1]
    return documentadas


def sem_descricao(tabela: str) -> list[str]:
    doc = colunas_documentadas(tabela)
    return [c for c in colunas_do_csv(tabela) if not doc.get(c) or "TODO" in doc[c]]


def test_tabelas_principais_estao_documentadas():
    for tabela in ("orgao", "unidade", "contratacao", "fornecedor", "contrato"):
        assert sem_descricao(tabela) == [], f"{tabela}: colunas sem descrição no DICIONARIO.md"


@todo_estagiaria(issue=3, raises=AssertionError)
def test_dicionario_de_contratacao_item_completo():
    faltando = sem_descricao("contratacao_item")
    assert faltando == [], f"Colunas de contratacao_item sem descrição no DICIONARIO.md: {faltando}"
