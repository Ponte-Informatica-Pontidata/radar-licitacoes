"""Configuração lida das variáveis de ambiente (e do arquivo .env, quando existir).

Nada de segredo no código: senhas e URLs vêm do ambiente. No Docker, o docker-compose.yml
já define as variáveis do banco local.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracao(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://postgres:postgres@localhost:54322/postgres?sslmode=disable"
    radar_uf: str = "MG"
    radar_pncp_intervalo: float = 1.5
    radar_embeddings: str = "falso"
    radar_resumo: str = "extrativo"
    radar_ollama_url: str = "http://localhost:11434"
    radar_ollama_modelo: str = "qwen2.5:3b"


@lru_cache
def obter_configuracao() -> Configuracao:
    return Configuracao()
