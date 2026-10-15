# 0002 — SQL explícito com psycopg, sem ORM

- Status: aceito
- Data: 15/10/2026

## Contexto
O foco do estágio é **bases de dados**: modelagem, consultas, índices, qualidade. Um ORM esconde
justamente o que ela precisa praticar.

## Decisão
Usar `psycopg` 3 com SQL escrito à mão, concentrado na camada de persistência (Repository). Views e
transformações pesadas ficam no próprio banco, versionadas em migrations.

## Alternativas consideradas
- SQLAlchemy ORM: produtivo, mas gera SQL que ninguém lê e acrescenta um conceito a mais (sessão, mapeamento).
- SQLAlchemy Core: meio-termo, ainda assim uma camada a mais sem ganho real para o MVP.

## Consequências
- Ela escreve, lê e otimiza SQL de verdade (EXPLAIN, índices) desde a Sprint 1.
- Mudanças de schema exigem atualizar o SQL do Repository: os testes de integração pegam a quebra.
