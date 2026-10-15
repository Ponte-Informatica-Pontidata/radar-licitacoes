-- Tabelas de domínio (códigos do PNCP e seus nomes).
-- Uma tabela por domínio permite chave estrangeira de verdade nas tabelas principais:
-- o banco recusa um código de modalidade que não existe.

create table radar.dominio_modalidade (
    codigo smallint primary key,
    nome text not null
);
comment on table radar.dominio_modalidade is 'Modalidade da contratação (ex.: 6 = Pregão - Eletrônico)';

create table radar.dominio_modo_disputa (
    codigo smallint primary key,
    nome text not null
);

create table radar.dominio_situacao_compra (
    codigo smallint primary key,
    nome text not null
);

create table radar.dominio_instrumento_convocatorio (
    codigo smallint primary key,
    nome text not null
);

create table radar.dominio_amparo_legal (
    codigo integer primary key,
    nome text not null,
    descricao text
);
comment on table radar.dominio_amparo_legal is 'Base legal da contratação (artigo/inciso da Lei 14.133/2021 etc.)';

create table radar.dominio_criterio_julgamento (
    codigo smallint primary key,
    nome text not null
);

create table radar.dominio_situacao_item (
    codigo smallint primary key,
    nome text not null
);

create table radar.dominio_tipo_beneficio (
    codigo smallint primary key,
    nome text not null
);
comment on table radar.dominio_tipo_beneficio is 'Benefício para ME/EPP previsto no item (Lei Complementar 123/2006)';

create table radar.dominio_categoria_item (
    codigo smallint primary key,
    nome text not null
);

create table radar.dominio_tipo_contrato (
    codigo smallint primary key,
    nome text not null
);

create table radar.dominio_categoria_processo (
    codigo smallint primary key,
    nome text not null
);
