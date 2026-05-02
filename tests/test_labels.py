import pytest

from closing_labels.labels import compute_labels


@pytest.mark.parametrize(
    "closing, removed, exclude, respect_unlabeled, expected",
    [
        # Basic: label from closing issue is applied
        (["bug"], [], [], True, ["bug"]),
        # Multiple labels
        (["bug", "enhancement"], [], [], True, ["bug", "enhancement"]),
        # Exclude filters a label
        (["bug", "wontfix"], [], ["wontfix"], True, ["bug"]),
        # Exclude filters all labels
        (["wontfix"], [], ["wontfix"], True, []),
        # Respect unlabeled: removed label is not re-added
        (["bug"], ["bug"], [], True, []),
        # Respect unlabeled: only removed label is subtracted
        (["bug", "enhancement"], ["bug"], [], True, ["enhancement"]),
        # Ignore unlabeled: removed label IS added back
        (["bug"], ["bug"], [], False, ["bug"]),
        # No closing issues
        ([], [], [], True, []),
        # Exclude and respect_unlabeled interact correctly
        (["bug", "wontfix"], ["bug"], ["wontfix"], True, []),
        # Result is sorted
        (["z-label", "a-label"], [], [], True, ["a-label", "z-label"]),
    ],
)
def test_compute_labels(closing, removed, exclude, respect_unlabeled, expected):
    assert compute_labels(closing, removed, exclude, respect_unlabeled) == expected
