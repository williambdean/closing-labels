def compute_labels(
    closing: list[str],
    removed: list[str],
    exclude: list[str],
    respect_unlabeled: bool,
) -> list[str]:
    """Compute the final set of labels to apply to a pull request.

    Args:
        closing: Labels from issues closed by this PR.
        removed: Labels that were manually removed from this PR.
        exclude: Labels to never add.
        respect_unlabeled: If True, labels manually removed from the PR
            will not be re-added even if they appear on a closing issue.

    Returns:
        Sorted list of labels to apply.
    """
    result = set(closing)

    if respect_unlabeled:
        result -= set(removed)

    result -= set(exclude)

    return sorted(result)
