import json

import pytest
from pytest_httpx import HTTPXMock

from closing_labels.main import main

GRAPHQL_URL = "https://api.github.com/graphql"
LABELS_URL = "https://api.github.com/repos/williambdean/closing-labels/issues/42/labels"

BASE_ENV = {
    "INPUT_OWNER": "williambdean",
    "INPUT_REPO": "closing-labels",
    "INPUT_PR_NUMBER": "42",
    "INPUT_EXCLUDE": "",
    "INPUT_RESPECT_UNLABELED": "true",
    "INPUT_DRY_RUN": "false",
    "GH_TOKEN": "test-token",
}


def closing_labels_response(labels: list[str], has_next: bool = False):
    return {
        "data": {
            "repository": {
                "pullRequest": {
                    "closingIssuesReferences": {
                        "nodes": [
                            {"labels": {"nodes": [{"name": label} for label in labels]}}
                        ],
                        "pageInfo": {"hasNextPage": has_next, "endCursor": None},
                    }
                }
            }
        }
    }


def removed_labels_response(labels: list[str]):
    return {
        "data": {
            "repository": {
                "pullRequest": {
                    "timelineItems": {
                        "nodes": [
                            {"__typename": "UnlabeledEvent", "label": {"name": label}}
                            for label in labels
                        ],
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    }
                }
            }
        }
    }


def no_closing_issues_response():
    return {
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
    }


# ---------------------------------------------------------------------------
# end-to-end main() tests
# ---------------------------------------------------------------------------


def test_main_adds_labels(httpx_mock: HTTPXMock, monkeypatch):
    for key, value in BASE_ENV.items():
        monkeypatch.setenv(key, value)

    httpx_mock.add_response(url=GRAPHQL_URL, json=closing_labels_response(["bug"]))
    httpx_mock.add_response(url=GRAPHQL_URL, json=removed_labels_response([]))
    httpx_mock.add_response(url=LABELS_URL, status_code=200, json=[])

    main()

    requests = httpx_mock.get_requests()
    rest_request = requests[-1]
    assert rest_request.method == "POST"
    assert json.loads(rest_request.content) == {"labels": ["bug"]}


def test_main_no_closing_issues_exits_early(httpx_mock: HTTPXMock, monkeypatch):
    for key, value in BASE_ENV.items():
        monkeypatch.setenv(key, value)

    httpx_mock.add_response(url=GRAPHQL_URL, json=no_closing_issues_response())

    main()

    # Only one request made — no removed labels query, no REST call
    assert len(httpx_mock.get_requests()) == 1


def test_main_dry_run_skips_rest_call(httpx_mock: HTTPXMock, monkeypatch):
    for key, value in {**BASE_ENV, "INPUT_DRY_RUN": "true"}.items():
        monkeypatch.setenv(key, value)

    httpx_mock.add_response(url=GRAPHQL_URL, json=closing_labels_response(["bug"]))
    httpx_mock.add_response(url=GRAPHQL_URL, json=removed_labels_response([]))

    main()

    # Two GraphQL requests but no REST POST
    requests = httpx_mock.get_requests()
    assert len(requests) == 2
    assert all(r.url == GRAPHQL_URL for r in requests)


def test_main_exclude_filters_label(httpx_mock: HTTPXMock, monkeypatch):
    for key, value in {**BASE_ENV, "INPUT_EXCLUDE": "wontfix"}.items():
        monkeypatch.setenv(key, value)

    httpx_mock.add_response(
        url=GRAPHQL_URL, json=closing_labels_response(["bug", "wontfix"])
    )
    httpx_mock.add_response(url=GRAPHQL_URL, json=removed_labels_response([]))
    httpx_mock.add_response(url=LABELS_URL, status_code=200, json=[])

    main()

    rest_request = httpx_mock.get_requests()[-1]
    assert json.loads(rest_request.content) == {"labels": ["bug"]}


def test_main_respect_unlabeled_removes_label(httpx_mock: HTTPXMock, monkeypatch):
    for key, value in BASE_ENV.items():
        monkeypatch.setenv(key, value)

    httpx_mock.add_response(url=GRAPHQL_URL, json=closing_labels_response(["bug"]))
    httpx_mock.add_response(url=GRAPHQL_URL, json=removed_labels_response(["bug"]))

    main()

    # No labels left after subtraction — no REST call made
    assert len(httpx_mock.get_requests()) == 2


def test_main_missing_token_exits(monkeypatch):
    for key, value in BASE_ENV.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("GH_TOKEN")

    with pytest.raises(SystemExit):
        main()
