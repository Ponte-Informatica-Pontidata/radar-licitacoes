"""Entidades do Radar de Licitações.

São classes simples e imutáveis (frozen dataclasses). Elas não sabem nada de HTTP nem de SQL:
o Adapter da coleta cria estes objetos a partir do JSON do PNCP, e o Repository os grava no banco.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Codigo:
    """Par código/nome de uma tabela de domínio do PNCP (ex.: 6 / "Pregão - Eletrônico")."""

    codigo: int
    nome: str | None = None


@dataclass(frozen=True, slots=True)
class Orgao:
    cnpj: str
    razao_social: str
    esfera_id: str | None = None
    poder_id: str | None = None


@dataclass(frozen=True, slots=True)
class Unidade:
    cnpj_orgao: str
    codigo_unidade: str
    nome_unidade: str | None = None
    uf_sigla: str | None = None
    uf_nome: str | None = None
    municipio_nome: str | None = None
    codigo_ibge: str | None = None


@dataclass(frozen=True, slots=True)
class Contratacao:
    numero_controle_pncp: str
    orgao: Orgao
    unidade: Unidade
    ano_compra: int
    sequencial_compra: int
    modalidade: Codigo
    objeto_compra: str
    numero_compra: str | None = None
    processo: str | None = None
    modo_disputa: Codigo | None = None
    situacao_compra: Codigo | None = None
    instrumento_convocatorio: Codigo | None = None
    amparo_legal: Codigo | None = None
    srp: bool | None = None
    informacao_complementar: str | None = None
    valor_total_estimado: Decimal | None = None
    valor_total_homologado: Decimal | None = None
    data_publicacao_pncp: datetime | None = None
    data_abertura_proposta: datetime | None = None
    data_encerramento_proposta: datetime | None = None
    data_atualizacao: datetime | None = None
    link_sistema_origem: str | None = None

    @property
    def link_pncp(self) -> str:
        return link_pncp(self.orgao.cnpj, self.ano_compra, self.sequencial_compra)


@dataclass(frozen=True, slots=True)
class LicitacaoAberta:
    """Uma linha da listagem do app: já vem pronta para exibir."""

    numero_controle_pncp: str
    orgao: str
    municipio: str | None
    uf: str | None
    modalidade: str
    objeto: str
    valor_total_estimado: Decimal | None
    data_encerramento_proposta: datetime | None
    link_pncp: str


def link_pncp(cnpj: str, ano: int, sequencial: int) -> str:
    """Endereço da página pública do edital no portal do PNCP."""
    return f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{sequencial}"
