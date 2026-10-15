"""O cliente é testado sem internet: httpx.MockTransport responde no lugar da API."""

from __future__ import annotations

from datetime import date

import httpx
import pytest

from radar.coleta.cliente_pncp import URL_CONSULTA, ClientePncp, ErroPncp


def montar_cliente(respostas: list[httpx.Response]) -> tuple[ClientePncp, list[httpx.Request], list[float]]:
    chamadas: list[httpx.Request] = []
    esperas: list[float] = []

    def responder(request: httpx.Request) -> httpx.Response:
        chamadas.append(request)
        return respostas.pop(0)

    http = httpx.Client(base_url=URL_CONSULTA, transport=httpx.MockTransport(responder))
    return ClientePncp(intervalo=1.0, http=http, dormir=esperas.append), chamadas, esperas


def pagina(numero: int, total: int, registros: list[dict]) -> httpx.Response:
    return httpx.Response(200, json={"data": registros, "numeroPagina": numero, "totalPaginas": total})


def test_percorre_todas_as_paginas_com_os_parametros_certos():
    cliente, chamadas, esperas = montar_cliente([pagina(1, 2, [{"id": 1}]), pagina(2, 2, [{"id": 2}])])
    registros = list(cliente.contratacoes_com_proposta_aberta("MG", date(2027, 10, 15)))
    assert [r["id"] for r in registros] == [1, 2]
    assert chamadas[0].url.path.endswith("/api/consulta/v1/contratacoes/proposta")
    assert chamadas[0].url.params["dataFinal"] == "20271015"
    assert chamadas[0].url.params["uf"] == "MG"
    assert chamadas[1].url.params["pagina"] == "2"
    assert esperas == [1.0]  # espera o intervalo antes da 2ª chamada


def test_respeita_o_maximo_de_paginas():
    cliente, chamadas, _ = montar_cliente([pagina(1, 5, [{"id": 1}])])
    assert len(list(cliente.contratacoes_com_proposta_aberta("MG", date(2027, 1, 1), max_paginas=1))) == 1
    assert len(chamadas) == 1


def test_espera_e_repete_quando_a_api_responde_429():
    cliente, chamadas, esperas = montar_cliente([httpx.Response(429), pagina(1, 1, [{"id": 1}])])
    assert len(list(cliente.contratacoes_com_proposta_aberta("MG", date(2027, 1, 1)))) == 1
    assert len(chamadas) == 2
    assert 30.0 in esperas


def test_desiste_se_o_429_continua():
    cliente, _, _ = montar_cliente([httpx.Response(429) for _ in range(4)])
    with pytest.raises(ErroPncp, match="429"):
        list(cliente.contratacoes_com_proposta_aberta("MG", date(2027, 1, 1)))


def test_204_significa_sem_resultados():
    cliente, _, _ = montar_cliente([httpx.Response(204)])
    assert list(cliente.contratacoes_com_proposta_aberta("MG", date(2027, 1, 1))) == []


def test_erro_http_vira_erro_pncp():
    cliente, _, _ = montar_cliente([httpx.Response(500, text="erro interno")])
    with pytest.raises(ErroPncp, match="HTTP 500"):
        list(cliente.contratacoes_com_proposta_aberta("MG", date(2027, 1, 1)))
