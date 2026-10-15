#!/usr/bin/env bash
# DDL: aplica as migrations de supabase/migrations no banco de DATABASE_URL.
#
# É o MESMO comando do CI e da produção (Supabase). Ele só aplica o que ainda não foi aplicado:
# o histórico fica na tabela supabase_migrations.schema_migrations.
#
# Como rodar:  docker compose run --rm dev bash banco/migrar.sh
set -euo pipefail

: "${DATABASE_URL:?defina DATABASE_URL (no Docker ela já vem do docker-compose.yml)}"

echo ">> Aplicando migrations de supabase/migrations ..."
supabase db push --db-url "$DATABASE_URL" --yes

echo ">> Migrations registradas no banco:"
psql -X -q -c "select version, name from supabase_migrations.schema_migrations order by version"
