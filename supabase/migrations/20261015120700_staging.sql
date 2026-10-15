-- Tabelas de staging: espelham os CSVs de dados/csv, coluna a coluna, tudo como texto.
-- Por que texto? Para a leitura do CSV nunca falhar por tipo. Conversões e regras
-- ficam no passo 2 da carga (banco/carga/02_transformar.sql).
-- Gerado por scripts/gerar_sql_carga.py.

create table staging.dominio_modalidade (
    codigo text,
    nome text
);

create table staging.dominio_modo_disputa (
    codigo text,
    nome text
);

create table staging.dominio_situacao_compra (
    codigo text,
    nome text
);

create table staging.dominio_instrumento_convocatorio (
    codigo text,
    nome text
);

create table staging.dominio_amparo_legal (
    codigo text,
    nome text,
    descricao text
);

create table staging.dominio_criterio_julgamento (
    codigo text,
    nome text
);

create table staging.dominio_situacao_item (
    codigo text,
    nome text
);

create table staging.dominio_tipo_beneficio (
    codigo text,
    nome text
);

create table staging.dominio_categoria_item (
    codigo text,
    nome text
);

create table staging.dominio_tipo_contrato (
    codigo text,
    nome text
);

create table staging.dominio_categoria_processo (
    codigo text,
    nome text
);

create table staging.orgao (
    cnpj text,
    razao_social text,
    esfera_id text,
    poder_id text
);

create table staging.unidade (
    cnpj_orgao text,
    codigo_unidade text,
    nome_unidade text,
    uf_sigla text,
    uf_nome text,
    municipio_nome text,
    codigo_ibge text
);

create table staging.contratacao (
    numero_controle_pncp text,
    cnpj_orgao text,
    codigo_unidade text,
    ano_compra text,
    sequencial_compra text,
    numero_compra text,
    processo text,
    modalidade_id text,
    modo_disputa_id text,
    situacao_compra_id text,
    instrumento_convocatorio_id text,
    amparo_legal_codigo text,
    srp text,
    objeto_compra text,
    informacao_complementar text,
    valor_total_estimado text,
    valor_total_homologado text,
    data_publicacao_pncp text,
    data_abertura_proposta text,
    data_encerramento_proposta text,
    data_inclusao text,
    data_atualizacao text,
    data_atualizacao_global text,
    link_sistema_origem text,
    link_processo_eletronico text,
    justificativa_presencial text,
    usuario_nome text
);

create table staging.contratacao_item (
    numero_controle_pncp text,
    numero_item text,
    descricao text,
    material_ou_servico text,
    quantidade text,
    unidade_medida text,
    valor_unitario_estimado text,
    valor_total text,
    orcamento_sigiloso text,
    criterio_julgamento_id text,
    situacao_item_id text,
    tipo_beneficio_id text,
    categoria_item_id text,
    tem_resultado text,
    ncm_nbs_codigo text,
    ncm_nbs_descricao text,
    catalogo_codigo_item text,
    informacao_complementar text,
    data_inclusao text,
    data_atualizacao text
);

create table staging.fornecedor (
    chave text,
    tipo_pessoa text,
    cnpj text,
    razao_social text,
    possivel_mei text
);

create table staging.contrato (
    numero_controle_pncp text,
    numero_controle_pncp_compra text,
    numero_controle_pncp_ata text,
    cnpj_orgao text,
    codigo_unidade text,
    ano_contrato text,
    sequencial_contrato text,
    numero_contrato_empenho text,
    processo text,
    tipo_contrato_id text,
    categoria_processo_id text,
    receita text,
    objeto_contrato text,
    informacao_complementar text,
    fornecedor_chave text,
    subcontratado_chave text,
    valor_inicial text,
    valor_parcela text,
    numero_parcelas text,
    valor_global text,
    valor_acumulado text,
    data_assinatura text,
    data_vigencia_inicio text,
    data_vigencia_fim text,
    data_publicacao_pncp text,
    data_atualizacao text,
    data_atualizacao_global text,
    numero_retificacao text,
    usuario_nome text
);
