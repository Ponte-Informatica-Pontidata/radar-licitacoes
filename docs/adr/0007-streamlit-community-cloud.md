# 0007 — Streamlit Community Cloud (e não Vercel) para o app

- Status: aceito
- Data: 15/10/2026

## Contexto
O app precisa ser publicado de graça para as reviews de sprint, e a estagiária deve continuar no Python.
Foram consideradas Vercel e Supabase (sugestão inicial do tech lead) e alternativas.

## Decisão
App em **Streamlit**, publicado no **Streamlit Community Cloud** a partir da `main` deste repositório
público. O banco de produção fica no Supabase.

## Alternativas consideradas
- **Vercel:** ótima para front-end JavaScript, mas não roda Streamlit (conexão websocket de longa duração),
  e as funções serverless não comportam o modelo de embedding da busca. Exigiria um front-end Next.js
  separado, fora do foco do estágio.
- **Hugging Face Spaces:** desde 2026 a criação de Spaces Gradio/Docker exige plano pago.
- **Netlify:** mesmo problema da Vercel.

## Consequências
- Deploy automático a cada merge na `main`; segredos no painel do Streamlit.
- O app dorme após 12 h sem acesso (acorda no primeiro clique) e tem de 690 MB a 2,7 GB de RAM.
- Um portal Next.js na Vercel fica como desafio opcional na fase 4.
