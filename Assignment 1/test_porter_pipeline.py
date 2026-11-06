import random
from hospital_nlp.porter_wrap import porter_stem, measure
from hospital_nlp import noise, corpus_gen
from hospital_nlp.pipeline import process_record, analyse_token, SearchIndex
from hospital_nlp.tokenizer import tokenize


def test_porter_known_outputs():
    assert porter_stem("fractures") == "fractur"
    assert porter_stem("treated") == "treat"
    assert porter_stem("bleeding") == "bleed"
    assert porter_stem("infection") == "infect"
    assert porter_stem("nephrectomies") == "nephrectomi"          # under-stemming vs lemma nephrectomy


def test_measure_function():
    assert measure("tree")[0] == 0 and measure("trouble")[0] == 1 and measure("oaten")[0] == 2


def test_corpus_size_and_reproducibility():
    a = corpus_gen.generate(); b = corpus_gen.generate()
    assert [r["text"] for r in a] == [r["text"] for r in b]
    assert len(a) == 500 and sum(len(tokenize(r["text"])) for r in a) >= 25000
    assert {r["type"] for r in a} == set(corpus_gen.COUNTS)


def test_noise_examples_from_task12():
    c = noise.clean("PT-I234567 05/II/2026 Dis-charge: fractured femur.")["cleaned"]
    assert "PT-1234567" in c and "05/11/2026" in c and "Discharge" in c
    c2 = noise.clean("pt O12345? fever irun-dhuchu; paracetarnol 5OOmg kuduthen.")
    assert "paracetamol" in c2["cleaned"] and "500mg" in c2["cleaned"] and "irundhuchu" in c2["cleaned"]
    assert c2["corrections"], "every correction must be logged for auditability"


def test_weighted_edit_distance_prefers_ocr_confusions():
    assert noise.weighted_edit_distance("paracetarnol", "paracetamol") < 0.5
    assert noise.weighted_edit_distance("paracetaxol", "paracetamol") >= 1.0


def test_language_id_and_routing():
    L = noise.LanguageID()
    assert L.identify("patient")[0] == "en" and L.identify("irundhuchu")[0] == "ta-rom"
    assert analyse_token("kuduthen", use_lid=True)["source"] == "none"       # not forced through English rules
    assert analyse_token("fractured")["source"] == "fst"
    assert analyse_token("zorbitis")["source"] == "porter-fallback"


def test_pipeline_keeps_original_and_search_ranking():
    rec = process_record("PT-1234567 | 05/11/2026 | c/o fever x 3 days. BP 120/80 mmHg. Rx: PARACETAMOL 500 MG BD.")
    assert rec["original"].startswith("PT-1234567") and "2026-11-05" in rec["normalised"]
    idx = SearchIndex()
    idx.add("A", [analyse_token(t) for t in tokenize("fractures seen")])
    idx.add("B", [analyse_token(t) for t in tokenize("fracture seen")])
    r = idx.search("fractures", "fst")
    assert set(r) == {"A", "B"} and r["A"] > r["B"]           # exact surface outranks lemma-only match
    assert set(idx.search("fractures", "none")) == {"A"}
