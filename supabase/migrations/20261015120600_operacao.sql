-- Registro de cada execução de ingestão: base para medir qualidade e diagnosticar a API.

create table radar.execucao_ingestao (
    id bigint generated always as identity primary key,
    tipo text not null,
    parametros jsonb not null default '{}'::jsonb,
    iniciado_em timestamptz not null default now(),
    finalizado_em timestamptz,
    status text not null default 'em_andamento',
    registros_lidos integer not null default 0,
    registros_gravados integer not null default 0,
    registros_rejeitados integer not null default 0,
    divergencias_filtro integer not null default 0,
    mensagem text,
    constraint execucao_status check (status in ('em_andamento', 'sucesso', 'parcial', 'falha'))
);
comment on table radar.execucao_ingestao is 'Uma linha por execução do pipeline (coleta da API ou carga CSV)';
comment on column radar.execucao_ingestao.divergencias_filtro is
    'Registros que vieram fora do filtro pedido (ex.: UF diferente): a API às vezes ignora filtros';
