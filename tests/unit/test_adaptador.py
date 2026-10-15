from __future__ import annotations

from decimal import Decimal

from radar.coleta.adaptador_pncp import AdaptadorPncp, para_data, para_decimal


def test_converte_todas_as_contratacoes_reais(contratacoes_api):
    contratacoes = [AdaptadorPncp().contratacao(bruto) for bruto in contratacoes_api]
    assert len(contratacoes) == 3
    assert {c.unidade.uf_sigla for c in contratacoes} == {"MG"}


def test_campos_principais(contratacoes_api):
    bruto = contratacoes_api[1]
    c = AdaptadorPncp().contratacao(bruto)
    assert c.numero_controle_pncp == bruto["numeroControlePNCP"]
    assert c.orgao.cnpj == bruto["orgaoEntidade"]["cnpj"]
    assert c.unidade.codigo_unidade == str(bruto["unidadeOrgao"]["codigoUnidade"])
    assert c.modalidade.codigo == bruto["modalidadeId"]
    assert c.modalidade.nome == bruto["modalidadeNome"]
    assert isinstance(c.valor_total_estimado, Decimal)
    assert c.link_pncp == (
        f"https://pncp.gov.br/app/editais/{bruto['orgaoEntidade']['cnpj']}/{bruto['anoCompra']}/{bruto['sequencialCompra']}"
    )


def test_datas_do_pncp_sao_horario_de_brasilia():
    data = para_data("2026-10-15T08:59:00")
    assert data is not None
    assert data.utcoffset().total_seconds() == -3 * 3600
    assert para_data(None) is None
    assert para_data("") is None


def test_decimal_sem_imprecisao_de_float():
    assert para_decimal(0.1) == Decimal("0.1")
    assert para_decimal(2820297.8) == Decimal("2820297.8")
    assert para_decimal(None) is None
