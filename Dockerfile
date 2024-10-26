FROM ubuntu:latest

COPY get-closing-labels.sh entrypoint.sh /

RUN apt-get update && apt-get install -y \
    curl \
    jq \
    git \
    gh \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/entrypoint.sh"]
