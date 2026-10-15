-- Contratações (licitações, dispensas etc.) e seus itens.
-- Datas do PNCP chegam sem fuso (horário de Brasília); aqui ficam como timestamptz.

create table radar.contratacao (
    numero_controle_pncp text primary key,
    cnpj_orgao char(14) not null,
    codigo_unidade text not null,
    ano_compra smallint not null,
    sequencial_compra integer not null,
    numero_compra text,
    processo text,
    modalidade_id smallint not null references radar.dominio_modalidade (codigo),
    modo_disputa_id smallint references radar.dominio_modo_disputa (codigo),
    situacao_compra_id smallint references radar.dominio_situacao_compra (codigo),
    instrumento_convocatorio_id smallint references radar.dominio_instrumento_convocatorio (codigo),
    amparo_legal_codigo integer references radar.dominio_amparo_legal (codigo),
    srp boolean,
    objeto_compra text not null,
    informacao_complementar text,
    valor_total_estimado numeric(18, 2),
    valor_total_homologado numeric(18, 2),
    data_publicacao_pncp timestamptz,
    data_abertura_proposta timestamptz,
    data_encerramento_proposta timestamptz,
    data_inclusao timestamptz,
    data_atualizacao timestamptz,
    data_atualizacao_global timestamptz,
    link_sistema_origem text,
    link_processo_eletronico text,
    justificativa_presencial text,
    usuario_nome text,
    carregado_em timestamptz not null default now(),
    foreign key (cnpj_orgao, codigo_unidade) references radar.unidade (cnpj_orgao, codigo_unidade),
    constraint contratacao_identificador_natural unique (cnpj_orgao, ano_compra, sequencial_compra)
);
comment on table radar.contratacao is 'Contratação publicada no PNCP (edital, aviso de dispensa etc.)';
comment on column radar.contratacao.numero_controle_pncp is 'Identificador do PNCP: CNPJ-1-SEQUENCIAL/ANO';
comment on column radar.contratacao.srp is 'Sistema de Registro de Preços (gera ata em vez de contrato direto)';
comment on column radar.contratacao.data_encerramento_proposta is 'Fim do prazo de propostas: é o que define "aberta" no Radar';

create table radar.contratacao_item (
    numero_controle_pncp text not null references radar.contratacao (numero_controle_pncp) on delete cascade,
    numero_item integer not null,
    descricao text,
    material_ou_servico char(1),
    quantidade numeric(20, 6),
    unidade_medida text,
    valor_unitario_estimado numeric(20, 6),
    valor_total numeric(18, 2),
    orcamento_sigiloso boolean,
    criterio_julgamento_id smallint references radar.dominio_criterio_julgamento (codigo),
    situacao_item_id smallint references radar.dominio_situacao_item (codigo),
    tipo_beneficio_id smallint references radar.dominio_tipo_beneficio (codigo),
    categoria_item_id smallint references radar.dominio_categoria_item (codigo),
    tem_resultado boolean,
    ncm_nbs_codigo text,
    ncm_nbs_descricao text,
    catalogo_codigo_item text,
    informacao_complementar text,
    data_inclusao timestamptz,
    data_atualizacao timestamptz,
    primary key (numero_controle_pncp, numero_item),
    constraint item_material_ou_servico check (material_ou_servico in ('M', 'S'))
);
comment on table radar.contratacao_item is 'Itens de uma contratação (o que está sendo comprado)';
comment on column radar.contratacao_item.material_ou_servico is 'M = material, S = serviço';
