-- Fornecedores e contratos assinados.
--
-- LGPD: pessoa física (PF) e pessoa estrangeira (PE) NUNCA têm documento nem nome gravados.
-- A identificação vira uma chave pseudônima (HMAC com segredo fora do repositório), que permite
-- contar fornecedores distintos sem saber quem são. A constraint abaixo garante isso no próprio
-- banco: mesmo que o código tenha um bug, o Postgres recusa a linha.

create table radar.fornecedor (
    chave text primary key,
    tipo_pessoa char(2) not null,
    cnpj char(14) unique,
    razao_social text,
    possivel_mei boolean not null default false,
    constraint fornecedor_tipo_pessoa check (tipo_pessoa in ('PJ', 'PF', 'PE')),
    constraint fornecedor_lgpd_pf_sem_identificacao
        check (tipo_pessoa = 'PJ' or (cnpj is null and razao_social is null)),
    constraint fornecedor_pj_com_cnpj check (tipo_pessoa <> 'PJ' or cnpj ~ '^[0-9]{14}$')
);
comment on table radar.fornecedor is 'Fornecedor contratado. PF/PE só com chave pseudônima (LGPD)';
comment on column radar.fornecedor.possivel_mei is 'Razão social começa com CNPJ-base: típico de MEI, que contém nome de pessoa';

create table radar.contrato (
    numero_controle_pncp text primary key,
    -- Referência lógica (sem FK): a compra de origem pode estar fora do recorte carregado
    numero_controle_pncp_compra text,
    numero_controle_pncp_ata text,
    cnpj_orgao char(14) not null references radar.orgao (cnpj),
    codigo_unidade text,
    ano_contrato smallint,
    sequencial_contrato integer,
    numero_contrato_empenho text,
    processo text,
    tipo_contrato_id smallint references radar.dominio_tipo_contrato (codigo),
    categoria_processo_id smallint references radar.dominio_categoria_processo (codigo),
    receita boolean,
    objeto_contrato text,
    informacao_complementar text,
    fornecedor_chave text references radar.fornecedor (chave),
    subcontratado_chave text references radar.fornecedor (chave),
    valor_inicial numeric(18, 2),
    valor_parcela numeric(18, 2),
    numero_parcelas integer,
    valor_global numeric(18, 2),
    valor_acumulado numeric(18, 2),
    data_assinatura date,
    data_vigencia_inicio date,
    data_vigencia_fim date,
    data_publicacao_pncp timestamptz,
    data_atualizacao timestamptz,
    data_atualizacao_global timestamptz,
    numero_retificacao integer,
    usuario_nome text,
    carregado_em timestamptz not null default now(),
    foreign key (cnpj_orgao, codigo_unidade) references radar.unidade (cnpj_orgao, codigo_unidade)
);
comment on table radar.contrato is 'Contrato (ou empenho) publicado no PNCP';
comment on column radar.contrato.data_publicacao_pncp is
    'Data de publicação no PNCP. O filtro de data da API usa ESTA data, não a de assinatura';
