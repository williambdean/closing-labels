from __future__ import annotations

import importlib.resources

import httpx

GRAPHQL_URL = "https://api.github.com/graphql"

_queries = importlib.resources.files("closing_labels.queries")
CLOSING_LABELS_QUERY = (_queries / "closing_labels.graphql").read_text()
REMOVED_LABELS_QUERY = (_queries / "removed_labels.graphql").read_text()


def _graphql(client: httpx.Client, query: str, variables: dict) -> dict:
    """Execute a GraphQL query and return the data payload.

    Raises RuntimeError for GraphQL-level errors (which GitHub returns as
    HTTP 200 with an 'errors' key rather than a 4xx status).
    """
    response = client.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables},
    )
    response.raise_for_status()
    payload = response.json()
    if "errors" in payload:
        raise RuntimeError(f"GitHub GraphQL error: {payload['errors']}")
    return payload["data"]


def get_closing_labels(
    client: httpx.Client,
    owner: str,
    repo: str,
    pr_number: int,
) -> list[str]:
    """Return deduplicated labels from all issues closed by this PR."""
    labels: set[str] = set()
    cursor: str | None = None

    while True:
        data = _graphql(
            client,
            CLOSING_LABELS_QUERY,
            {"owner": owner, "name": repo, "number": pr_number, "endCursor": cursor},
        )
        closing = data["repository"]["pullRequest"]["closingIssuesReferences"]
        for issue in closing["nodes"]:
            for label in issue["labels"]["nodes"]:
                labels.add(label["name"])

        page_info = closing["pageInfo"]
        if not page_info["hasNextPage"]:
            break
        cursor = page_info["endCursor"]

    return sorted(labels)


def get_removed_labels(
    client: httpx.Client,
    owner: str,
    repo: str,
    pr_number: int,
) -> list[str]:
    """Return deduplicated labels that were manually removed from this PR."""
    labels: set[str] = set()
    cursor: str | None = None

    while True:
        data = _graphql(
            client,
            REMOVED_LABELS_QUERY,
            {"owner": owner, "name": repo, "number": pr_number, "endCursor": cursor},
        )
        timeline = data["repository"]["pullRequest"]["timelineItems"]
        for node in timeline["nodes"]:
            if node["__typename"] == "UnlabeledEvent":
                labels.add(node["label"]["name"])

        page_info = timeline["pageInfo"]
        if not page_info["hasNextPage"]:
            break
        cursor = page_info["endCursor"]

    return sorted(labels)


def add_labels_to_pr(
    client: httpx.Client,
    owner: str,
    repo: str,
    pr_number: int,
    labels: list[str],
) -> None:
    """Add labels to a pull request via the REST API."""
    response = client.post(
        f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/labels",
        json={"labels": labels},
    )
    response.raise_for_status()
