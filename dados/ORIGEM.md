# Origem dos dados

## Fonte

API pública de consultas do **Portal Nacional de Contratações Públicas (PNCP)**:
`https://pncp.gov.br/api/consulta` (especificação em `https://pncp.gov.br/api/consulta/v3/api-docs`).
São dados públicos por força da Lei de Acesso à Informação (Lei 12.527/2011) e da Lei 14.133/2021.

## Recorte do snapshot

| Tabela | Endpoint | Recorte |
|---|---|---|
| `contratacao` | `GET /v1/contratacoes/proposta` | UF = MG, `dataFinal` = data de referência + 365 dias (todas com proposta aberta) |
| `contratacao_item` | `GET /api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}/itens` | itens de todas as contratações acima (`tamanhoPagina=500`) |
| `contrato` | `GET /v1/contratos` | publicados nos 30 dias anteriores à referência; UF filtrada **no cliente** (a API não tem filtro de UF) |
| `orgao`, `unidade`, `fornecedor`, `dominio_*` | derivados dos registros acima | — |

Data de referência, contagens exatas e hash de cada arquivo: [`MANIFESTO.json`](MANIFESTO.json).

Os dados foram extraídos pelo script `ferramentas/snapshot_pncp/snapshot_pncp.py` do repositório
[`laboratorio`](https://github.com/Ponte-Informatica-Pontidata/laboratorio). O script é reprodutível,
respeita o ritmo da API (que responde 429 a partir de ~20 chamadas por minuto) e retoma de onde parou.

## O que foi feito com os dados (e o que NÃO foi)

**Não foi feita limpeza.** Textos, valores e códigos estão como a API devolveu. Limpar é parte do trabalho.

**Foi feito tratamento de LGPD antes de gravar qualquer arquivo** (este repositório é público):

| Situação | Tratamento |
|---|---|
| Fornecedor pessoa física (PF) ou estrangeira (PE) | sem CPF/documento e sem nome; vira chave `PF-<hash>` (HMAC-SHA256 com segredo que não está no git) |
| CPF em qualquer texto livre (formatado, parcial `***.123.456-**` ou 11 dígitos com dígito verificador válido) | `[CPF REMOVIDO]` |
| CPF dentro da razão social de empresa (comum em MEI) | `[CPF REMOVIDO]` e `possivel_mei = true` |
| Número de processo judicial (padrão CNJ), comum em compra de medicamento por ordem judicial | `[PROCESSO JUDICIAL]` |
| Nome logo após "paciente", "requerente", "munícipe", "beneficiário", "Sr./Sra.", "em favor de" | `[NOME REMOVIDO]` |
| Nome de fornecedor PF citado em qualquer texto | `[PESSOA FÍSICA]` |

Uma varredura final bloqueia a gravação se sobrar qualquer CPF, processo judicial ou nome de PF conhecido.

**Limitações conhecidas** (viram tarefas de LGPD ao longo do laboratório):
- Nomes de pessoas em textos livres sem palavra-chave antes (ex.: servidores citados no objeto) podem existir.
- Razões sociais de MEI contêm o nome do empreendedor: estão marcadas com `possivel_mei` para análise.
- Compras de saúde para pacientes específicos podem permitir reidentificação indireta em municípios pequenos.

Se você encontrar um dado pessoal que escapou, **não copie o dado em issue, PR ou chat**: avise o tech lead
apontando só o arquivo e o número da linha.
