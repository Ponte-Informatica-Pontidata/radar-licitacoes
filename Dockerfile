# syntax=docker/dockerfile:1.7
# Imagem de desenvolvimento do Radar de Licitações:
# Python 3.13 + uv + psql 17 + Supabase CLI (o mesmo `supabase db push` usado no CI e em produção).
FROM python:3.13.13-slim-bookworm

ARG SUPABASE_CLI_VERSION=2.121.0
ARG TARGETARCH

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:${PATH}" \
    TZ=America/Sao_Paulo

# psql 17 vem do repositório oficial do PostgreSQL (o Debian traz uma versão mais antiga)
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl gnupg git \
 && install -d /usr/share/postgresql-common/pgdg \
 && curl -fsSL -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc https://www.postgresql.org/media/keys/ACCC4CF8.asc \
 && echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" \
    > /etc/apt/sources.list.d/pgdg.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends postgresql-client-17 \
 && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL "https://github.com/supabase/cli/releases/download/v${SUPABASE_CLI_VERSION}/supabase_linux_${TARGETARCH:-amd64}.tar.gz" \
    | tar -xz -C /usr/local/bin supabase \
 && supabase --version

COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /uvx /usr/local/bin/

WORKDIR /workspace
# Dependências primeiro (camada em cache), depois o código
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-install-project
COPY . .
RUN uv sync --frozen

EXPOSE 8501
CMD ["bash"]
