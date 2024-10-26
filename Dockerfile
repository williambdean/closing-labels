FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    curl \
    jq \
    git \
    gh \
    && rm -rf /var/lib/apt/lists/*

COPY get-closing-labels.sh get-removed-labels.sh entrypoint.sh /
RUN chmod +x /get-closing-labels.sh /entrypoint.sh /get-removed-labels.sh
# Move get-closing-labels.sh to /usr/local/bin
RUN mv /get-closing-labels.sh /usr/local/bin/get-closing-labels
RUN mv /get-removed-labels.sh /usr/local/bin/get-removed-labels

CMD ["/entrypoint.sh"]
