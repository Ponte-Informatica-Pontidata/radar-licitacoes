# Registros de decisão de arquitetura (ADR)

Um ADR registra **uma** decisão importante: o contexto, o que decidimos, as alternativas e as
consequências. Ele não é apagado quando a decisão muda: um ADR novo o substitui.

| # | Decisão | Status |
|---|---|---|
| [0001](0001-camadas-e-padroes.md) | Camadas + Adapter, Repository, Strategy/Factory e Service | aceito |
| [0002](0002-sql-explicito-sem-orm.md) | SQL explícito com psycopg, sem ORM | aceito |
| [0003](0003-postgres-pgvector-supabase.md) | Postgres + pgvector (Docker no dev, Supabase na produção) e `halfvec` | aceito |
| [0004](0004-migrations-e-carga-em-staging.md) | Migrations com Supabase CLI e carga CSV via staging | aceito |
| [0005](0005-lgpd-desde-a-origem.md) | LGPD aplicada antes de gravar, com trava no banco | aceito |
| [0006](0006-tarefas-como-testes-xfail.md) | Tarefas da estagiária como testes `xfail(strict)` | aceito |
| [0007](0007-streamlit-community-cloud.md) | Streamlit Community Cloud (e não Vercel) para o app | aceito |
| [0008](0008-ia-local-e-em-lote.md) | IA local (FastEmbed, Ollama) e em lote no GitHub Actions | aceito |

## Modelo

```markdown
# NNNN — Título da decisão

- Status: proposto | aceito | substituído por NNNN
- Data: dd/mm/aaaa

## Contexto
O problema e as forças em jogo (limites, prazos, riscos).

## Decisão
O que vamos fazer.

## Alternativas consideradas
O que mais foi avaliado e por que não foi escolhido.

## Consequências
O que fica mais fácil, o que fica mais difícil e o que precisamos acompanhar.
```
