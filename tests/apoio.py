"""Apoio aos testes: marcador das tarefas da estagiária."""

from __future__ import annotations

import pytest


def todo_estagiaria(issue: int | str, raises: type[BaseException] | tuple = NotImplementedError):
    """Marca um teste cuja implementação é uma tarefa pendente da estagiária.

    Enquanto a tarefa não existe, o teste "falha do jeito esperado" (XFAIL) e o CI continua verde.
    Quando a implementação fica pronta, o teste passa — e, por ser `strict`, o pytest acusa XPASS
    como falha. É o sinal para APAGAR o @todo_estagiaria do teste no seu Pull Request.

    Para ver as falhas de verdade enquanto trabalha:  pytest --runxfail -m estagiaria
    """

    def decorar(funcao):
        funcao = pytest.mark.estagiaria(issue=issue)(funcao)
        return pytest.mark.xfail(
            raises=raises,
            strict=True,
            reason=f"TODO(estagiaria): #{issue} — quando terminar, apague o @todo_estagiaria deste teste",
        )(funcao)

    return decorar
