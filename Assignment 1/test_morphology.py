import pytest
from hospital_nlp import morphology as m
from hospital_nlp.lexicon_data import INFLECTIONAL_AFFIXES, DERIVATIONAL_AFFIXES

# (lexical input, expected surface) from Task 8.4
CASES = [("treat +V +PROG", "treating"), ("admit +V +PAST", "admitted"), ("biopsy +N +PL", "biopsies"),
         ("rash +N +PL", "rashes"), ("play +V +3SG", "plays"), ("fracture +N +PL", "fractures"),
         ("lesion +N +PL", "lesions"), ("study +V +PAST", "studied"), ("stop +V +PROG", "stopping"),
         ("make +V +PROG", "making"), ("bleed +V +PAST", "bled"), ("go +V +PAST", "went"),
         ("have +V +3SG", "has"), ("see +V +PROG", "seeing"), ("visit +V +PAST", "visited"),
         ("open +V +PAST", "opened"), ("fix +N +PL", "fixes"), ("box +N +PL", "boxes"),
         ("kidney +N +PL", "kidneys"), ("nephrectomy +N +PL", "nephrectomies")]


@pytest.mark.parametrize("lex,surface", CASES)
def test_generation(lex, surface):
    assert m.generate_from_lexical(lex) == surface


@pytest.mark.parametrize("lex,surface", CASES)
def test_round_trip_analysis(lex, surface):
    lemma, pos, feat = lex.split()
    assert any(a.lemma == lemma and a.feat == feat for a in m.analyse(surface))


def test_hand_traced_analyses():
    assert "fracture +N +PL" in [str(a) for a in m.analyse("fractures")]
    assert any(str(a).startswith("treat +V +PAST") for a in m.analyse("treated"))
    assert any(str(a).startswith("bleed +V +PROG") for a in m.analyse("bleeding"))


def test_ambiguity_returns_all_analyses():
    feats = {a.feat for a in m.analyse("treated")}
    assert {"+PAST", "+PASTPART"} <= feats
    assert len(m.analyse("healing")) >= 2                    # noun reading + progressive verb
    assert len(m.analyse("fractures")) >= 2                  # +N +PL and +V +3SG


def test_irregulars():
    for surface, lemma in [("went", "go"), ("was", "be"), ("has", "have"), ("bled", "bleed"), ("children", "child")]:
        assert lemma in m.lemmas_for(surface)


def test_lexicon_meets_assignment_minimums():
    st = m.lexicon_stats()
    assert st["stems_incl_roots"] >= 300
    assert len(INFLECTIONAL_AFFIXES) >= 20 and len(DERIVATIONAL_AFFIXES) >= 15
    assert st["irregular_verbs"] + st["irregular_plurals"] > 0


def test_unknown_word_has_no_analysis():
    assert m.analyse("irundhuchu") == []
