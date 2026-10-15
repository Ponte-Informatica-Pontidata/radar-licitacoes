"""Especificação executável de perfil_qualidade (issue #6)."""

from __future__ import annotations

import pandas as pd

from apoio import todo_estagiaria
from radar.tratamento.qualidade import COLUNAS_PERFIL, perfil_qualidade


def base_pequena() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "modalidade": ["Pregão", "Pregão", None, "Dispensa"],
            "objeto": ["Merenda", "  ", "Asfalto", "Merenda"],
        }
    )


@todo_estagiaria(issue=6)
def test_colunas_e_ordem_do_resultado():
    perfil = perfil_qualidade(base_pequena())
    assert list(perfil.columns) == COLUNAS_PERFIL
    assert list(perfil["coluna"]) == ["id", "modalidade", "objeto"]
    assert (perfil["linhas"] == 4).all()


@todo_estagiaria(issue=6)
def test_metricas_por_coluna():
    p = perfil_qualidade(base_pequena()).set_index("coluna")
    assert p.loc["id", "tipo"] == "int64"
    assert p.loc["id", "nulos"] == 0
    assert p.loc["id", "pct_distintos"] == 100.0
    assert p.loc["modalidade", "nulos"] == 1
    assert p.loc["modalidade", "pct_nulos"] == 25.0
    assert p.loc["modalidade", "distintos"] == 2
    assert p.loc["modalidade", "pct_distintos"] == 66.67
    assert p.loc["modalidade", "exemplo"] == "Pregão"


@todo_estagiaria(issue=6)
def test_texto_so_com_espacos_conta_como_nulo():
    p = perfil_qualidade(base_pequena()).set_index("coluna")
    assert p.loc["objeto", "nulos"] == 1
    assert p.loc["objeto", "distintos"] == 2
    assert p.loc["objeto", "exemplo"] == "Merenda"


@todo_estagiaria(issue=6)
def test_dataframe_vazio_nao_quebra():
    perfil = perfil_qualidade(pd.DataFrame({"a": pd.Series([], dtype="object")}))
    assert perfil.loc[0, "linhas"] == 0
    assert perfil.loc[0, "pct_nulos"] == 0.0
    assert perfil.loc[0, "pct_distintos"] == 0.0
    assert perfil.loc[0, "exemplo"] is None
