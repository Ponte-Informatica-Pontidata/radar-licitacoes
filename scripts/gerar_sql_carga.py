"""Gera os SQLs de carga a partir dos CSVs e do MANIFESTO (ferramenta do tech lead).

Saídas:
  supabase/migrations/20261015120700_staging.sql  tabelas de staging (texto) espelhando os CSVs
  banco/carga/01_staging.sql                       \\copy de cada CSV para o staging
  banco/carga/03_validar.sql                       confere contagens e chaves contra o MANIFESTO

Uso:  python scripts/gerar_sql_carga.py [--dados dados]

Rode de novo sempre que o snapshot mudar. Atenção: se a migration de staging já foi aplicada
em algum banco compartilhado, mudanças de colunas exigem uma NOVA migration.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

CHAVES = {
    "orgao": ["cnpj"],
    "unidade": ["cnpj_orgao", "codigo_unidade"],
    "contratacao": ["numero_controle_pncp"],
    "contratacao_item": ["numero_controle_pncp", "numero_item"],
    "fornecedor": ["chave"],
    "contrato": ["numero_controle_pncp"],
}

ORDEM = [
    "dominio_modalidade",
    "dominio_modo_disputa",
    "dominio_situacao_compra",
    "dominio_instrumento_convocatorio",
    "dominio_amparo_legal",
    "dominio_criterio_julgamento",
    "dominio_situacao_item",
    "dominio_tipo_beneficio",
    "dominio_categoria_item",
    "dominio_tipo_contrato",
    "dominio_categoria_processo",
    "orgao",
    "unidade",
    "contratacao",
    "contratacao_item",
    "fornecedor",
    "contrato",
]


def ler_cabecalho(caminho: Path) -> list[str]:
    with caminho.open(encoding="utf-8", newline="") as f:
        return next(csv.reader(f))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dados", type=Path, default=RAIZ / "dados")
    args = ap.parse_args()
    manifesto = json.loads((args.dados / "MANIFESTO.json").read_text(encoding="utf-8"))
    pasta_csv = args.dados / "csv"
    arquivos = {t: [a["arquivo"] for a in manifesto["tabelas"][t]["arquivos"]] for t in ORDEM}
    cabecalhos = {t: ler_cabecalho(pasta_csv / arquivos[t][0]) for t in ORDEM}

    # 1) migration de staging
    blocos = [
        "-- Tabelas de staging: espelham os CSVs de dados/csv, coluna a coluna, tudo como texto.",
        "-- Por que texto? Para a leitura do CSV nunca falhar por tipo. Conversões e regras",
        "-- ficam no passo 2 da carga (banco/carga/02_transformar.sql).",
        "-- Gerado por scripts/gerar_sql_carga.py.",
        "",
    ]
    for t in ORDEM:
        colunas = ",\n".join(f"    {c} text" for c in cabecalhos[t])
        blocos.append(f"create table staging.{t} (\n{colunas}\n);\n")
    (RAIZ / "supabase/migrations/20261015120700_staging.sql").write_text("\n".join(blocos), encoding="utf-8")

    # 2) carga CSV -> staging
    linhas = [
        "-- Carga inicial — passo 1 de 3: CSV -> staging.",
        "--",
        "-- \\copy roda no CLIENTE (o psql), lendo os arquivos de dados/csv. Por isso o mesmo script",
        "-- funciona no Postgres do Docker e no Supabase. HEADER MATCH faz o Postgres conferir se o",
        "-- cabeçalho de cada CSV bate com as colunas da tabela de staging.",
        "--",
        "-- Como rodar:  docker compose run --rm dev psql -f banco/carga/01_staging.sql",
        "-- Gerado por scripts/gerar_sql_carga.py.",
        "",
        "\\set ON_ERROR_STOP on",
        "\\timing on",
        "",
        "begin;",
        "",
        "truncate table " + ", ".join(f"staging.{t}" for t in ORDEM) + ";",
        "",
    ]
    for t in ORDEM:
        for arquivo in arquivos[t]:
            linhas.append(
                f"\\copy staging.{t} from 'dados/csv/{arquivo}' with (format csv, header match, encoding 'UTF8')"
            )
    linhas += ["", "commit;", ""]
    partes = [f"select '{t}' as tabela, count(*) as linhas from staging.{t}" for t in ORDEM]
    linhas.append("\nunion all ".join(partes) + ";")
    (RAIZ / "banco/carga/01_staging.sql").write_text("\n".join(linhas) + "\n", encoding="utf-8")

    # 3) validação contra o MANIFESTO
    valores = []
    for t in ORDEM:
        esperado = manifesto["tabelas"][t]["linhas"]
        chave = CHAVES.get(t, ["codigo"])
        valores.append(f"    ('{t}', '{','.join(chave)}', {esperado})")
    validar = f"""-- Carga inicial — passo 3 de 3: confere se TUDO que está nos CSVs chegou ao banco.
--
-- Para cada tabela:
--   1. o staging tem exatamente as linhas que o MANIFESTO diz que o CSV tem;
--   2. nenhuma chave do staging ficou de fora da tabela final (anti-join com NOT EXISTS).
-- No fim, confere a regra de LGPD dos fornecedores. Qualquer problema = erro (exit code 3).
--
-- Snapshot validado: {manifesto["gerado_em"]} (UF {manifesto["parametros"]["uf"]})
-- Como rodar:  docker compose run --rm dev psql -f banco/carga/03_validar.sql
-- Gerado por scripts/gerar_sql_carga.py.

\\set ON_ERROR_STOP on

create temp table validacao_esperado (
    tabela text primary key,
    chave text not null,
    linhas_csv bigint not null
);

insert into validacao_esperado (tabela, chave, linhas_csv) values
{("," + chr(10)).join(valores)};

do $$
declare
    t record;
    n_staging bigint;
    n_radar bigint;
    n_faltando bigint;
    expr_r text;
    expr_s text;
    erros text := '';
begin
    for t in select * from validacao_esperado order by tabela loop
        select string_agg(format('r.%I::text', c), ', '), string_agg(format('s.%I', c), ', ')
          into expr_r, expr_s
          from unnest(string_to_array(t.chave, ',')) as c;
        execute format('select count(*) from staging.%I', t.tabela) into n_staging;
        execute format('select count(*) from radar.%I', t.tabela) into n_radar;
        execute format(
            'select count(*) from staging.%1$I s where not exists '
            '(select 1 from radar.%1$I r where (%2$s) = (%3$s))',
            t.tabela, expr_r, expr_s
        ) into n_faltando;
        raise notice '%', format('%-34s csv=%-7s staging=%-7s radar=%-7s faltando=%s',
                                 t.tabela, t.linhas_csv, n_staging, n_radar, n_faltando);
        if n_staging <> t.linhas_csv then
            erros := erros || format(E'\\n - %s: staging tem %s linhas, o CSV tem %s', t.tabela, n_staging, t.linhas_csv);
        end if;
        if n_faltando > 0 then
            erros := erros || format(E'\\n - %s: %s linhas do staging não chegaram ao radar', t.tabela, n_faltando);
        end if;
    end loop;

    if exists (
        select 1 from radar.fornecedor
        where tipo_pessoa <> 'PJ' and (cnpj is not null or razao_social is not null)
    ) then
        erros := erros || E'\\n - LGPD: fornecedor PF/PE com documento ou nome';
    end if;

    if erros <> '' then
        raise exception 'Validação da carga FALHOU:%', erros;
    end if;
    raise notice 'Validação da carga OK: todas as tabelas conferem com o MANIFESTO.';
end
$$;
"""
    (RAIZ / "banco/carga/03_validar.sql").write_text(validar, encoding="utf-8")
    print("SQL gerado: staging, 01_staging.sql e 03_validar.sql")


if __name__ == "__main__":
    main()
