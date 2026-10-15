# 📡 Radar de Licitações

[![CI](https://github.com/Ponte-Informatica-Pontidata/radar-licitacoes/actions/workflows/ci.yml/badge.svg)](https://github.com/Ponte-Informatica-Pontidata/radar-licitacoes/actions/workflows/ci.yml)

O Radar mostra as **licitações com proposta aberta** publicadas no
[Portal Nacional de Contratações Públicas (PNCP)](https://pncp.gov.br). Ele permite buscar por filtros e
**por significado** (embeddings + pgvector) e traz **resumos gerados por IA**.

É o primeiro produto do [Laboratório Pontidata](https://github.com/Ponte-Informatica-Pontidata/laboratorio),
um programa de estágio em Big Data e IA que simula o dia a dia de uma software house.

> **Modelo "eu monto, ela completa":** o projeto nasce estruturado e funcionando. As partes que a
> estagiária constrói estão marcadas com `TODO(estagiaria): #<issue>` e têm testes esperando por ela.

## Começando (Docker)

Pré-requisitos: Git, Docker Desktop (no Windows, com WSL2) e VS Code.

```bash
git clone https://github.com/Ponte-Informatica-Pontidata/radar-licitacoes.git
cd radar-licitacoes
docker compose up -d --build                         # banco + app em http://localhost:8501
docker compose run --rm dev bash banco/migrar.sh     # cria as tabelas (DDL)
docker compose run --rm dev bash banco/carregar.sh   # carrega a base CSV (DML) e valida
docker compose run --rm dev pytest                   # roda os testes
```

Todos os comandos funcionam igual no PowerShell e no bash. O passo a passo comentado da carga está em
[`banco/README.md`](banco/README.md).

## Comandos do dia a dia

| Para... | Rode |
|---|---|
| subir o ambiente | `docker compose up -d --build` |
| ver o app | http://localhost:8501 |
| abrir um terminal no container | `docker compose run --rm dev bash` |
| abrir o banco no psql | `docker compose run --rm dev psql` |
| abrir o Adminer (banco no navegador) | `docker compose --profile ferramentas up -d adminer` → http://localhost:8080 |
| rodar os testes | `docker compose run --rm dev pytest` |
| ver as falhas reais das suas tarefas | `docker compose run --rm dev pytest --runxfail -m estagiaria` |
| checar estilo | `docker compose run --rm dev ruff check .` e `ruff format --check .` |
| coletar dados novos da API | `docker compose run --rm dev radar coletar --paginas 2` |
| contar linhas das tabelas | `docker compose run --rm dev radar status` |
| criar uma migration | `docker compose run --rm dev supabase migration new <nome>` |
| desligar tudo | `docker compose down` (acrescente `-v` para apagar o banco local) |

## Como o código está organizado

```
src/radar/
  coleta/        cliente da API do PNCP + Adapter (JSON -> domínio)
  tratamento/    limpeza, validação e qualidade de dados (funções puras)
  persistencia/  Repository: o único lugar com SQL
  ia/            embeddings e resumos (Strategy + Factory)
  servicos/      casos de uso usados pela CLI e pelo app
  dominio/       entidades (dataclasses)
  cli.py         comando `radar`
app/             Streamlit (apresentação)
supabase/        migrations versionadas (DDL)
banco/           scripts de carga (DML) e validação
dados/           base CSV real (snapshot do PNCP com LGPD aplicada) + dicionário
tests/           unitários (sem banco) e de integração (com banco)
docs/            arquitetura, decisões (ADRs) e guias
```

A arquitetura completa, com os diagramas, está em [`docs/arquitetura.md`](docs/arquitetura.md).

## Como trabalhamos

- Uma branch por issue: `tipo/<número>-descricao` (ex.: `feat/7-normalizar-texto`).
- Pull Request sempre, com o template preenchido, incluindo **os prompts de IA usados** e
  **a explicação com suas palavras**.
- O título do PR segue Conventional Commits (`feat: …`, `fix: …`, `docs: …`). O CI confere.
- A `main` é protegida: só entra por PR revisado, com o CI verde.
- Segredos só em `.env` (que não vai para o git) ou nos Secrets do GitHub.

Regras completas, rubrica e roadmap: repositório [`laboratorio`](https://github.com/Ponte-Informatica-Pontidata/laboratorio).

## Dados e LGPD

A base em `dados/csv` é um recorte real do PNCP (MG). Antes de entrar no repositório, passou por
tratamento de LGPD: pessoas físicas pseudonimizadas, CPFs e processos judiciais mascarados. Detalhes em
[`dados/ORIGEM.md`](dados/ORIGEM.md) e significado de cada coluna em [`dados/DICIONARIO.md`](dados/DICIONARIO.md).
