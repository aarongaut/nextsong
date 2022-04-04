"""Implementation of sample subpackage"""

__all__ = ["weighted_choice", "sublist"]

import random


def weighted_choice(weights):
    if any(w < 0 for w in weights):
        raise ValueError("weights must be nonnegative")
    if all(w == 0 for w in weights):
        raise ValueError("at least one weight must be positive")
    total_weight = sum(weights)
    normed_weights = [weight / total_weight for weight in weights]
    running_total = 0
    cumulative_weights = []
    for weight in normed_weights:
        running_total += weight
        cumulative_weights.append(running_total)
    # Ensure the final total is 1 regardless of precision issues
    cumulative_weights[-1] = 1
    threshold = random.random()
    # Choose the first item whose cumulative normalized weight exceeds
    # the random number
    for i, weight in enumerate(cumulative_weights):
        if weight > threshold:
            return i
    raise RuntimeError("Unexpected logic error")


def sublist(items, count, weights=None):
    """Extracts a sublist containing count entries from items

    Parameters
    ----------
    items: List[Any]
        The list of items to be sampled from.
    count: int
        The number of entries from items to be returned.
    weights: List[float]
        A list with equal length to items. Indicates the relative
        likelyhood of the item being used in the sample. An item
        with zero weight is never included, even it means not reaching
        count entries. If not given, all items have equal weight.

    """
    items = list(items)
    if not items:
        return []

    if not weights:
        weights = [1] * len(items)
    weights = list(weights)

    if len(items) != len(weights):
        raise ValueError("Length mismatch between items and weights")

    candidates = [
        (i, item, weight)
        for i, (item, weight) in enumerate(zip(items, weights))
        if weight > 0
    ]
    choices = []

    while candidates and len(choices) < count:
        weights = [weight for _, _, weight in candidates]
        i = weighted_choice(weights)
        choices.append(candidates.pop(i))

    return [item for _, item, _ in sorted(choices)]
