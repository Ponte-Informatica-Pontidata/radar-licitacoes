"""Especificação executável de normalizar_texto (issue #7).

Estes testes descrevem o comportamento esperado. Hoje eles "falham do jeito esperado" (XFAIL)
porque a função ainda não existe. Quando você implementar, eles passam: apague os @todo_estagiaria.
"""

from __future__ import annotations

from apoio import todo_estagiaria
from radar.tratamento.limpeza import normalizar_texto


@todo_estagiaria(issue=7)
def test_none_continua_none():
    assert normalizar_texto(None) is None


@todo_estagiaria(issue=7)
def test_remove_espacos_das_pontas():
    assert normalizar_texto("  Pregão eletrônico  ") == "Pregão eletrônico"


@todo_estagiaria(issue=7)
def test_colapsa_espacos_tabs_e_quebras_de_linha():
    assert normalizar_texto("Aquisição\n\nde  merenda\tescolar") == "Aquisição de merenda escolar"


@todo_estagiaria(issue=7)
def test_remove_caracteres_de_controle():
    assert normalizar_texto("Obra\x00 de\x1f pavimentação") == "Obra de pavimentação"


@todo_estagiaria(issue=7)
def test_mantem_acentos_cedilha_e_maiusculas():
    assert normalizar_texto("AQUISIÇÃO de Pão de Açúcar") == "AQUISIÇÃO de Pão de Açúcar"


@todo_estagiaria(issue=7)
def test_texto_vazio_vira_none():
    assert normalizar_texto("") is None
    assert normalizar_texto(" \n\t ") is None
