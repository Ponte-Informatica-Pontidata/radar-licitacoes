"""Testes de integração: rodam contra o banco com migrations + carga aplicadas.

No Docker:  docker compose run --rm dev pytest -m integracao
"""

from __future__ import annotations

import os
from datetime import datetime
from zoneinfo import ZoneInfo

import psycopg
import pytest
from psycopg.rows import dict_row

from radar.coleta.adaptador_pncp import AdaptadorPncp
from radar.persistencia.postgres import RepositorioPostgres

pytestmark = pytest.mark.integracao

FUSO = ZoneInfo("America/Sao_Paulo")


def um_valor(conexao, sql: str):
    return conexao.execute(sql).fetchone()[0]


def test_carga_inicial_tem_dados(conexao):
    for tabela in ("orgao", "unidade", "contratacao", "contratacao_item", "fornecedor", "contrato"):
        assert um_valor(conexao, f"select count(*) from radar.{tabela}") > 0, tabela


def test_banco_recusa_pessoa_fisica_identificada(conexao):
    with pytest.raises(psycopg.errors.CheckViolation):
        conexao.execute(
            "insert into radar.fornecedor (chave, tipo_pessoa, razao_social) values ('PF-teste', 'PF', 'Fulano')"
        )


def test_nenhum_fornecedor_pf_ou_pe_identificado(conexao):
    sql = """select count(*) from radar.fornecedor
              where tipo_pessoa <> 'PJ' and (cnpj is not null or razao_social is not null)"""
    assert um_valor(conexao, sql) == 0


def test_datas_do_csv_viram_horario_de_brasilia(conexao):
    linha = conexao.execute(
        """select (c.data_encerramento_proposta at time zone 'America/Sao_Paulo')::text, s.data_encerramento_proposta
             from radar.contratacao c
             join staging.contratacao s using (numero_controle_pncp)
            where s.data_encerramento_proposta is not null
            limit 1"""
    ).fetchone()
    assert linha[0][:19] == linha[1].replace("T", " ")[:19]


@pytest.fixture
def conexao_transacional():
    """Conexão cujas alterações são SEMPRE desfeitas no fim do teste.

    Cuidado: `conn.transaction()` faz COMMIT se não houver transação aberta. Abrindo uma transação
    externa com force_rollback, as transações internas viram savepoints e nada é gravado de verdade.
    """
    with (
        psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row) as conn,
        conn.transaction(force_rollback=True),
    ):
        yield conn


def test_repositorio_lista_abertas_na_data_do_snapshot(conexao, conexao_transacional):
    referencia = datetime(2026, 10, 15, tzinfo=FUSO)
    abertas = RepositorioPostgres(conexao_transacional).listar_abertas(referencia=referencia, limite=50)
    assert abertas
    encerramentos = [a.data_encerramento_proposta for a in abertas]
    assert encerramentos == sorted(encerramentos)
    assert all(e >= referencia for e in encerramentos)
    assert all(a.link_pncp.startswith("https://pncp.gov.br/app/editais/") for a in abertas)


def test_repositorio_salva_contratacao_nova(conexao, conexao_transacional, contratacoes_api):
    bruto = dict(
        contratacoes_api[0], numeroControlePNCP="00000000000000-1-999999/2099", sequencialCompra=999999
    )
    bruto["anoCompra"] = 2099
    repositorio = RepositorioPostgres(conexao_transacional)
    assert repositorio.salvar_contratacoes([AdaptadorPncp().contratacao(bruto)]) == 1
    total = conexao_transacional.execute(
        "select count(*) as n from radar.contratacao where numero_controle_pncp = %s",
        [bruto["numeroControlePNCP"]],
    ).fetchone()["n"]
    assert total == 1
