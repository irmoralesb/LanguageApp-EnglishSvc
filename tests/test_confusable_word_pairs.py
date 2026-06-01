from domain.confusable_word_pairs import CONFUSABLE_WORD_PAIRS, pair_key, normalize_pair


def test_pair_key_is_order_independent():
    assert pair_key("Affect", "effect") == pair_key("effect", "Affect")


def test_normalize_pair_sorts():
    assert normalize_pair("tell", "say") == ("say", "tell")


def test_catalog_has_pairs():
    assert len(CONFUSABLE_WORD_PAIRS) >= 10
    for a, b in CONFUSABLE_WORD_PAIRS:
        assert a != b
        assert a.islower() and b.islower()
