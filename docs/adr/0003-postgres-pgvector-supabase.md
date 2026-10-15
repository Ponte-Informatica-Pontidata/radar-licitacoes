# 0003 — Postgres + pgvector (Docker no dev, Supabase na produção) e `halfvec`

- Status: aceito
- Data: 15/10/2026

## Contexto
Precisamos de dados relacionais (órgãos, contratações, contratos) e de busca por significado
(vetores). A produção tem de ser gratuita: o Supabase Free oferece 500 MB de Postgres com pgvector.

## Decisão
- Um único Postgres 17 com pgvector para relacional + vetores.
- Desenvolvimento em Docker (`pgvector/pgvector:0.8.7-pg17`); produção no Supabase (PG 17, pgvector ≥ 0.8).
- Vetores como `halfvec(384)` (meia precisão), gerados por um modelo multilíngue pequeno.
- Conexão de produção pelo **pooler** (IPv4, modo sessão), porque a conexão direta do Supabase é só IPv6.

## Alternativas consideradas
- Banco vetorial separado (Qdrant, Pinecone): mais um serviço, mais um limite gratuito para vigiar.
- `vector(384)` em precisão cheia: o dobro do espaço sem ganho perceptível para busca semântica.

## Consequências
- JOIN entre resultado vetorial e filtros (UF, valor, data) numa só consulta.
- Os 500 MB viram restrição de modelagem: medir, recortar e agregar fazem parte do trabalho (Sprint 14).
