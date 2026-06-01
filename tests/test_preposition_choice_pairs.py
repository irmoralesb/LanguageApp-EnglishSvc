from domain.preposition_choice_pairs import pair_key, pairs_for_terms, normalize_pair


def test_pairs_for_terms_filters_catalog() -> None:
    eligible = pairs_for_terms(["in", "into", "on"])
    assert ("in", "into") in eligible
    assert all("on" in p for p in eligible if p[0] == "on" or p[1] == "on")


def test_pair_key_is_order_independent() -> None:
    assert pair_key("into", "in") == pair_key("in", "into")


def test_normalize_pair_sorts_terms() -> None:
    assert normalize_pair("into", "in") == ("in", "into")
