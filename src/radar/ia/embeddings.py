"""Geradores de embeddings (padrão Strategy).

Todos seguem o mesmo contrato (`GeradorEmbeddings`), então o resto do sistema não sabe qual está
em uso. Isso importa porque limites e preços de IA mudam: trocar de modelo vira mudança de
configuração (RADAR_EMBEDDINGS), não de código.

Regra de ouro: a consulta e os documentos PRECISAM usar o mesmo modelo. Vetores de modelos
diferentes não são comparáveis — por isso a tabela radar.contratacao_embedding guarda o modelo.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Sequence
from typing import Protocol

MODELO_PADRAO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class GeradorEmbeddings(Protocol):
    modelo: str
    dimensao: int

    def gerar(self, textos: Sequence[str]) -> list[list[float]]: ...


class EmbeddingsFastEmbed:
    """Modelo multilíngue pequeno (384 dimensões, ~220 MB), roda em CPU via ONNX, sem GPU nem torch.

    Instale com: uv sync --extra ia  (dentro do container: docker compose run --rm dev uv sync --extra ia)
    Atenção: o modelo lê no máximo 128 tokens — textos longos são cortados.
    """

    dimensao = 384

    def __init__(self, modelo: str = MODELO_PADRAO) -> None:
        try:
            from fastembed import TextEmbedding
        except ImportError as exc:  # pragma: no cover - depende do extra "ia"
            raise RuntimeError("fastembed não instalado: rode `uv sync --extra ia`") from exc
        self.modelo = modelo
        self._modelo = TextEmbedding(model_name=modelo)

    def gerar(self, textos: Sequence[str]) -> list[list[float]]:
        return [vetor.tolist() for vetor in self._modelo.embed(list(textos))]


class EmbeddingsFalso:
    """Vetores determinísticos (hash do texto): para testes e para rodar sem baixar modelo.

    Não têm significado nenhum — servem só para exercitar o encanamento (banco, índices, busca).
    """

    modelo = "falso-sha256"

    def __init__(self, dimensao: int = 384) -> None:
        self.dimensao = dimensao

    def gerar(self, textos: Sequence[str]) -> list[list[float]]:
        return [self._vetor(t) for t in textos]

    def _vetor(self, texto: str) -> list[float]:
        valores: list[float] = []
        bloco = 0
        while len(valores) < self.dimensao:
            digest = hashlib.sha256(f"{bloco}:{texto}".encode()).digest()
            valores.extend((b - 127.5) / 127.5 for b in digest)
            bloco += 1
        valores = valores[: self.dimensao]
        norma = math.sqrt(sum(v * v for v in valores)) or 1.0
        return [v / norma for v in valores]
