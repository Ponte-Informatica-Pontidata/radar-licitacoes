"""Página inicial do Radar: licitações com proposta aberta.

Rodando no Docker: http://localhost:8501  (docker compose up -d)
Fluxo: Streamlit -> ServicoLicitacoes (regras) -> RepositorioPostgres (SQL) -> Postgres
"""

from __future__ import annotations

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pandas as pd
import psycopg
import streamlit as st

from radar.config import obter_configuracao
from radar.persistencia.conexao import conectar
from radar.persistencia.postgres import RepositorioPostgres
from radar.servicos.licitacoes import ServicoLicitacoes

FUSO = ZoneInfo("America/Sao_Paulo")
DATA_SNAPSHOT = date(2026, 10, 15)

st.set_page_config(page_title="Radar de Licitações", page_icon="📡", layout="wide")
cfg = obter_configuracao()


@st.cache_data(ttl=300, show_spinner="Consultando o banco…")
def carregar(uf: str, texto: str, referencia: datetime, limite: int) -> pd.DataFrame:
    with conectar(cfg.database_url) as conexao:
        servico = ServicoLicitacoes(RepositorioPostgres(conexao))
        linhas = servico.abertas(uf=uf, texto=texto, referencia=referencia, limite=limite)
    return pd.DataFrame(
        {
            "Encerra em": [r.data_encerramento_proposta for r in linhas],
            "Órgão": [r.orgao for r in linhas],
            "Município": [r.municipio for r in linhas],
            "Modalidade": [r.modalidade for r in linhas],
            "Objeto": [r.objeto for r in linhas],
            "Valor estimado (R$)": [float(r.valor_total_estimado or 0) for r in linhas],
            "Edital": [r.link_pncp for r in linhas],
        }
    )


st.title("📡 Radar de Licitações")
st.caption("Licitações com proposta aberta, a partir da API pública do PNCP · Laboratório Pontidata")

with st.sidebar:
    st.header("Filtros")
    uf = st.text_input("UF", value=cfg.radar_uf, max_chars=2)
    texto = st.text_input("Buscar no objeto", placeholder="ex.: merenda, asfalto, notebook")
    dia = st.date_input("Abertas em", value=date.today(), format="DD/MM/YYYY")
    limite = st.slider("Máximo de linhas", min_value=10, max_value=500, value=100, step=10)
    st.caption(
        f"A base inicial (CSV) é de {DATA_SNAPSHOT:%d/%m/%Y}. Para ver as licitações de hoje, "
        "rode `docker compose run --rm dev radar coletar`."
    )

# Hoje = a partir de agora (o que já encerrou hoje cedo não aparece); outro dia = desde o início dele
referencia = datetime.now(FUSO) if dia == date.today() else datetime.combine(dia, time.min, tzinfo=FUSO)
try:
    tabela = carregar(uf, texto, referencia, limite)
except psycopg.OperationalError:
    st.error("Não consegui conectar no banco. Ele está rodando? `docker compose up -d`")
    st.stop()
except psycopg.errors.UndefinedTable:
    st.info(
        "O banco está vazio: as tabelas ainda não existem. Siga a issue de criação do banco "
        "(migrations + carga dos CSVs) e volte aqui."
    )
    st.stop()

if tabela.empty:
    st.warning("Nenhuma licitação aberta com esses filtros nessa data.")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Licitações exibidas", f"{len(tabela):,}".replace(",", "."))
col2.metric("Valor estimado somado", f"R$ {tabela['Valor estimado (R$)'].sum():,.0f}".replace(",", "."))
col3.metric("Próximo encerramento", f"{tabela['Encerra em'].min():%d/%m %H:%M}")

st.dataframe(
    tabela,
    hide_index=True,
    use_container_width=True,
    column_config={
        "Encerra em": st.column_config.DatetimeColumn(format="DD/MM/YYYY HH:mm"),
        "Valor estimado (R$)": st.column_config.NumberColumn(format="%.2f"),
        "Edital": st.column_config.LinkColumn(display_text="abrir no PNCP"),
        "Objeto": st.column_config.TextColumn(width="large"),
    },
)
