# Banco de dados do Radar

Tudo o que cria ou altera o banco está versionado aqui. **Nunca altere o banco "na mão".**
Se precisar de uma tabela, coluna ou view nova, crie uma migration.

## Mapa

| Caminho | O que é | Tipo de SQL |
|---|---|---|
| `supabase/migrations/*.sql` | Estrutura: schemas, tabelas, chaves, constraints, papéis | DDL |
| `banco/carga/01_staging.sql` | Lê os CSVs de `dados/csv` para o schema `staging` (tudo texto) | DML (`\copy`) |
| `banco/carga/02_transformar.sql` | Converte tipos e fuso e grava no schema `radar` | DML (`INSERT … SELECT`) |
| `banco/carga/03_validar.sql` | Confere linhas e chaves contra o `dados/MANIFESTO.json` | consultas + `DO` |
| `banco/migrar.sh` | Aplica as migrations com a Supabase CLI | script |
| `banco/carregar.sh` | Roda os 3 passos da carga em sequência | script |

## Criar e carregar o banco local (Sprint 0)

Com o ambiente no ar (`docker compose up -d --build`):

```bash
# 1. Estrutura (DDL): cria schemas e tabelas
docker compose run --rm dev bash banco/migrar.sh

# 2. Carga (DML), passo a passo
docker compose run --rm dev psql -f banco/carga/01_staging.sql
docker compose run --rm dev psql -f banco/carga/02_transformar.sql
docker compose run --rm dev psql -f banco/carga/03_validar.sql
```

Os comandos funcionam do mesmo jeito no PowerShell e no bash. O container `dev` já sabe onde
está o banco (variáveis `PG*` no `docker-compose.yml`).

Para explorar o banco:
- psql interativo: `docker compose run --rm dev psql`
- Adminer no navegador: `docker compose --profile ferramentas up -d adminer` e depois http://localhost:8080
  (servidor `db`, usuário `postgres`, senha `postgres`)

## Criar uma migration nova

```bash
docker compose run --rm dev supabase migration new criar_view_licitacoes_abertas
# edite o arquivo criado em supabase/migrations/ e aplique:
docker compose run --rm dev bash banco/migrar.sh
```

Uma migration já aplicada (e já na `main`) **não se edita**: se algo mudou, crie outra.

## Começar do zero

`docker compose down -v` apaga o volume do banco local. Depois é só repetir migrations + carga.

## Produção (Sprint 7)

No Supabase, os passos são os mesmos. Muda só a conexão: a URL do pooler (modo sessão, porta 5432,
`sslmode=require`) entra no lugar da local, via variáveis de ambiente. O passo a passo entra junto
com a issue da Sprint 7.
