# Both stages use the same ghcr.io image: it publishes the official Python
# 3.13 bookworm-slim runtime, so no pulls from Docker Hub are needed and the
# build is immune to Docker Hub rate limiting (HTTP 429) on hosted runners.
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY src/ ./src/
RUN uv sync --frozen --no-dev

# Prune the uv toolchain (uv/uvx, ~43MB) and other build-only content from a
# throwaway stage, then materialize the runtime from the pruned merged
# filesystem. Copying to a fresh stage re-creates the layers without the
# deleted content, instead of leaving whiteout stubs that keep the size.
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS pruned
RUN rm -f /usr/local/bin/uv /usr/local/bin/uvx \
  && rm -rf /usr/local/lib/python3.13/ensurepip \
  && rm -rf /usr/local/lib/python3.13/site-packages/*

FROM scratch AS runtime
COPY --from=pruned / /
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

ENV PATH="/app/.venv/bin:$PATH"

CMD ["closing-labels"]
