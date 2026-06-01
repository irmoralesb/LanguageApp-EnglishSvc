"""Catalog of easily confused English word pairs for choice exercises."""

from typing import Iterable

CONFUSABLE_WORD_PAIRS: tuple[tuple[str, str], ...] = (
    ("affect", "effect"),
    ("borrow", "lend"),
    ("bring", "take"),
    ("say", "tell"),
    ("hear", "listen"),
    ("look", "see"),
    ("lay", "lie"),
    ("rise", "raise"),
    ("win", "beat"),
    ("job", "work"),
    ("house", "home"),
    ("trip", "travel"),
    ("fun", "funny"),
    ("historic", "historical"),
    ("sensible", "sensitive"),
)


def pair_key(term_a: str, term_b: str) -> str:
    a, b = sorted((term_a.strip().lower(), term_b.strip().lower()))
    return f"{a}|{b}"


def normalize_pair(term_a: str, term_b: str) -> tuple[str, str]:
    return tuple(sorted((term_a.strip().lower(), term_b.strip().lower())))  # type: ignore[return-value]
