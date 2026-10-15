# 0006 — Tarefas da estagiária como testes `xfail(strict)`

- Status: aceito
- Data: 15/10/2026

## Contexto
O modelo do laboratório é "eu monto, ela completa": cada tarefa tem um `TODO(estagiaria)` e um teste que
falha até ela terminar. Mas a `main` é protegida e exige CI verde: um teste vermelho travaria todo mundo.

## Decisão
Os testes das tarefas usam `@todo_estagiaria(issue=N, raises=...)` (em `tests/apoio.py`), que aplica
`pytest.mark.xfail(strict=True)`:
- enquanto a tarefa não existe, o teste falha **do jeito esperado** (XFAIL) e o CI fica verde;
- implementação parcial falha de outro jeito → FAIL → o PR não passa;
- implementação completa passa → XPASS(strict) → o PR falha até ela **apagar o marcador**.

`raises` muda conforme a tarefa: `NotImplementedError` (Python), `psycopg.errors.UndefinedTable` (views),
`AssertionError` (documentação).

## Consequências
- Remover o marcador é o critério de aceite objetivo de cada tarefa.
- `pytest --runxfail -m estagiaria` mostra as falhas reais durante o trabalho.
- O resumo do pytest lista as tarefas pendentes por issue.
