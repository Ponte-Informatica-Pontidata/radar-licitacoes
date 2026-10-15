from __future__ import annotations

import json
import math

import httpx
import pytest

from radar.config import Configuracao
from radar.ia.fabrica import criar_gerador_embeddings, criar_resumidor
from radar.ia.resumo import ResumidorExtrativo, ResumidorOllama


def test_fabrica_recusa_estrategia_desconhecida():
    with pytest.raises(ValueError):
        criar_gerador_embeddings("gpt-qualquer")
    with pytest.raises(ValueError):
        criar_resumidor("magico", Configuracao())


def test_embeddings_falso_e_deterministico_e_normalizado():
    gerador = criar_gerador_embeddings("falso")
    a, b, c = gerador.gerar(["merenda escolar", "merenda escolar", "asfalto"])
    assert a == b
    assert a != c
    assert len(a) == gerador.dimensao == 384
    assert math.isclose(math.sqrt(sum(v * v for v in a)), 1.0, rel_tol=1e-9)


def test_resumo_extrativo_corta_em_palavra_inteira():
    resumidor = ResumidorExtrativo(max_caracteres=30)
    assert resumidor.resumir("Aquisição de merenda") == "Aquisição de merenda"
    resumo = resumidor.resumir("Aquisição de gêneros alimentícios para a merenda escolar")
    assert resumo.endswith("…")
    assert len(resumo) <= 31
    assert "alimentíc…" not in resumo


def test_resumidor_ollama_monta_a_chamada_certa():
    recebido = {}

    def responder(request: httpx.Request) -> httpx.Response:
        recebido.update(json.loads(request.content))
        return httpx.Response(200, json={"response": "  Compra de merenda.  "})

    http = httpx.Client(base_url="http://ollama:11434", transport=httpx.MockTransport(responder))
    resumidor = ResumidorOllama("http://ollama:11434", "qwen2.5:3b", http=http)
    assert resumidor.resumir("Aquisição de merenda escolar") == "Compra de merenda."
    assert recebido["model"] == "qwen2.5:3b"
    assert recebido["stream"] is False
    assert "Aquisição de merenda escolar" in recebido["prompt"]
