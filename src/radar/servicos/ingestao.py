"""Caso de uso: coletar contratações abertas na API do PNCP e gravar no banco.

Versão inicial (ingênua de propósito). Ao longo da fase 2 ela ganha:
  * Sprint 4 — controle de taxa no cliente (429, backoff, Retry-After);
  * Sprint 5 — validação dos resultados (filtros que a API ignora) e registro em radar.execucao_ingestao;
  * Sprint 6 — tratamento de LGPD antes de gravar;
  * Sprint 7 — ingestão incremental agendada no GitHub Actions.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from radar.coleta.adaptador_pncp import AdaptadorPncp
from radar.coleta.cliente_pncp import ClientePncp
from radar.persistencia.repositorio import RepositorioLicitacoes


@dataclass
class ResultadoIngestao:
    lidos: int = 0
    gravados: int = 0


class ServicoIngestao:
    def __init__(
        self,
        cliente: ClientePncp,
        adaptador: AdaptadorPncp,
        repositorio: RepositorioLicitacoes,
    ) -> None:
        self.cliente = cliente
        self.adaptador = adaptador
        self.repositorio = repositorio

    def coletar_propostas_abertas(
        self,
        uf: str,
        dias: int = 365,
        max_paginas: int | None = None,
        hoje: date | None = None,
    ) -> ResultadoIngestao:
        data_final = (hoje or date.today()) + timedelta(days=dias)
        resultado = ResultadoIngestao()
        contratacoes = []
        for bruto in self.cliente.contratacoes_com_proposta_aberta(uf, data_final, max_paginas):
            resultado.lidos += 1
            contratacoes.append(self.adaptador.contratacao(bruto))
        resultado.gravados = self.repositorio.salvar_contratacoes(contratacoes)
        return resultado
