-- Carga inicial — passo 1 de 3: CSV -> staging.
--
-- \copy roda no CLIENTE (o psql), lendo os arquivos de dados/csv. Por isso o mesmo script
-- funciona no Postgres do Docker e no Supabase. HEADER MATCH faz o Postgres conferir se o
-- cabeçalho de cada CSV bate com as colunas da tabela de staging.
--
-- Como rodar:  docker compose run --rm dev psql -f banco/carga/01_staging.sql
-- Gerado por scripts/gerar_sql_carga.py.

\set ON_ERROR_STOP on
\timing on

begin;

truncate table staging.dominio_modalidade, staging.dominio_modo_disputa, staging.dominio_situacao_compra, staging.dominio_instrumento_convocatorio, staging.dominio_amparo_legal, staging.dominio_criterio_julgamento, staging.dominio_situacao_item, staging.dominio_tipo_beneficio, staging.dominio_categoria_item, staging.dominio_tipo_contrato, staging.dominio_categoria_processo, staging.orgao, staging.unidade, staging.contratacao, staging.contratacao_item, staging.fornecedor, staging.contrato;

\copy staging.dominio_modalidade from 'dados/csv/dominio_modalidade.csv' with (format csv, header match, encoding 'UTF8')
\copy staging.dominio_modo_disputa from 'dados/csv/dominio_modo_disputa.csv' with (format csv, header match, encoding 'UTF8')
\copy staging.dominio_situacao_compra from 'dados/csv/dominio_situacao_compra.csv' with (format csv, header match, encoding 'UTF8')
\copy staging.dominio_instrumento_convocatorio from 'dados/csv/dominio_instrumento_convocatorio.csv' with (format csv, header match, encoding 'UTF8')
\copy staging.dominio_amparo_legal from 'dados/csv/dominio_amparo_legal.csv' with (format csv, header match, encoding 'UTF8')
\copy staging.dominio_criterio_julgamento from 'dados/csv/dominio_criterio_julgamento.csv' with (format csv, header match, encoding 'UTF8')
\copy staging.dominio_situacao_item from 'dados/csv/dominio_situacao_item.csv' with (format csv, header match, encoding 'UTF8')
\copy staging.dominio_tipo_beneficio from 'dados/csv/dominio_tipo_beneficio.csv' with (format csv, header match, encoding 'UTF8')
\copy staging.dominio_categoria_item from 'dados/csv/dominio_categoria_item.csv' with (format csv, header match, encoding 'UTF8')
\copy staging.dominio_tipo_contrato from 'dados/csv/dominio_tipo_contrato.csv' with (format csv, header match, encoding 'UTF8')
\copy staging.dominio_categoria_processo from 'dados/csv/dominio_categoria_processo.csv' with (format csv, header match, encoding 'UTF8')
\copy staging.orgao from 'dados/csv/orgao.csv' with (format csv, header match, encoding 'UTF8')
\copy staging.unidade from 'dados/csv/unidade.csv' with (format csv, header match, encoding 'UTF8')
\copy staging.contratacao from 'dados/csv/contratacao.csv' with (format csv, header match, encoding 'UTF8')
\copy staging.contratacao_item from 'dados/csv/contratacao_item.csv' with (format csv, header match, encoding 'UTF8')
\copy staging.fornecedor from 'dados/csv/fornecedor.csv' with (format csv, header match, encoding 'UTF8')
\copy staging.contrato from 'dados/csv/contrato.csv' with (format csv, header match, encoding 'UTF8')

commit;

select 'dominio_modalidade' as tabela, count(*) as linhas from staging.dominio_modalidade
union all select 'dominio_modo_disputa' as tabela, count(*) as linhas from staging.dominio_modo_disputa
union all select 'dominio_situacao_compra' as tabela, count(*) as linhas from staging.dominio_situacao_compra
union all select 'dominio_instrumento_convocatorio' as tabela, count(*) as linhas from staging.dominio_instrumento_convocatorio
union all select 'dominio_amparo_legal' as tabela, count(*) as linhas from staging.dominio_amparo_legal
union all select 'dominio_criterio_julgamento' as tabela, count(*) as linhas from staging.dominio_criterio_julgamento
union all select 'dominio_situacao_item' as tabela, count(*) as linhas from staging.dominio_situacao_item
union all select 'dominio_tipo_beneficio' as tabela, count(*) as linhas from staging.dominio_tipo_beneficio
union all select 'dominio_categoria_item' as tabela, count(*) as linhas from staging.dominio_categoria_item
union all select 'dominio_tipo_contrato' as tabela, count(*) as linhas from staging.dominio_tipo_contrato
union all select 'dominio_categoria_processo' as tabela, count(*) as linhas from staging.dominio_categoria_processo
union all select 'orgao' as tabela, count(*) as linhas from staging.orgao
union all select 'unidade' as tabela, count(*) as linhas from staging.unidade
union all select 'contratacao' as tabela, count(*) as linhas from staging.contratacao
union all select 'contratacao_item' as tabela, count(*) as linhas from staging.contratacao_item
union all select 'fornecedor' as tabela, count(*) as linhas from staging.fornecedor
union all select 'contrato' as tabela, count(*) as linhas from staging.contrato;
