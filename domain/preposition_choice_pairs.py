"""Catalog of easily confused English preposition pairs for choice exercises."""

from typing import Iterable

# Canonical pairs (alphabetically sorted within each tuple).
SIMILAR_PREPOSITION_PAIRS: tuple[tuple[str, str], ...] = (
    ("across", "through"),
    ("along", "across"),
    ("at", "in"),
    ("at", "on"),
    ("behind", "beside"),
    ("between", "among"),
    ("during", "for"),
    ("for", "to"),
    ("in", "into"),
    ("over", "under"),
    ("since", "for"),
    ("to", "into"),
)


def pair_key(term_a: str, term_b: str) -> str:
    a, b = sorted((term_a.strip().lower(), term_b.strip().lower()))
    return f"{a}|{b}"


def normalize_pair(term_a: str, term_b: str) -> tuple[str, str]:
    return tuple(sorted((term_a.strip().lower(), term_b.strip().lower())))  # type: ignore[return-value]


def pairs_for_terms(available_terms: Iterable[str]) -> list[tuple[str, str]]:
    """Return catalog pairs where both prepositions exist in *available_terms*."""
    term_set = {t.strip().lower() for t in available_terms}
    return [
        pair
        for pair in SIMILAR_PREPOSITION_PAIRS
        if pair[0] in term_set and pair[1] in term_set
    ]
