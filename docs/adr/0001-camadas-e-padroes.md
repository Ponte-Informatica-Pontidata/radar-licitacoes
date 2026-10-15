# 0001 — Camadas + Adapter, Repository, Strategy/Factory e Service

- Status: aceito
- Data: 15/10/2026

## Contexto
O Radar junta uma API externa instável (PNCP), um banco relacional, IA e um app. Uma estagiária vai
evoluir o código por 22 sprints, em pedaços pequenos. Sem fronteiras claras, cada mudança espalha efeitos.

## Decisão
Separar em camadas (coleta → tratamento → persistência → serviço → apresentação) e usar padrões só onde
resolvem um problema concreto:
- **Adapter** (`AdaptadorPncp`): único lugar que conhece o JSON do PNCP.
- **Repository** (`RepositorioLicitacoes`): contrato da persistência; Postgres e memória implementam.
- **Strategy + Factory** (`ia/`): trocar o provedor de IA por configuração.
- **Service layer** (`servicos/`): casos de uso compartilhados por CLI, app e pipeline.

## Alternativas consideradas
- Script único (notebook → banco): rápido no início, impossível de testar e evoluir.
- Arquitetura hexagonal completa: mais cerimônia do que um MVP com uma fonte e um banco precisa.

## Consequências
- Testes unitários rodam sem rede e sem banco (fakes nos pontos de troca).
- Cada tarefa da estagiária mexe em uma camada por vez.
- Custo: mais arquivos e a disciplina de não "pular" camadas (ex.: SQL dentro do Streamlit).
