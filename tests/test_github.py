import json

import httpx
import pytest
from pytest_httpx import HTTPXMock

from closing_labels.github import (
    add_labels_to_pr,
    get_closing_labels,
    get_removed_labels,
)

OWNER = "williambdean"
REPO = "closing-labels"
PR_NUMBER = 1
GRAPHQL_URL = "https://api.github.com/graphql"
LABELS_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/issues/{PR_NUMBER}/labels"


def make_client() -> httpx.Client:
    return httpx.Client(headers={"Authorization": "Bearer test-token"})


# ---------------------------------------------------------------------------
# get_closing_labels
# ---------------------------------------------------------------------------


def test_get_closing_labels_single_page(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url=GRAPHQL_URL,
        json={
            "data": {
                "repository": {
                    "pullRequest": {
                        "closingIssuesReferences": {
                            "nodes": [
                                {
                                    "labels": {
                                        "nodes": [
                                            {"name": "bug"},
                                            {"name": "enhancement"},
                                        ]
                                    }
                                },
                                {"labels": {"nodes": [{"name": "bug"}]}},
                            ],
                            "pageInfo": {"hasNextPage": False, "endCursor": None},
                        }
                    }
                }
            }
        },
    )

    with make_client() as client:
        labels = get_closing_labels(client, OWNER, REPO, PR_NUMBER)

    assert labels == ["bug", "enhancement"]


def test_get_closing_labels_no_closing_issues(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url=GRAPHQL_URL,
        json={
            "data": {
                "repository": {
                    "pullRequest": {
                        "closingIssuesReferences": {
                            "nodes": [],
                            "pageInfo": {"hasNextPage": False, "endCursor": None},
                        }
                    }
                }
            }
        },
    )

    with make_client() as client:
        labels = get_closing_labels(client, OWNER, REPO, PR_NUMBER)

    assert labels == []


def test_get_closing_labels_paginated(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url=GRAPHQL_URL,
        json={
            "data": {
                "repository": {
                    "pullRequest": {
                        "closingIssuesReferences": {
                            "nodes": [{"labels": {"nodes": [{"name": "bug"}]}}],
                            "pageInfo": {"hasNextPage": True, "endCursor": "cursor-1"},
                        }
                    }
                }
            }
        },
    )
    httpx_mock.add_response(
        url=GRAPHQL_URL,
        json={
            "data": {
                "repository": {
                    "pullRequest": {
                        "closingIssuesReferences": {
                            "nodes": [{"labels": {"nodes": [{"name": "enhancement"}]}}],
                            "pageInfo": {"hasNextPage": False, "endCursor": None},
                        }
                    }
                }
            }
        },
    )

    with make_client() as client:
        labels = get_closing_labels(client, OWNER, REPO, PR_NUMBER)

    assert labels == ["bug", "enhancement"]


# ---------------------------------------------------------------------------
# get_removed_labels
# ---------------------------------------------------------------------------


def test_get_removed_labels_single_page(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url=GRAPHQL_URL,
        json={
            "data": {
                "repository": {
                    "pullRequest": {
                        "timelineItems": {
                            "nodes": [
                                {
                                    "__typename": "UnlabeledEvent",
                                    "label": {"name": "bug"},
                                },
                                {"__typename": "LabeledEvent"},
                                {
                                    "__typename": "UnlabeledEvent",
                                    "label": {"name": "bug"},
                                },
                            ],
                            "pageInfo": {"hasNextPage": False, "endCursor": None},
                        }
                    }
                }
            }
        },
    )

    with make_client() as client:
        labels = get_removed_labels(client, OWNER, REPO, PR_NUMBER)

    assert labels == ["bug"]


def test_get_removed_labels_none(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url=GRAPHQL_URL,
        json={
            "data": {
                "repository": {
                    "pullRequest": {
                        "timelineItems": {
                            "nodes": [],
                            "pageInfo": {"hasNextPage": False, "endCursor": None},
                        }
                    }
                }
            }
        },
    )

    with make_client() as client:
        labels = get_removed_labels(client, OWNER, REPO, PR_NUMBER)

    assert labels == []


# ---------------------------------------------------------------------------
# add_labels_to_pr
# ---------------------------------------------------------------------------


def test_add_labels_to_pr(httpx_mock: HTTPXMock):
    httpx_mock.add_response(url=LABELS_URL, status_code=200, json=[])

    with make_client() as client:
        add_labels_to_pr(client, OWNER, REPO, PR_NUMBER, ["bug", "enhancement"])

    requests = httpx_mock.get_requests()
    assert len(requests) == 1
    assert requests[0].method == "POST"
    body = json.loads(requests[0].content)
    assert body["labels"] == ["bug", "enhancement"]


def test_add_labels_raises_on_error(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url=LABELS_URL, status_code=404, json={"message": "Not Found"}
    )

    with make_client() as client:
        with pytest.raises(httpx.HTTPStatusError):
            add_labels_to_pr(client, OWNER, REPO, PR_NUMBER, ["bug"])


# ---------------------------------------------------------------------------
# GraphQL error handling
# ---------------------------------------------------------------------------


def test_graphql_error_raises_runtime_error(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url=GRAPHQL_URL,
        json={"errors": [{"message": "Could not resolve to a Repository"}]},
    )

    with make_client() as client:
        with pytest.raises(RuntimeError, match="GitHub GraphQL error"):
            get_closing_labels(client, OWNER, REPO, PR_NUMBER)
