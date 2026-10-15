"""Factory: cria a estratégia de IA a partir da configuração.

Por que uma fábrica? O pipeline e o app pedem "um gerador de embeddings" sem saber qual. A
escolha fica num lugar só, guiada por variável de ambiente (RADAR_EMBEDDINGS, RADAR_RESUMO).
"""

from __future__ import annotations

from radar.config import Configuracao
from radar.ia.embeddings import EmbeddingsFalso, EmbeddingsFastEmbed, GeradorEmbeddings
from radar.ia.resumo import Resumidor, ResumidorExtrativo, ResumidorOllama


def criar_gerador_embeddings(nome: str) -> GeradorEmbeddings:
    if nome == "fastembed":
        return EmbeddingsFastEmbed()
    if nome == "falso":
        return EmbeddingsFalso()
    raise ValueError(f"Gerador de embeddings desconhecido: {nome!r} (use 'fastembed' ou 'falso')")


def criar_resumidor(nome: str, configuracao: Configuracao) -> Resumidor:
    if nome == "extrativo":
        return ResumidorExtrativo()
    if nome == "ollama":
        return ResumidorOllama(configuracao.radar_ollama_url, configuracao.radar_ollama_modelo)
    raise ValueError(f"Resumidor desconhecido: {nome!r} (use 'extrativo' ou 'ollama')")
