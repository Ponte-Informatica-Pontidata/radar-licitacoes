from __future__ import annotations

from datetime import UTC, date, datetime

from radar.coleta.adaptador_pncp import AdaptadorPncp
from radar.persistencia.memoria import RepositorioMemoria
from radar.servicos.ingestao import ServicoIngestao
from radar.servicos.licitacoes import ServicoLicitacoes


def test_abertas_respeita_a_data_de_referencia(contratacoes_api):
    contratacoes = [AdaptadorPncp().contratacao(b) for b in contratacoes_api]
    servico = ServicoLicitacoes(RepositorioMemoria(contratacoes))

    todas = servico.abertas(referencia=datetime(2026, 10, 15, tzinfo=UTC))
    assert len(todas) == 3
    encerramentos = [t.data_encerramento_proposta for t in todas]
    assert encerramentos == sorted(encerramentos)

    mais_tarde = datetime(2027, 4, 1, tzinfo=UTC)
    esperadas = {c.numero_controle_pncp for c in contratacoes if c.data_encerramento_proposta >= mais_tarde}
    assert {t.numero_controle_pncp for t in servico.abertas(referencia=mais_tarde)} == esperadas


def test_abertas_normaliza_os_filtros():
    chamadas = []

    class RepositorioEspiao(RepositorioMemoria):
        def listar_abertas(self, **kwargs):
            chamadas.append(kwargs)
            return []

    servico = ServicoLicitacoes(RepositorioEspiao())
    servico.abertas(uf=" mg ", texto="   ", limite=10_000)
    assert chamadas[0]["uf"] == "MG"
    assert chamadas[0]["texto"] is None
    assert chamadas[0]["limite"] == 500


def test_ingestao_grava_tudo_o_que_o_cliente_trouxe(contratacoes_api):
    class ClienteFalso:
        def contratacoes_com_proposta_aberta(self, uf, data_final, max_paginas):
            self.argumentos = (uf, data_final, max_paginas)
            yield from contratacoes_api

    cliente = ClienteFalso()
    repositorio = RepositorioMemoria()
    resultado = ServicoIngestao(cliente, AdaptadorPncp(), repositorio).coletar_propostas_abertas(
        "MG", dias=30, hoje=date(2026, 10, 15)
    )
    assert resultado.lidos == resultado.gravados == 3
    assert cliente.argumentos == ("MG", date(2026, 11, 14), None)
    assert len(repositorio.contratacoes) == 3
