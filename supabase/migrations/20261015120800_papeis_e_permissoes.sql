-- Papéis com o mínimo de privilégio.
--   radar_leitura -> o app (Streamlit) só lê
--   radar_escrita -> o pipeline grava
-- Os papéis são NOLOGIN: os usuários de login (com senha) são criados fora do git,
-- no ambiente de produção (Sprint 7), e herdam um destes papéis.

do $$
begin
    if not exists (select from pg_roles where rolname = 'radar_leitura') then
        create role radar_leitura nologin;
    end if;
    if not exists (select from pg_roles where rolname = 'radar_escrita') then
        create role radar_escrita nologin;
    end if;
end
$$;

grant usage on schema radar to radar_leitura, radar_escrita;
grant usage on schema extensions to radar_leitura, radar_escrita;
grant select on all tables in schema radar to radar_leitura;
grant select, insert, update, delete on all tables in schema radar to radar_escrita;
grant usage, select on all sequences in schema radar to radar_escrita;

alter default privileges in schema radar grant select on tables to radar_leitura;
alter default privileges in schema radar grant select, insert, update, delete on tables to radar_escrita;
alter default privileges in schema radar grant usage, select on sequences to radar_escrita;

-- No Supabase existem os papéis anon/authenticated (Data API). Garantimos que não enxergam o radar.
do $$
begin
    if exists (select from pg_roles where rolname = 'anon') then
        revoke all on schema radar, staging from anon;
    end if;
    if exists (select from pg_roles where rolname = 'authenticated') then
        revoke all on schema radar, staging from authenticated;
    end if;
end
$$;
