-- Extensões e schemas do Radar de Licitações.
--
-- Por que schemas separados?
--   radar   -> dados tratados, com tipos, chaves e regras (é o que o app lê)
--   staging -> área de pouso da carga CSV: tudo texto, sem regras, recriada a cada carga
-- No Supabase, só o schema `public` é exposto pela Data API. Deixar os dados em `radar`
-- evita expor tabelas sem querer: o app conecta direto no Postgres com um papel de leitura.

create schema if not exists extensions;
create extension if not exists vector with schema extensions;    -- embeddings (busca por significado)
create extension if not exists unaccent with schema extensions;  -- busca sem acento
create extension if not exists pg_trgm with schema extensions;   -- busca aproximada por texto

create schema if not exists radar;
create schema if not exists staging;

comment on schema radar is 'Dados tratados do Radar de Licitações (fonte: API pública do PNCP)';
comment on schema staging is 'Área de pouso da carga CSV: colunas texto, sem constraints';
