"""Integration tests against the real GitHub API.

Opt-in: run with `CLOSING_LABELS_INTEGRATION=1 uv run pytest -m integration`.
Skipped automatically otherwise so CI stays hermetic.

Fixture: PR #29 of williambdean/closing-labels closed issues #2 and #22,
labeled "enhancement" and "maintenance" respectively. Both issues have no
issue type set. See #61 for why a real-schema check matters.
"""

import os

import httpx
import pytest

from closing_labels.github import get_closing_labels

OWNER = "williambdean"
REPO = "closing-labels"
PR_NUMBER = 29
EXPECTED_LABELS = ["enhancement", "maintenance"]

pytestmark = pytest.mark.integration

requires_github = pytest.mark.skipif(
    os.environ.get("CLOSING_LABELS_INTEGRATION") != "1",
    reason="set CLOSING_LABELS_INTEGRATION=1 to run against the real GitHub API",
)


@pytest.fixture
def github_client():
    token = os.environ.get("GH_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    with httpx.Client(headers=headers) as client:
        yield client


@requires_github
def test_get_closing_labels_real_api(github_client):
    """The default query must work against the live schema (see #61)."""
    labels = get_closing_labels(
        github_client, OWNER, REPO, PR_NUMBER, include_issue_types=False
    )
    assert labels == EXPECTED_LABELS


@requires_github
def test_get_closing_labels_real_api_with_issue_types(github_client):
    """The issueType selection must also validate against the live schema."""
    labels = get_closing_labels(
        github_client, OWNER, REPO, PR_NUMBER, include_issue_types=True
    )
    # Both fixture issues have no issue type, so only labels are collected
    assert labels == EXPECTED_LABELS
