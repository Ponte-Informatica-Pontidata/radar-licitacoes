-- Órgãos (CNPJ do ente público) e suas unidades compradoras.

create table radar.orgao (
    cnpj char(14) primary key,
    razao_social text not null,
    esfera_id char(1),
    poder_id char(1),
    constraint orgao_cnpj_14_digitos check (cnpj ~ '^[0-9]{14}$')
);
comment on table radar.orgao is 'Órgão ou entidade pública (orgaoEntidade no PNCP)';
comment on column radar.orgao.esfera_id is 'F = federal, E = estadual, M = municipal, D = distrital';
comment on column radar.orgao.poder_id is 'E = executivo, L = legislativo, J = judiciário, N = não se aplica';

create table radar.unidade (
    cnpj_orgao char(14) not null references radar.orgao (cnpj),
    codigo_unidade text not null,
    nome_unidade text,
    uf_sigla char(2),
    uf_nome text,
    municipio_nome text,
    codigo_ibge text,
    primary key (cnpj_orgao, codigo_unidade)
);
comment on table radar.unidade is 'Unidade compradora de um órgão (unidadeOrgao no PNCP)';
comment on column radar.unidade.codigo_ibge is 'Código IBGE do município (7 dígitos)';
