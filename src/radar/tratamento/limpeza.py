"""Limpeza dos textos livres que vêm do PNCP (objeto da compra, descrição dos itens...).

Os textos chegam do jeito que cada órgão digitou: espaços duplos, quebras de linha no meio da
frase, tabulações e até caracteres de controle invisíveis. Isso atrapalha a busca, a exibição no
app e a qualidade dos embeddings (Sprint 8).
"""

from __future__ import annotations


def normalizar_texto(texto: str | None) -> str | None:
    """Deixa um texto livre pronto para exibir, buscar e gerar embeddings.

    Regras (os testes em tests/unit/test_limpeza.py são a especificação executável):
      1. None continua None.
      2. Remove espaços do começo e do fim.
      3. Troca qualquer sequência de espaços, tabs e quebras de linha por UM espaço.
      4. Remove caracteres de controle invisíveis (ex.: "\\x00", "\\x1f"), mas mantém acentos e "ç".
      5. Não muda maiúsculas e minúsculas (o texto original aparece no app).
      6. Se não sobrar nada, devolve None.
    """
    # TODO(estagiaria): #7 implementar seguindo as regras da docstring (e fazer os testes passarem)
    raise NotImplementedError("TODO(estagiaria): #7 normalizar_texto")
