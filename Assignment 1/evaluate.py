"""Measured experiments for the report (Tasks 2.5, 5.5, 9, 10, 12).  Nothing here is illustrative:
every figure is computed from the generated corpus and saved to results/.
"""
import csv
import json
import os
import random
import re
import time
from collections import Counter, defaultdict
from . import corpus_gen, morphology as morph, noise
from .patterns import PRIORITY, recognise_entities
from .pipeline import SearchIndex, analyse_token, process_record
from .porter_wrap import porter_stem
from .tokenizer import tokenize


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    return round(p, 4), round(r, 4), round(2 * p * r / (p + r), 4) if p + r else 0.0


def entity_eval(records, texts=None):
    tp, fp, fn = Counter(), Counter(), Counter()
    errors = []
    for i, r in enumerate(records):
        text = texts[i] if texts else r["text"]
        pred = Counter((t, s) for t, _, _, s in recognise_entities(text))
        gold = Counter((t, s) for t, s in r["gold_entities"])
        for k in set(pred) | set(gold):
            m = min(pred[k], gold[k])
            tp[k[0]] += m
            if pred[k] > m:
                fp[k[0]] += pred[k] - m; errors.append((r["id"], "FP", k[0], k[1]))
            if gold[k] > m:
                fn[k[0]] += gold[k] - m; errors.append((r["id"], "FN", k[0], k[1]))
    rows = {t: dict(zip(("precision", "recall", "f1"), prf(tp[t], fp[t], fn[t])), TP=tp[t], FP=fp[t], FN=fn[t])
            for t in PRIORITY}
    return rows, errors


def stemming_study(forms):
    """Porter vs FST lemma agreement + over/under-stemming measured over generated paradigms."""
    rows, agree = [], 0
    for f in forms:
        lem = sorted(morph.lemmas_for(f))
        st = porter_stem(f)
        ok = st in lem or (len(lem) > 0 and any(st == l for l in lem))
        agree += ok
        rows.append((f, st, "|".join(lem), int(ok)))
    stem2lem = defaultdict(set); lem2stem = defaultdict(set)
    for f in morph.all_surface_forms():
        st = porter_stem(f)
        for l in morph.lemmas_for(f):
            stem2lem[st].add(l); lem2stem[l].add(st)
    over = sum(1 for v in stem2lem.values() if len(v) > 1) / len(stem2lem)
    under = sum(1 for v in lem2stem.values() if len(v) > 1) / len(lem2stem)
    return rows, agree / len(forms), over, under


def retrieval_eval(records, n_queries=40, seed=7):
    """Retrieval P/R/F1 for none / porter / fst. Relevance = lemma concept inserted by the generator."""
    rng = random.Random(seed)
    idx = SearchIndex()
    for r in records:
        idx.add(r["id"], [analyse_token(t) for t in tokenize(r["text"])])
    rel = defaultdict(set)
    for r in records:
        for c in r["gold_concepts"]:
            rel[c].add(r["id"])
    # keep only concepts for which every document containing ANY form is gold-relevant (fair judgements)
    fair = []
    for c, docs in rel.items():
        pos = {x for x in morph.ENTRIES if x == c}
        forms = {s for s, an in morph._TABLE.items() if any(a.lemma == c for a in an)}
        containing = {r["id"] for r in records if forms & {t.lower() for t in tokenize(r["text"])}}
        if len(docs) >= 5 and containing == docs:
            fair.append(c)
    rng.shuffle(fair)
    queries = []
    for c in fair[:n_queries]:
        forms = sorted(s for s, an in morph._TABLE.items() if any(a.lemma == c for a in an) and s != c) or [c]
        queries.append((c, rng.choice(forms)))
    out, per_query = {}, []
    for mode in ("none", "porter", "fst"):
        tp = fp = fn = 0
        for c, q in queries:
            got = set(idx.search(q, mode)); gold = rel[c]
            tp += len(got & gold); fp += len(got - gold); fn += len(gold - got)
            per_query.append((mode, c, q, len(got & gold), len(got - gold), len(gold - got)))
        out[mode] = dict(zip(("precision", "recall", "f1"), prf(tp, fp, fn)), TP=tp, FP=fp, FN=fn)
    return out, queries, per_query


def noise_study(records, seed=11, n=150):
    rng = random.Random(seed)
    sample = records[:n]
    noisy = [corpus_gen.ocr_corrupt(r["text"], rng) for r in sample]
    base, _ = entity_eval(sample)
    raw, _ = entity_eval(sample, noisy)
    cleaned_texts = [noise.clean(t)["cleaned"] for t in noisy]
    fixed, _ = entity_eval(sample, cleaned_texts)
    summ = lambda d: {k: round(sum(v[k] for v in d.values()) / len(d), 4) for k in ("precision", "recall", "f1")}
    # FST coverage on tokens
    def cov(texts):
        toks = [t for x in texts for t in tokenize(x) if t.isalpha()]
        return round(sum(1 for t in toks if morph.analyse(t)) / len(toks), 4)
    return {"macro_entity_clean": summ(base), "macro_entity_noisy_raw": summ(raw),
            "macro_entity_noisy_after_cleanup": summ(fixed),
            "fst_coverage_clean": cov([r["text"] for r in sample]),
            "fst_coverage_noisy_raw": cov(noisy), "fst_coverage_noisy_after_cleanup": cov(cleaned_texts)}


def coverage_by_lexicon_size(records, sizes=(50, 100, 200, 300, 400)):
    toks = [t.lower() for r in records for t in tokenize(r["text"]) if t.isalpha()]
    stems = sorted(morph.ENTRIES)
    res = []
    for k in sizes:
        keep = set(stems[:k]); n = 0
        for t in toks:
            if any(a.lemma in keep for a in morph.analyse(t)):
                n += 1
        res.append((k, round(100 * n / len(toks), 2)))
    return res


def write_annotation_sheet(path, n=200, seed=5):
    rng = random.Random(seed)
    forms = sorted(morph.all_surface_forms())
    pick = rng.sample(forms, n)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["surface", "porter_stem", "fst_analyses", "GOLD_lemma", "GOLD_features", "over_stem?", "under_stem?"])
        for s in pick:
            w.writerow([s, porter_stem(s), "; ".join(str(a) for a in morph.analyse(s)), "", "", "", ""])
    return pick


def run_all(out="results", data="data"):
    os.makedirs(out, exist_ok=True); os.makedirs(data, exist_ok=True)
    R = {}
    recs = corpus_gen.generate(); corpus_gen.save(recs, f"{data}/synthetic_corpus.jsonl")
    ntok = sum(len(tokenize(r["text"])) for r in recs)
    R["corpus"] = {"records": len(recs), "tokens": ntok, "by_type": dict(Counter(r["type"] for r in recs))}
    R["lexicon"] = morph.lexicon_stats()
    tm = {}
    t0 = time.perf_counter()
    for r in recs:
        process_record(r["text"], timings=tm)
    R["timing_seconds"] = {k: round(v, 4) for k, v in tm.items()}
    R["timing_seconds"]["total_wall"] = round(time.perf_counter() - t0, 4)
    R["entity_eval"], errs = entity_eval(recs)
    with open(f"{out}/entity_errors.csv", "w", newline="") as f:
        csv.writer(f).writerows([("record_id", "kind", "entity", "text")] + errs)
    pick = write_annotation_sheet(f"{out}/annotation_sheet_200_forms.csv")
    rows, agree, over, under = stemming_study(pick)
    R["stemming_vs_lemmatisation"] = {"forms": len(pick), "agreement": round(agree, 4),
                                      "over_stemming_stem_classes": round(over, 4),
                                      "under_stemming_lemma_classes": round(under, 4),
                                      "type_to_lemma_ratio_lexicon": round(
                                          len(morph.all_surface_forms()) / len({a.lemma for s in morph._TABLE for a in morph._TABLE[s]}), 3)}
    R["retrieval"], queries, pq = retrieval_eval(recs)
    R["retrieval"]["n_queries"] = len(queries)
    with open(f"{out}/queries.csv", "w", newline="") as f:
        csv.writer(f).writerows([("concept", "query_form")] + queries)
    R["noise_study"] = noise_study(recs)
    R["coverage_by_lexicon_size"] = coverage_by_lexicon_size(recs)
    with open(f"{out}/results.json", "w") as f:
        json.dump(R, f, indent=2)
    try:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        xs, ys = zip(*R["coverage_by_lexicon_size"])
        plt.figure(); plt.plot(xs, ys, marker="o"); plt.xlabel("lexicon size (stems)")
        plt.ylabel("% alphabetic tokens with FST analysis"); plt.title("FST coverage vs lexicon size")
        plt.grid(True); plt.savefig(f"{out}/coverage_vs_lexicon.png", dpi=150); plt.close()
    except Exception as e:
        print("plot skipped:", e)
    return R
