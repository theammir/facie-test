FROM ghcr.io/astral-sh/uv:0.7.12-python3.13-alpine AS base

ADD . /app/backend
WORKDIR /app/backend

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN uv sync --locked

FROM base AS debug
CMD ["uv", "run", "fastapi", "dev", "--host", "0.0.0.0"]

FROM base AS release
CMD ["uv", "run", "fastapi", "run"]
