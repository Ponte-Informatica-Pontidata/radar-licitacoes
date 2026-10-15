-- Carga inicial — passo 3 de 3: confere se TUDO que está nos CSVs chegou ao banco.
--
-- Para cada tabela:
--   1. o staging tem exatamente as linhas que o MANIFESTO diz que o CSV tem;
--   2. nenhuma chave do staging ficou de fora da tabela final (anti-join com NOT EXISTS).
-- No fim, confere a regra de LGPD dos fornecedores. Qualquer problema = erro (exit code 3).
--
-- Snapshot validado: 2026-10-15T10:23:38-03:00 (UF MG)
-- Como rodar:  docker compose run --rm dev psql -f banco/carga/03_validar.sql
-- Gerado por scripts/gerar_sql_carga.py.

\set ON_ERROR_STOP on

create temp table validacao_esperado (
    tabela text primary key,
    chave text not null,
    linhas_csv bigint not null
);

insert into validacao_esperado (tabela, chave, linhas_csv) values
    ('dominio_modalidade', 'codigo', 11),
    ('dominio_modo_disputa', 'codigo', 6),
    ('dominio_situacao_compra', 'codigo', 4),
    ('dominio_instrumento_convocatorio', 'codigo', 3),
    ('dominio_amparo_legal', 'codigo', 25),
    ('dominio_criterio_julgamento', 'codigo', 8),
    ('dominio_situacao_item', 'codigo', 5),
    ('dominio_tipo_beneficio', 'codigo', 5),
    ('dominio_categoria_item', 'codigo', 3),
    ('dominio_tipo_contrato', 'codigo', 8),
    ('dominio_categoria_processo', 'codigo', 11),
    ('orgao', 'cnpj', 1306),
    ('unidade', 'cnpj_orgao,codigo_unidade', 2366),
    ('contratacao', 'numero_controle_pncp', 5304),
    ('contratacao_item', 'numero_controle_pncp,numero_item', 145669),
    ('fornecedor', 'chave', 7332),
    ('contrato', 'numero_controle_pncp', 13151);

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
            erros := erros || format(E'\n - %s: staging tem %s linhas, o CSV tem %s', t.tabela, n_staging, t.linhas_csv);
        end if;
        if n_faltando > 0 then
            erros := erros || format(E'\n - %s: %s linhas do staging não chegaram ao radar', t.tabela, n_faltando);
        end if;
    end loop;

    if exists (
        select 1 from radar.fornecedor
        where tipo_pessoa <> 'PJ' and (cnpj is not null or razao_social is not null)
    ) then
        erros := erros || E'\n - LGPD: fornecedor PF/PE com documento ou nome';
    end if;

    if erros <> '' then
        raise exception 'Validação da carga FALHOU:%', erros;
    end if;
    raise notice 'Validação da carga OK: todas as tabelas conferem com o MANIFESTO.';
end
$$;
