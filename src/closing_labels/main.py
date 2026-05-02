from __future__ import annotations

import os
import sys

import httpx

from closing_labels.github import add_labels_to_pr, get_closing_labels, get_removed_labels
from closing_labels.labels import compute_labels


def _log(message: str) -> None:
    print(message, file=sys.stderr)


def _get_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        print(f"Error: required environment variable {name} is not set.", file=sys.stderr)
        sys.exit(1)
    return value


def main() -> None:
    owner = _get_env("INPUT_OWNER")
    repo = _get_env("INPUT_REPO")
    pr_number = int(_get_env("INPUT_PR_NUMBER"))
    exclude_raw = os.environ.get("INPUT_EXCLUDE", "").strip()
    respect_unlabeled = os.environ.get("INPUT_RESPECT_UNLABELED", "true").strip().lower() == "true"
    dry_run = os.environ.get("INPUT_DRY_RUN", "false").strip().lower() == "true"
    token = _get_env("GH_TOKEN")

    exclude = [label.strip() for label in exclude_raw.split(",") if label.strip()]

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    with httpx.Client(headers=headers) as client:
        closing = get_closing_labels(client, owner, repo, pr_number)

        if not closing:
            _log("No closing labels found, exiting.")
            return

        removed = get_removed_labels(client, owner, repo, pr_number)

        _log(f"Closing labels: {closing}")
        _log(f"Removed labels: {removed}")
        _log(f"Exclude: {exclude}")
        _log(f"Respect unlabeled: {respect_unlabeled}")

        labels = compute_labels(closing, removed, exclude, respect_unlabeled)

        if not labels:
            _log("No labels to add.")
            return

        _log(f"Adding label(s): {labels}")

        if dry_run:
            _log("Dry run enabled, skipping adding labels.")
            return

        add_labels_to_pr(client, owner, repo, pr_number, labels)
