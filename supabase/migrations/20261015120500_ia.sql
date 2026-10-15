-- Resultados de IA, em tabelas separadas das contratações.
--
-- Por quê: trocar de modelo ou de prompt não pode apagar o histórico nem misturar versões.
-- Cada linha diz qual modelo (e qual versão de prompt) gerou o resultado.
-- O índice vetorial (HNSW) será criado na Sprint 9, depois de medirmos o volume.

create table radar.contratacao_embedding (
    numero_controle_pncp text primary key
        references radar.contratacao (numero_controle_pncp) on delete cascade,
    modelo text not null,
    texto_hash char(64) not null,
    embedding extensions.halfvec(384) not null,
    gerado_em timestamptz not null default now()
);
comment on table radar.contratacao_embedding is
    'Vetor do objeto da contratação. halfvec = metade do espaço de vector (cabe nos 500 MB do Supabase)';
comment on column radar.contratacao_embedding.texto_hash is
    'SHA-256 do texto que gerou o vetor: se o texto mudar, o vetor precisa ser refeito';

create table radar.contratacao_resumo (
    numero_controle_pncp text primary key
        references radar.contratacao (numero_controle_pncp) on delete cascade,
    resumo text not null,
    modelo text not null,
    versao_prompt text not null,
    gerado_em timestamptz not null default now()
);
comment on table radar.contratacao_resumo is 'Resumo gerado por IA (ou extrativo), com rastreabilidade de modelo e prompt';
