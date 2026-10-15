# 0004 — Migrations com Supabase CLI e carga CSV via staging

- Status: aceito
- Data: 15/10/2026

## Contexto
O banco existe em três lugares (Docker, CI, Supabase) e não pode ser alterado à mão. A base inicial é
um CSV real e "sujo", que precisa entrar no banco com tipos, fuso e chaves corretos.

## Decisão
- Estrutura (DDL) só por migrations em `supabase/migrations`, aplicadas com **o mesmo comando** em todos
  os ambientes: `supabase db push --db-url ...` (histórico em `supabase_migrations.schema_migrations`).
- Carga (DML) em três passos: `\copy` para `staging` (tudo texto, `HEADER MATCH`) → `INSERT … SELECT`
  para `radar` (conversões, `ON CONFLICT DO NOTHING`) → validação contra o `MANIFESTO.json`.

## Alternativas consideradas
- `COPY` direto nas tabelas finais: qualquer valor estranho derruba a carga inteira sem dizer onde.
- Carga via pandas `to_sql`: esconde tipos e conversões, e é lenta para dezenas de milhares de linhas.

## Consequências
- A carga é idempotente e auditável (cada passo é um arquivo SQL legível).
- Migration aplicada não se edita: correção = migration nova.
- O CI prova a cada PR que o banco nasce do zero e carrega a base inteira.
