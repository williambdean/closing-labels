FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    curl \
    jq \
    git \
    gh \
    && rm -rf /var/lib/apt/lists/*

COPY get-closing-labels get-removed-labels entrypoint.sh /
RUN chmod +x /get-closing-labels /entrypoint.sh /get-removed-labels
# Move get-closing-labels.sh to /usr/local/bin
RUN mv /get-closing-labels /usr/local/bin/get-closing-labels
RUN mv /get-removed-labels /usr/local/bin/get-removed-labels

CMD ["/entrypoint.sh"]
