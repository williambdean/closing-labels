from __future__ import annotations

import httpx

GRAPHQL_URL = "https://api.github.com/graphql"

CLOSING_LABELS_QUERY = """
query($endCursor: String, $owner: String!, $name: String!, $number: Int!) {
    repository(owner: $owner, name: $name) {
        pullRequest(number: $number) {
            closingIssuesReferences(first: 10, after: $endCursor) {
                nodes {
                    labels(first: 10) {
                        nodes {
                            name
                        }
                    }
                }
                pageInfo {
                    endCursor
                    hasNextPage
                }
            }
        }
    }
}
"""

REMOVED_LABELS_QUERY = """
query($endCursor: String, $owner: String!, $name: String!, $number: Int!) {
    repository(owner: $owner, name: $name) {
        pullRequest(number: $number) {
            timelineItems(first: 25, after: $endCursor) {
                nodes {
                    __typename
                    ... on UnlabeledEvent {
                        label {
                            name
                        }
                    }
                }
                pageInfo {
                    endCursor
                    hasNextPage
                }
            }
        }
    }
}
"""


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
        response = client.post(
            GRAPHQL_URL,
            json={
                "query": CLOSING_LABELS_QUERY,
                "variables": {
                    "owner": owner,
                    "name": repo,
                    "number": pr_number,
                    "endCursor": cursor,
                },
            },
        )
        response.raise_for_status()
        data = response.json()

        closing = data["data"]["repository"]["pullRequest"]["closingIssuesReferences"]
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
        response = client.post(
            GRAPHQL_URL,
            json={
                "query": REMOVED_LABELS_QUERY,
                "variables": {
                    "owner": owner,
                    "name": repo,
                    "number": pr_number,
                    "endCursor": cursor,
                },
            },
        )
        response.raise_for_status()
        data = response.json()

        timeline = data["data"]["repository"]["pullRequest"]["timelineItems"]
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
