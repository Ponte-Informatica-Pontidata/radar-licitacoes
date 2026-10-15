"""Perfil de qualidade de dados: o primeiro diagnóstico de qualquer base nova.

Uso típico (depois da carga do banco):

    import pandas as pd
    from radar.persistencia.conexao import conectar
    from radar.tratamento.qualidade import perfil_qualidade

    with conectar() as conn:
        df = pd.read_sql("select * from radar.contratacao", conn)
    print(perfil_qualidade(df).to_markdown(index=False))
"""

from __future__ import annotations

import pandas as pd

COLUNAS_PERFIL = ["coluna", "tipo", "linhas", "nulos", "pct_nulos", "distintos", "pct_distintos", "exemplo"]


def perfil_qualidade(df: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por coluna de `df`, na mesma ordem das colunas, com as métricas de qualidade.

    Colunas do resultado (exatamente nesta ordem — ver COLUNAS_PERFIL):
      coluna         nome da coluna
      tipo           dtype do pandas como texto (ex.: "int64", "object")
      linhas         total de linhas do df
      nulos          valores ausentes (None/NaN/NaT). Texto vazio ou só com espaços TAMBÉM conta como nulo
      pct_nulos      nulos / linhas * 100, arredondado com 2 casas (0.0 se o df estiver vazio)
      distintos      quantidade de valores distintos entre os NÃO nulos
      pct_distintos  distintos / (linhas - nulos) * 100, com 2 casas (0.0 se não houver não nulos)
      exemplo        o valor não nulo mais frequente, convertido para str (None se a coluna for toda nula)

    Dica de leitura do resultado: pct_nulos alto = coluna pouco preenchida; pct_distintos = 100 numa
    coluna que deveria repetir (ex.: modalidade) = algo estranho; pct_distintos baixo numa coluna que
    deveria ser única (ex.: identificador) = duplicidade.
    """
    # TODO(estagiaria): #6 implementar o perfil seguindo a docstring (os testes são a especificação)
    raise NotImplementedError("TODO(estagiaria): #6 perfil_qualidade")
