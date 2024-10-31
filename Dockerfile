FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    jq \
    gh \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY get-closing-labels get-removed-labels entrypoint.sh /
RUN chmod +x /get-closing-labels /entrypoint.sh /get-removed-labels \
    && mv /get-closing-labels /usr/local/bin/get-closing-labels \
    && mv /get-removed-labels /usr/local/bin/get-removed-labels

CMD ["/entrypoint.sh"]
