"""Helpers for selecting easy or hard multiplication pairs and factor targets."""

from __future__ import annotations

import random
from typing import Iterable, Optional, Sequence, Tuple

Pair = Tuple[int, int]


def _pair_key(a: int, b: int) -> Pair:
    """Return a canonical (small, big) representation of the pair."""
    return tuple(sorted((a, b)))  # type: ignore[return-value]


def easy_pairs(limit: int = 10) -> set[Pair]:
    """Easy practice pairs, always ordered as (small, big)."""
    pairs: set[Pair] = set()

    for n in range(1, limit + 1):
        pairs.add(_pair_key(1, n))
        pairs.add(_pair_key(n, 10))

    for pair in ((2, 2), (2, 3), (2, 4), (2, 5), (3, 3)):
        if pair[0] <= limit and pair[1] <= limit:
            pairs.add(_pair_key(*pair))

    # Filter anything above the current practice limit (handles limit < 10)
    pairs = {pair for pair in pairs if pair[0] <= limit and pair[1] <= limit}
    return pairs


def hard_pairs(limit: int = 10) -> set[Pair]:
    """All remaining pairs (small, big) once easy combos are removed."""
    easy = easy_pairs(limit)
    all_pairs = {_pair_key(i, j) for i in range(1, limit + 1) for j in range(i, limit + 1)}
    return all_pairs - easy


def _shuffle_pair(pair: Pair, rng: random.Random | None = None) -> Pair:
    """Return the pair in a random order for presentation."""
    rng = rng or random
    a, b = pair
    if a == b or rng.random() < 0.5:
        return pair
    return b, a


def _factor_pairs(source: Iterable[Pair], limit: int) -> set[Pair]:
    """Filter pairs to those valid for factor questions (under 10, product >= 10)."""
    max_factor = min(limit, 9)
    return {
        pair
        for pair in source
        if pair[0] <= max_factor and pair[1] <= max_factor and pair[0] * pair[1] >= 10
    }


def _choose_from_pool(
    primary: Sequence[Pair], secondary: Sequence[Pair], fallback: Sequence[Pair], rng: random.Random
) -> Optional[Pair]:
    if primary:
        return rng.choice(primary)
    if secondary:
        return rng.choice(secondary)
    if fallback:
        return rng.choice(fallback)
    return None


def choose_pair(limit: int = 10, easy_probability: float = 0.10, rng: random.Random | None = None) -> Optional[Pair]:
    """Pick a multiplication pair, randomising orientation at presentation time."""
    rng = rng or random
    easy = sorted(easy_pairs(limit))
    hard = sorted(hard_pairs(limit))
    use_easy = rng.random() < easy_probability
    base = _choose_from_pool(easy if use_easy else hard, hard if use_easy else easy, easy + hard, rng)
    if base is None:
        return None
    return _shuffle_pair(base, rng)


def choose_factor_product(
    limit: int = 10, easy_probability: float = 0.10, rng: random.Random | None = None
) -> Optional[int]:
    """Pick a composite number to use for factor challenges."""
    rng = rng or random
    easy = sorted(_factor_pairs(easy_pairs(limit), limit))
    hard = sorted(_factor_pairs(hard_pairs(limit), limit))
    use_easy = rng.random() < easy_probability
    base = _choose_from_pool(easy if use_easy else hard, hard if use_easy else easy, easy + hard, rng)
    if base is None:
        return None
    return base[0] * base[1]


def easy_factors(limit: int = 10) -> set[int]:
    """Products considered 'easy' during factor practice."""
    return {a * b for a, b in _factor_pairs(easy_pairs(limit), limit)}


def hard_factors(limit: int = 10) -> set[int]:
    """Products reserved for harder factor challenges."""
    return {a * b for a, b in _factor_pairs(hard_pairs(limit), limit)}


def accepted_factor(value: int, limit: int = 10) -> bool:
    """Validate factor inputs: strictly between 1 and 10 and within range."""
    max_factor = min(limit, 9)
    return 1 < value < 10 and value <= max_factor
