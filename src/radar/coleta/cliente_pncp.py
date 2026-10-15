"""Cliente da API de consultas do PNCP (https://pncp.gov.br/api/consulta/v3/api-docs).

Versão inicial, simples DE PROPÓSITO:
  * espera um intervalo FIXO entre as chamadas;
  * se a API responder 429 (excesso de requisições), espera um tempo fixo e tenta de novo.

Já vimos na prática que ~20 chamadas seguidas em menos de um minuto geram 429. Na Sprint 4 este
cliente ganha controle de taxa de verdade (backoff exponencial, cabeçalho Retry-After, ritmo
adaptativo) — e testes que provam isso.

Quirks conhecidos da API (documentados em docs/arquitetura.md):
  * `contratacoes/proposta`: `dataFinal` é o TETO da data de encerramento das propostas;
  * `tamanhoPagina` vai de 10 a 50 nas contratações (e até 500 em contratos);
  * o endpoint de itens devolve só 10 itens se você não mandar `tamanhoPagina`.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterator
from datetime import date
from typing import Any

import httpx

URL_CONSULTA = "https://pncp.gov.br/api/consulta/v1"
USER_AGENT = "radar-licitacoes/0.1 (+https://github.com/Ponte-Informatica-Pontidata/radar-licitacoes)"


class ErroPncp(RuntimeError):
    """A API respondeu algo que o cliente não sabe tratar."""


class ClientePncp:
    def __init__(
        self,
        intervalo: float = 1.5,
        http: httpx.Client | None = None,
        dormir: Callable[[float], None] = time.sleep,
        tentativas_429: int = 3,
        espera_429: float = 30.0,
    ) -> None:
        self.intervalo = intervalo
        self.http = http or httpx.Client(
            base_url=URL_CONSULTA,
            timeout=60.0,
            headers={"Accept": "application/json", "User-Agent": USER_AGENT},
        )
        self.dormir = dormir
        self.tentativas_429 = tentativas_429
        self.espera_429 = espera_429
        self.requisicoes = 0

    def _get(self, caminho: str, params: dict[str, Any]) -> dict[str, Any] | None:
        for _ in range(self.tentativas_429 + 1):
            if self.requisicoes:
                self.dormir(self.intervalo)
            self.requisicoes += 1
            resposta = self.http.get(caminho, params=params)
            if resposta.status_code == 429:
                self.dormir(self.espera_429)
                continue
            if resposta.status_code == 204:
                return None
            if resposta.status_code != 200:
                raise ErroPncp(f"HTTP {resposta.status_code} em {caminho}: {resposta.text[:200]}")
            return resposta.json()
        raise ErroPncp(f"A API continuou respondendo 429 em {caminho}")

    def contratacoes_com_proposta_aberta(
        self, uf: str, data_final: date, max_paginas: int | None = None
    ) -> Iterator[dict[str, Any]]:
        """Contratações da UF com proposta aberta e encerramento até `data_final` (JSON bruto)."""
        pagina = 1
        while True:
            dados = self._get(
                "/contratacoes/proposta",
                {"dataFinal": data_final.strftime("%Y%m%d"), "uf": uf, "pagina": pagina, "tamanhoPagina": 50},
            )
            if not dados or not dados.get("data"):
                return
            yield from dados["data"]
            total_paginas = int(dados.get("totalPaginas") or 0)
            if pagina >= total_paginas or (max_paginas is not None and pagina >= max_paginas):
                return
            pagina += 1
