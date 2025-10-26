FROM ubuntu:latest

ARG GH_VERSION=2.82.1
RUN apt-get update && apt-get install -y \
    jq \
    ca-certificates \
    curl \
    && curl -sSL "https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_amd64.tar.gz" -o gh.tar.gz \
    && tar -xvf gh.tar.gz \
    && cp gh_${GH_VERSION}_linux_amd64/bin/gh /usr/local/bin/ \
    && rm -rf gh.tar.gz gh_${GH_VERSION}_linux_amd64 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY get-closing-labels get-removed-labels entrypoint.sh /
RUN chmod +x /get-closing-labels /entrypoint.sh /get-removed-labels \
    && mv /get-closing-labels /usr/local/bin/get-closing-labels \
    && mv /get-removed-labels /usr/local/bin/get-removed-labels

CMD ["/entrypoint.sh"]
