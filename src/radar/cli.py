"""Linha de comando do Radar.

No Docker:  docker compose run --rm dev radar --help
"""

from __future__ import annotations

import typer

from radar.coleta.adaptador_pncp import AdaptadorPncp
from radar.coleta.cliente_pncp import ClientePncp
from radar.config import obter_configuracao
from radar.persistencia.conexao import conectar
from radar.persistencia.postgres import RepositorioPostgres
from radar.servicos.ingestao import ServicoIngestao

app = typer.Typer(help="Radar de Licitações — linha de comando", no_args_is_help=True)


@app.command()
def coletar(
    uf: str | None = typer.Option(None, help="UF a coletar (padrão: variável RADAR_UF)"),
    paginas: int = typer.Option(2, help="Máximo de páginas de 50 contratações"),
    dias: int = typer.Option(
        365, help="Teto da data de encerramento das propostas, em dias a partir de hoje"
    ),
) -> None:
    """Busca contratações com proposta aberta no PNCP e grava no banco (versão simples)."""
    cfg = obter_configuracao()
    with conectar(cfg.database_url) as conexao:
        servico = ServicoIngestao(
            ClientePncp(intervalo=cfg.radar_pncp_intervalo), AdaptadorPncp(), RepositorioPostgres(conexao)
        )
        resultado = servico.coletar_propostas_abertas(uf or cfg.radar_uf, dias=dias, max_paginas=paginas)
    typer.echo(
        f"Lidas {resultado.lidos} contratações na API; {resultado.gravados} novas ou atualizadas no banco."
    )


@app.command()
def status() -> None:
    """Mostra quantas linhas existem em cada tabela do schema radar."""
    with conectar() as conexao:
        tabelas = conexao.execute(
            """select table_name from information_schema.tables
                where table_schema = 'radar' and table_type = 'BASE TABLE' order by 1"""
        ).fetchall()
        for linha in tabelas:
            nome = linha["table_name"]
            total = conexao.execute(f'select count(*) as n from radar."{nome}"').fetchone()["n"]
            typer.echo(f"{nome:<36} {total:>10}")


if __name__ == "__main__":
    app()
