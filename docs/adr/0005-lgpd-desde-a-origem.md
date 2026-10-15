# 0005 — LGPD aplicada antes de gravar, com trava no banco

- Status: aceito
- Data: 15/10/2026

## Contexto
A API do PNCP devolve CPF e nome de fornecedores pessoa física. Textos livres citam pacientes, processos
judiciais (que levam a dados de saúde, sensíveis pelo art. 11) e CPFs. O repositório é público.

## Decisão
- Minimização: o Radar não precisa saber **quem** é a pessoa física, só distinguir fornecedores.
- PF/PE viram chave pseudônima (`HMAC-SHA256` com segredo fora do git); documento e nome são descartados.
- Textos: CPF, processo judicial (CNJ) e nomes após palavras-chave ("paciente", "Sra.", "em favor de")
  são mascarados.
- Constraint no banco (`fornecedor_lgpd_pf_sem_identificacao`) recusa PF/PE com documento ou nome.
- O snapshot só é gravado se uma varredura final não encontrar nada.

## Alternativas consideradas
- Hash simples do CPF: reversível por força bruta (são só 10⁹ CPFs base). Não é anonimização.
- Descartar todos os contratos de PF: perde a análise de mercado sem ganho de privacidade.

## Consequências
- O pipeline (Sprint 6) precisa reproduzir este tratamento: é uma tarefa explícita, com teste.
- Limitações conhecidas (nomes sem palavra-chave, MEI, reidentificação indireta) estão em `dados/ORIGEM.md`.
