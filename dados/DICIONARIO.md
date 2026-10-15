# Dicionário de dados

Descreve cada coluna dos CSVs de `dados/csv/` (iguais às tabelas do schema `radar`).
O teste `tests/unit/test_dicionario.py` confere se nenhuma coluna ficou sem descrição.

Convenções:
- **Datas e horas** vêm do PNCP sem fuso; são horário de Brasília. No banco viram `timestamptz`.
- **Vazio no CSV** = valor ausente (`NULL` no banco).
- **Códigos** (`*_id`) apontam para as tabelas `dominio_*`.
- Fonte, recorte e tratamento de LGPD: veja [`ORIGEM.md`](ORIGEM.md).

## Tabelas

### `orgao`
Órgão ou entidade pública que compra (prefeitura, secretaria, autarquia...). Chave: `cnpj`.

| Coluna | Tipo no banco | Descrição |
|---|---|---|
| `cnpj` | char(14) | CNPJ do órgão, só dígitos. |
| `razao_social` | text | Nome oficial do órgão. |
| `esfera_id` | char(1) | Esfera de governo: F = federal, E = estadual, M = municipal, D = distrital, N = não informada. |
| `poder_id` | char(1) | Poder: E = executivo, L = legislativo, J = judiciário, N = não se aplica (ex.: consórcios, empresas públicas). |

### `unidade`
Unidade compradora dentro de um órgão (ex.: Secretaria de Saúde da prefeitura). Chave: (`cnpj_orgao`, `codigo_unidade`).

| Coluna | Tipo no banco | Descrição |
|---|---|---|
| `cnpj_orgao` | char(14) | Órgão dono da unidade (FK para `orgao`). |
| `codigo_unidade` | text | Código da unidade no sistema de origem. Só é único dentro do mesmo órgão. |
| `nome_unidade` | text | Nome da unidade compradora. |
| `uf_sigla` | char(2) | UF da unidade (é o filtro de UF do Radar). |
| `uf_nome` | text | Nome da UF por extenso. |
| `municipio_nome` | text | Município da unidade. |
| `codigo_ibge` | text | Código IBGE do município (7 dígitos): use para cruzar com outras bases públicas. |

### `contratacao`
Contratação publicada no PNCP: licitação, dispensa, credenciamento... Chave: `numero_controle_pncp`.

| Coluna | Tipo no banco | Descrição |
|---|---|---|
| `numero_controle_pncp` | text | Identificador único no PNCP: `CNPJ-1-SEQUENCIAL/ANO`. |
| `cnpj_orgao` | char(14) | Órgão que publicou (FK para `orgao`). |
| `codigo_unidade` | text | Unidade compradora (FK composta para `unidade`). |
| `ano_compra` | smallint | Ano da compra no PNCP. |
| `sequencial_compra` | integer | Número sequencial da compra no ano, por órgão. Junto com CNPJ e ano forma o link do edital. |
| `numero_compra` | text | Número da compra no sistema do órgão (formato livre). |
| `processo` | text | Número do processo administrativo (formato livre). Processos judiciais citados foram mascarados. |
| `modalidade_id` | smallint | Modalidade (FK para `dominio_modalidade`): pregão, dispensa, credenciamento... |
| `modo_disputa_id` | smallint | Modo de disputa (FK para `dominio_modo_disputa`): aberto, fechado... |
| `situacao_compra_id` | smallint | Situação (FK para `dominio_situacao_compra`): divulgada, suspensa, revogada... |
| `instrumento_convocatorio_id` | smallint | Tipo de documento que convoca (FK para `dominio_instrumento_convocatorio`): edital, aviso... |
| `amparo_legal_codigo` | integer | Base legal (FK para `dominio_amparo_legal`), ex.: Lei 14.133/2021, art. 75, II. |
| `srp` | boolean | `true` se for Sistema de Registro de Preços (gera ata, compra sob demanda). |
| `objeto_compra` | text | O que o órgão quer comprar ou contratar. Texto livre, **sem limpeza**. |
| `informacao_complementar` | text | Observações livres do órgão. Muitas vezes vazio ou com "-". |
| `valor_total_estimado` | numeric(18,2) | Valor estimado em reais. Atenção: há zeros (orçamento sigiloso ou não informado). |
| `valor_total_homologado` | numeric(18,2) | Valor homologado depois da disputa (vazio enquanto está aberta). |
| `data_publicacao_pncp` | timestamptz | Quando foi publicada no PNCP. |
| `data_abertura_proposta` | timestamptz | Início do prazo para propostas. |
| `data_encerramento_proposta` | timestamptz | Fim do prazo para propostas: define se está "aberta" no Radar. |
| `data_inclusao` | timestamptz | Quando o registro entrou no PNCP. |
| `data_atualizacao` | timestamptz | Última alteração da contratação: base da ingestão incremental. |
| `data_atualizacao_global` | timestamptz | Última alteração da contratação OU de algo ligado a ela (itens, arquivos). |
| `link_sistema_origem` | text | Link para o sistema onde a disputa acontece (Compras.gov.br, BLL, Licitanet...). |
| `link_processo_eletronico` | text | Link para o processo eletrônico, quando o órgão informa. |
| `justificativa_presencial` | text | Por que a disputa é presencial (exigido pela Lei 14.133/2021). |
| `usuario_nome` | text | Sistema que enviou os dados ao PNCP (ex.: "Compras.gov.br"). Não é uma pessoa. |

### `contratacao_item`
Itens de cada contratação: o que está sendo comprado, em que quantidade e por quanto. Chave: (`numero_controle_pncp`, `numero_item`).

| Coluna | Tipo no banco | Descrição |
|---|---|---|
| `numero_controle_pncp` | text | Contratação a que o item pertence (FK para `contratacao`). |
| `numero_item` | integer | Número do item dentro da contratação (1, 2, 3...). |
| `descricao` | text | TODO(estagiaria): #3 |
| `material_ou_servico` | char(1) | TODO(estagiaria): #3 |
| `quantidade` | numeric(20,6) | TODO(estagiaria): #3 |
| `unidade_medida` | text | TODO(estagiaria): #3 |
| `valor_unitario_estimado` | numeric(20,6) | TODO(estagiaria): #3 |
| `valor_total` | numeric(18,2) | TODO(estagiaria): #3 |
| `orcamento_sigiloso` | boolean | TODO(estagiaria): #3 |
| `criterio_julgamento_id` | smallint | TODO(estagiaria): #3 |
| `situacao_item_id` | smallint | TODO(estagiaria): #3 |
| `tipo_beneficio_id` | smallint | TODO(estagiaria): #3 |
| `categoria_item_id` | smallint | TODO(estagiaria): #3 |
| `tem_resultado` | boolean | TODO(estagiaria): #3 |
| `ncm_nbs_codigo` | text | TODO(estagiaria): #3 |
| `ncm_nbs_descricao` | text | TODO(estagiaria): #3 |
| `catalogo_codigo_item` | text | TODO(estagiaria): #3 |
| `informacao_complementar` | text | TODO(estagiaria): #3 |
| `data_inclusao` | timestamptz | TODO(estagiaria): #3 |
| `data_atualizacao` | timestamptz | TODO(estagiaria): #3 |

### `fornecedor`
Quem foi contratado. **LGPD:** pessoa física (PF) e estrangeira (PE) só aparecem com chave pseudônima. Chave: `chave`.

| Coluna | Tipo no banco | Descrição |
|---|---|---|
| `chave` | text | `PJ-<cnpj>` para empresas; `PF-<hash>` / `PE-<hash>` para pessoas (HMAC com segredo fora do git: não dá para voltar ao CPF). |
| `tipo_pessoa` | char(2) | PJ = pessoa jurídica, PF = pessoa física, PE = pessoa estrangeira. |
| `cnpj` | char(14) | CNPJ da empresa. Sempre vazio para PF/PE (regra garantida por constraint no banco). |
| `razao_social` | text | Nome da empresa. Sempre vazio para PF/PE. CPF dentro do nome (comum em MEI) foi mascarado. |
| `possivel_mei` | boolean | `true` quando a razão social tem o padrão de MEI (nome do dono): exige cuidado de LGPD. |

### `contrato`
Contrato (ou empenho) publicado no PNCP. Chave: `numero_controle_pncp`.

| Coluna | Tipo no banco | Descrição |
|---|---|---|
| `numero_controle_pncp` | text | Identificador único do contrato no PNCP: `CNPJ-2-SEQUENCIAL/ANO`. |
| `numero_controle_pncp_compra` | text | Contratação de origem. Referência lógica: a compra pode não estar no recorte carregado. |
| `numero_controle_pncp_ata` | text | Ata de registro de preços de origem, quando houver. |
| `cnpj_orgao` | char(14) | Órgão contratante (FK para `orgao`). |
| `codigo_unidade` | text | Unidade contratante (FK composta para `unidade`). |
| `ano_contrato` | smallint | Ano do contrato. |
| `sequencial_contrato` | integer | Sequencial do contrato no ano, por órgão. |
| `numero_contrato_empenho` | text | Número do contrato ou da nota de empenho no órgão. |
| `processo` | text | Número do processo administrativo. |
| `tipo_contrato_id` | smallint | Tipo (FK para `dominio_tipo_contrato`): contrato, empenho, carta contrato... |
| `categoria_processo_id` | smallint | Categoria (FK para `dominio_categoria_processo`): compras, obras, serviços... |
| `receita` | boolean | `true` se o contrato gera receita para o órgão (ex.: concessão). |
| `objeto_contrato` | text | O que foi contratado. Texto livre, sem limpeza; nomes de PF foram mascarados. |
| `informacao_complementar` | text | Observações livres. |
| `fornecedor_chave` | text | Fornecedor contratado (FK para `fornecedor`). |
| `subcontratado_chave` | text | Fornecedor subcontratado, quando houver (FK para `fornecedor`). |
| `valor_inicial` | numeric(18,2) | Valor na assinatura. |
| `valor_parcela` | numeric(18,2) | Valor de cada parcela. |
| `numero_parcelas` | integer | Quantidade de parcelas. |
| `valor_global` | numeric(18,2) | Valor total do contrato. |
| `valor_acumulado` | numeric(18,2) | Valor acumulado com aditivos (quando informado). |
| `data_assinatura` | date | Data de assinatura. |
| `data_vigencia_inicio` | date | Início da vigência. |
| `data_vigencia_fim` | date | Fim da vigência. |
| `data_publicacao_pncp` | timestamptz | Publicação no PNCP. **É esta data que o filtro da API usa**, não a de assinatura. |
| `data_atualizacao` | timestamptz | Última alteração do contrato. |
| `data_atualizacao_global` | timestamptz | Última alteração do contrato ou de algo ligado a ele. |
| `numero_retificacao` | integer | Quantas vezes o registro foi retificado. |
| `usuario_nome` | text | Sistema que enviou os dados ao PNCP. |

### Domínios (`dominio_*`)
Pares código/nome extraídos dos próprios dados (podem não ter todos os códigos oficiais do PNCP).
Todas têm `codigo` e `nome`; `dominio_amparo_legal` também tem `descricao`.

`dominio_modalidade`, `dominio_modo_disputa`, `dominio_situacao_compra`, `dominio_instrumento_convocatorio`,
`dominio_amparo_legal`, `dominio_criterio_julgamento`, `dominio_situacao_item`, `dominio_tipo_beneficio`,
`dominio_categoria_item`, `dominio_tipo_contrato`, `dominio_categoria_processo`.

## Pegadinhas conhecidas (qualidade de dados)

- `valor_total_estimado = 0` em contratações reais: orçamento sigiloso ou não informado. Não some zeros com valores reais sem pensar.
- Credenciamentos ficam "abertos" por meses ou anos (há casos de 2021 abertos até 2027).
- Textos chegam com espaços duplos, quebras de linha e caixa alta/baixa misturadas.
- O endpoint de itens devolve **só 10 itens** se a chamada não informar `tamanhoPagina`.
- O filtro de data de `/contratos` usa a data de **publicação**, não a de assinatura.
