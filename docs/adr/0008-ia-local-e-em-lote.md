# 0008 — IA local (FastEmbed, Ollama) e em lote no GitHub Actions

- Status: aceito
- Data: 15/10/2026

## Contexto
Só ferramentas gratuitas. Em 2026 o Hugging Face retirou o crédito mensal de inferência das contas
gratuitas, então não há API hospedada grátis para embeddings ou LLM.

## Decisão
- Embeddings com **FastEmbed** (`paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensões, ~220 MB, CPU, sem torch).
  O mesmo modelo gera os vetores dos documentos (em lote) e o da consulta (no app).
- Resumos com **Ollama** local (ex.: `qwen2.5:3b`) e fallback extrativo sem IA.
- Processamento **em lote** no GitHub Actions (runners públicos: 4 vCPU, 16 GB, minutos ilimitados),
  só para registros novos ou alterados, com limite por execução.

## Alternativas consideradas
- APIs pagas de LLM/embeddings: fora da regra de custo zero.
- Gerar resumos sob demanda no app: lento no Streamlit Cloud e repetiria trabalho a cada visita.

## Consequências
- Cada resultado guarda `modelo` e `versao_prompt` (governança e comparação entre versões).
- O modelo de embedding lê no máximo 128 tokens: o texto de entrada precisa ser curto e limpo.
- A troca de provedor é configuração (`RADAR_EMBEDDINGS`, `RADAR_RESUMO`), graças à Strategy/Factory.
