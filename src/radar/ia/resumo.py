"""Resumidores de texto (padrão Strategy).

  ResumidorExtrativo -> sem IA: corta o texto original numa frase curta (fallback sempre disponível)
  ResumidorOllama    -> LLM local via Ollama (docker compose --profile ia up -d ollama)

Cada resumo gravado guarda `modelo` e `versao_prompt`: mudar o prompt é mudar a versão.
"""

from __future__ import annotations

from typing import Protocol

import httpx

PROMPT_V1 = """Você é analista de licitações. Resuma em até 2 frases, em português simples, o que o órgão
público quer comprar ou contratar. Diga o quê, para quem (se aparecer) e algum requisito importante.
Não invente informação que não está no texto.

Texto do edital:
{texto}

Resumo:"""


class Resumidor(Protocol):
    modelo: str
    versao_prompt: str

    def resumir(self, texto: str) -> str: ...


class ResumidorExtrativo:
    modelo = "extrativo"
    versao_prompt = "extrativo-v1"

    def __init__(self, max_caracteres: int = 240) -> None:
        self.max_caracteres = max_caracteres

    def resumir(self, texto: str) -> str:
        texto = " ".join(texto.split())
        if len(texto) <= self.max_caracteres:
            return texto
        corte = texto[: self.max_caracteres].rsplit(" ", 1)[0]
        return corte.rstrip(" ,;:-") + "…"


class ResumidorOllama:
    versao_prompt = "llm-v1"

    def __init__(self, url: str, modelo: str, http: httpx.Client | None = None) -> None:
        self.modelo = modelo
        self.http = http or httpx.Client(base_url=url, timeout=300.0)

    def resumir(self, texto: str) -> str:
        resposta = self.http.post(
            "/api/generate",
            json={
                "model": self.modelo,
                "prompt": PROMPT_V1.format(texto=texto),
                "stream": False,
                "think": False,
                "options": {"temperature": 0.2},
            },
        )
        resposta.raise_for_status()
        return resposta.json()["response"].strip()
