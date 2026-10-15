#!/usr/bin/env bash
# DML: carga inicial completa (os 3 passos em sequência). Usado pelo CI.
# Na Sprint 0, rode os passos um por um para entender cada um (veja banco/README.md).
#
# Como rodar:  docker compose run --rm dev bash banco/carregar.sh
set -euo pipefail

for passo in banco/carga/01_staging.sql banco/carga/02_transformar.sql banco/carga/03_validar.sql; do
    echo ">> $passo"
    psql -X -q -f "$passo"
done
