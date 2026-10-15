-- Carga inicial — passo 2 de 3: staging (só texto) -> radar (tipos, chaves e regras).
--
-- O que este script faz, tabela por tabela:
--   * converte texto para o tipo certo (::smallint, ::numeric, ::boolean, ::date);
--   * converte as datas do PNCP, que chegam SEM fuso (horário de Brasília), para timestamptz;
--   * respeita a ordem das chaves estrangeiras (domínios -> órgãos -> unidades -> ...);
--   * usa ON CONFLICT DO NOTHING: rodar de novo não duplica nada (idempotente).
-- Tudo acontece numa transação: ou carrega tudo, ou nada.
--
-- Como rodar:  docker compose run --rm dev psql -f banco/carga/02_transformar.sql

\set ON_ERROR_STOP on
\timing on

begin;

-- 1) Domínios -----------------------------------------------------------------
insert into radar.dominio_modalidade (codigo, nome)
select codigo::smallint, coalesce(nome, '(sem nome no PNCP)') from staging.dominio_modalidade
on conflict (codigo) do nothing;

insert into radar.dominio_modo_disputa (codigo, nome)
select codigo::smallint, coalesce(nome, '(sem nome no PNCP)') from staging.dominio_modo_disputa
on conflict (codigo) do nothing;

insert into radar.dominio_situacao_compra (codigo, nome)
select codigo::smallint, coalesce(nome, '(sem nome no PNCP)') from staging.dominio_situacao_compra
on conflict (codigo) do nothing;

insert into radar.dominio_instrumento_convocatorio (codigo, nome)
select codigo::smallint, coalesce(nome, '(sem nome no PNCP)') from staging.dominio_instrumento_convocatorio
on conflict (codigo) do nothing;

insert into radar.dominio_amparo_legal (codigo, nome, descricao)
select codigo::integer, coalesce(nome, '(sem nome no PNCP)'), descricao from staging.dominio_amparo_legal
on conflict (codigo) do nothing;

insert into radar.dominio_criterio_julgamento (codigo, nome)
select codigo::smallint, coalesce(nome, '(sem nome no PNCP)') from staging.dominio_criterio_julgamento
on conflict (codigo) do nothing;

insert into radar.dominio_situacao_item (codigo, nome)
select codigo::smallint, coalesce(nome, '(sem nome no PNCP)') from staging.dominio_situacao_item
on conflict (codigo) do nothing;

insert into radar.dominio_tipo_beneficio (codigo, nome)
select codigo::smallint, coalesce(nome, '(sem nome no PNCP)') from staging.dominio_tipo_beneficio
on conflict (codigo) do nothing;

insert into radar.dominio_categoria_item (codigo, nome)
select codigo::smallint, coalesce(nome, '(sem nome no PNCP)') from staging.dominio_categoria_item
on conflict (codigo) do nothing;

insert into radar.dominio_tipo_contrato (codigo, nome)
select codigo::smallint, coalesce(nome, '(sem nome no PNCP)') from staging.dominio_tipo_contrato
on conflict (codigo) do nothing;

insert into radar.dominio_categoria_processo (codigo, nome)
select codigo::smallint, coalesce(nome, '(sem nome no PNCP)') from staging.dominio_categoria_processo
on conflict (codigo) do nothing;

-- 2) Órgãos e unidades -----------------------------------------------------------
insert into radar.orgao (cnpj, razao_social, esfera_id, poder_id)
select cnpj, razao_social, esfera_id, poder_id
from staging.orgao
on conflict (cnpj) do nothing;

insert into radar.unidade (cnpj_orgao, codigo_unidade, nome_unidade, uf_sigla, uf_nome, municipio_nome, codigo_ibge)
select cnpj_orgao, codigo_unidade, nome_unidade, uf_sigla, uf_nome, municipio_nome, codigo_ibge
from staging.unidade
on conflict (cnpj_orgao, codigo_unidade) do nothing;

-- 3) Contratações e itens --------------------------------------------------------
insert into radar.contratacao (
    numero_controle_pncp, cnpj_orgao, codigo_unidade, ano_compra, sequencial_compra, numero_compra,
    processo, modalidade_id, modo_disputa_id, situacao_compra_id, instrumento_convocatorio_id,
    amparo_legal_codigo, srp, objeto_compra, informacao_complementar, valor_total_estimado,
    valor_total_homologado, data_publicacao_pncp, data_abertura_proposta, data_encerramento_proposta,
    data_inclusao, data_atualizacao, data_atualizacao_global, link_sistema_origem,
    link_processo_eletronico, justificativa_presencial, usuario_nome
)
select
    numero_controle_pncp,
    cnpj_orgao,
    codigo_unidade,
    ano_compra::smallint,
    sequencial_compra::integer,
    numero_compra,
    processo,
    modalidade_id::smallint,
    modo_disputa_id::smallint,
    situacao_compra_id::smallint,
    instrumento_convocatorio_id::smallint,
    amparo_legal_codigo::integer,
    srp::boolean,
    objeto_compra,
    informacao_complementar,
    valor_total_estimado::numeric,
    valor_total_homologado::numeric,
    data_publicacao_pncp::timestamp at time zone 'America/Sao_Paulo',
    data_abertura_proposta::timestamp at time zone 'America/Sao_Paulo',
    data_encerramento_proposta::timestamp at time zone 'America/Sao_Paulo',
    data_inclusao::timestamp at time zone 'America/Sao_Paulo',
    data_atualizacao::timestamp at time zone 'America/Sao_Paulo',
    data_atualizacao_global::timestamp at time zone 'America/Sao_Paulo',
    link_sistema_origem,
    link_processo_eletronico,
    justificativa_presencial,
    usuario_nome
from staging.contratacao
on conflict (numero_controle_pncp) do nothing;

insert into radar.contratacao_item (
    numero_controle_pncp, numero_item, descricao, material_ou_servico, quantidade, unidade_medida,
    valor_unitario_estimado, valor_total, orcamento_sigiloso, criterio_julgamento_id, situacao_item_id,
    tipo_beneficio_id, categoria_item_id, tem_resultado, ncm_nbs_codigo, ncm_nbs_descricao,
    catalogo_codigo_item, informacao_complementar, data_inclusao, data_atualizacao
)
select
    numero_controle_pncp,
    numero_item::integer,
    descricao,
    material_ou_servico,
    quantidade::numeric,
    unidade_medida,
    valor_unitario_estimado::numeric,
    valor_total::numeric,
    orcamento_sigiloso::boolean,
    criterio_julgamento_id::smallint,
    situacao_item_id::smallint,
    tipo_beneficio_id::smallint,
    categoria_item_id::smallint,
    tem_resultado::boolean,
    ncm_nbs_codigo,
    ncm_nbs_descricao,
    catalogo_codigo_item,
    informacao_complementar,
    data_inclusao::timestamp at time zone 'America/Sao_Paulo',
    data_atualizacao::timestamp at time zone 'America/Sao_Paulo'
from staging.contratacao_item
on conflict (numero_controle_pncp, numero_item) do nothing;

-- 4) Fornecedores e contratos ----------------------------------------------------
insert into radar.fornecedor (chave, tipo_pessoa, cnpj, razao_social, possivel_mei)
select chave, tipo_pessoa, cnpj, razao_social, coalesce(possivel_mei::boolean, false)
from staging.fornecedor
on conflict (chave) do nothing;

insert into radar.contrato (
    numero_controle_pncp, numero_controle_pncp_compra, numero_controle_pncp_ata, cnpj_orgao,
    codigo_unidade, ano_contrato, sequencial_contrato, numero_contrato_empenho, processo,
    tipo_contrato_id, categoria_processo_id, receita, objeto_contrato, informacao_complementar,
    fornecedor_chave, subcontratado_chave, valor_inicial, valor_parcela, numero_parcelas, valor_global,
    valor_acumulado, data_assinatura, data_vigencia_inicio, data_vigencia_fim, data_publicacao_pncp,
    data_atualizacao, data_atualizacao_global, numero_retificacao, usuario_nome
)
select
    numero_controle_pncp,
    numero_controle_pncp_compra,
    numero_controle_pncp_ata,
    cnpj_orgao,
    codigo_unidade,
    ano_contrato::smallint,
    sequencial_contrato::integer,
    numero_contrato_empenho,
    processo,
    tipo_contrato_id::smallint,
    categoria_processo_id::smallint,
    receita::boolean,
    objeto_contrato,
    informacao_complementar,
    fornecedor_chave,
    subcontratado_chave,
    valor_inicial::numeric,
    valor_parcela::numeric,
    numero_parcelas::integer,
    valor_global::numeric,
    valor_acumulado::numeric,
    data_assinatura::date,
    data_vigencia_inicio::date,
    data_vigencia_fim::date,
    data_publicacao_pncp::timestamp at time zone 'America/Sao_Paulo',
    data_atualizacao::timestamp at time zone 'America/Sao_Paulo',
    data_atualizacao_global::timestamp at time zone 'America/Sao_Paulo',
    numero_retificacao::integer,
    usuario_nome
from staging.contrato
on conflict (numero_controle_pncp) do nothing;

-- 5) Registro da carga (rastreabilidade) -----------------------------------------
insert into radar.execucao_ingestao (tipo, parametros, finalizado_em, status, registros_lidos, registros_gravados, mensagem)
select
    'carga_csv',
    jsonb_build_object('origem', 'dados/csv', 'script', 'banco/carga/02_transformar.sql'),
    now(),
    'sucesso',
    (select count(*) from staging.contratacao) + (select count(*) from staging.contratacao_item)
        + (select count(*) from staging.contrato),
    (select count(*) from radar.contratacao) + (select count(*) from radar.contratacao_item)
        + (select count(*) from radar.contrato),
    'Carga inicial a partir do snapshot CSV';

commit;

-- Atualiza as estatísticas do planejador de consultas depois de uma carga grande
analyze radar.contratacao;
analyze radar.contratacao_item;
analyze radar.contrato;
analyze radar.fornecedor;

select 'contratacao' as tabela, count(*) as linhas from radar.contratacao
union all select 'contratacao_item', count(*) from radar.contratacao_item
union all select 'contrato', count(*) from radar.contrato
union all select 'fornecedor', count(*) from radar.fornecedor
union all select 'orgao', count(*) from radar.orgao
union all select 'unidade', count(*) from radar.unidade
order by 1;
