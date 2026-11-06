# Morphology-Aware Text Normalisation and Search Layer for a Hospital Record System

DSA03 – Natural Language Processing, Assignment 1 · Yoga Madha A · 192425058 · B.Tech AI&ML (3rd year)

Python implementation that backs every task in the report: regex entity recognisers, a maximal-munch
tokeniser, rewrite-rule normalisation, DFA/NFA machinery (subset construction, minimisation, state
elimination, Thompson construction), a finite-state-style morphological analyser/generator with
orthographic rules, Porter stemming, an OCR/code-mixing front end, a search index, and an evaluation
runner that produces **measured** numbers to replace the illustrative figures in the PDF.

## Quick start (Windows 11 / VS Code or Linux/macOS)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows   (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
python -m pytest -q             # 77 tests
python demo.py                  # hand-trace style output for the report
python run_all.py               # regenerates data/ and results/ (results.json, CSVs, plot)
```

## Layout and task map

| File | Report task |
|---|---|
| `src/hospital_nlp/patterns.py` | Task 2 – 12 entity regexes, positive/negative tests, semantic validators, overlap resolution |
| `src/hospital_nlp/tokenizer.py` | Task 3 – tokeniser with true maximal munch |
| `src/hospital_nlp/normalise.py` | Task 3 – case/abbreviation/date/unit rewrite rules, context-dependent expansion, audit log |
| `src/hospital_nlp/automata.py` | Task 4 – 4 DFA validators, ε-NFA, subset construction, Moore minimisation, DFA→regex |
| `src/hospital_nlp/thompson.py` | Task 4.5 – regex → ε-NFA (Thompson) |
| `src/hospital_nlp/lexicon_data.py` | Tasks 5–6 – stems (≥300), 24 inflectional / 23 derivational affixes, irregulars, derived families |
| `src/hospital_nlp/orthography.py` | Task 8 – e-deletion, y→i, consonant doubling, sibilant -es |
| `src/hospital_nlp/morphology.py` | Task 7 – analysis and generation from one surface↔lexical relation, ambiguity preserved |
| `src/hospital_nlp/porter_wrap.py` | Task 9 – NLTK Porter + measure *m* |
| `src/hospital_nlp/noise.py` | Task 12 – weighted edit distance, OCR repair, line-break repair, diacritics, char-trigram language ID |
| `src/hospital_nlp/pipeline.py` | Tasks 1.5/10/12 – pipeline and ranked inverted index |
| `src/hospital_nlp/corpus_gen.py` | Synthetic corpus: 500 records, 36,968 tokens, fixed seed |
| `src/hospital_nlp/evaluate.py` | Tasks 2.5, 5.5, 9, 10, 12 – measured experiments |
| `tests/` | Task 10.2 test plan (77 tests) |
| `results/` | Generated: `results.json`, `entity_errors.csv`, `queries.csv`, `annotation_sheet_200_forms.csv`, `coverage_vs_lexicon.png` |

## Measured results (seed 20260611; rerun with `python run_all.py`)

Corpus: 500 records, 36,968 tokens. Lexicon: 431 stems, 1018 generated surface forms.

| Entity | TP | FP | FN | Precision | Recall |
|---|---|---|---|---|---|
| patient_id | 500 | 0 | 0 | 1.0 | 1.0 |
| date | 550 | 0 | 0 | 1.0 | 1.0 |
| blood_pressure | 375 | 0 | 0 | 1.0 | 1.0 |
| lab_value | 250 | 0 | 0 | 1.0 | 1.0 |
| temperature | 250 | 0 | 0 | 1.0 | 1.0 |
| drug_strength | 655 | 0 | 0 | 1.0 | 1.0 |
| ward_bed | 250 | 0 | 0 | 1.0 | 1.0 |
| contact | 150 | 0 | 0 | 1.0 | 1.0 |
| age | 150 | 0 | 0 | 1.0 | 1.0 |
| frequency | 655 | 0 | 0 | 1.0 | 1.0 |
| icd_code | 275 | 0 | 0 | 1.0 | 1.0 |
| duration | 755 | 0 | 0 | 1.0 | 1.0 |

Stemming vs lemmatisation (200 random forms): Porter stem equals FST lemma on **52%**; Porter conflates distinct lemmas
in 3.6% of stem classes (over-stemming) and splits one lemma across several stems in
19.6% of lemmas (under-stemming).

Retrieval over 40 queries: none P/R/F1 = 1.0/0.4029/0.5744;
Porter = 1.0/0.9147/0.9555; FST = 1.0/1.0/1.0.

OCR noise (150 records, synthetic corruption): macro entity F1 clean 1.0 → noisy 0.9064 → after cleanup 0.9513.

FST coverage vs lexicon size (alphabetic corpus tokens with an analysis):

| Stems | Coverage |
|---|---|
| 50 | 7.58% |
| 100 | 12.81% |
| 200 | 23.96% |
| 300 | 34.52% |
| 400 | 45.4% |

Runtime on the machine that produced these files (sandbox, **not** your laptop): {'entity_recognition': 0.1006, 'normalisation': 0.056, 'tokenisation': 0.0822, 'fst_analysis': 0.1844, 'total_wall': 0.4293}. Re-run on your own Windows 11 machine and record hardware before submitting.

## Read this before submitting – honest limitations

1. **The corpus is synthetic and generated from templates, and the gold labels come from the same generator.**
   Entity F1 ≈ 1.0 and retrieval F1 = 1.0 for the FST therefore show the code works, **not** how it would perform on real
   hospital text. The retrieval relevance judgements are *automatic* (concept inserted by the generator); the assignment
   asks for 40 clinician-style queries with *manual* binary judgements. `results/queries.csv` and
   `results/annotation_sheet_200_forms.csv` (blank `GOLD_*` columns) are provided so you can do the manual annotation and
   re-score.
2. The generated sentences are grammatically odd on purpose (they exist to exercise morphology, not to read like notes).
3. Replace the illustrative tables in the PDF (Task 2.5, 5.5, 6.4, 8.4 "17 pass / 3 exceptions", 9.4, 9.5, 12) with
   the numbers in `results/results.json`; for example Porter/lemma agreement here is 52%, not the PDF's 74%.
4. Notes where the code deliberately differs from the PDF text:
   - The PDF shows regexes with doubled backslashes (`\\b`); in a Python raw string a single backslash is correct.
   - `frequency` is tried before `icd_code` because `Q8H` also fits the ICD shape (this removed 81 FP/81 FN in the first run).
   - Drug+strength uses a single drug word (the PDF's optional second word swallowed words such as "Tab").
   - The PDF's NFA lists states s0–s8 but an accepting s9; the code uses s0–s9 consistently.
   - DFA state counts include the explicit dead state; minimisation leaves the patient-ID DFA unchanged (11 states with dead state).
   - Entity recognition is validated after matching (calendar dates, BP/temperature/age ranges).
5. Derivational forms are an explicit attested list (not free concatenation), as argued in Task 6.2.
6. Language ID uses a tiny seed list of Romanised Tamil words; extend `TAMIL_ROMAN` with bilingual-reviewer-approved forms.
7. Abbreviation expansions (especially OD/BD/SOS and the ambiguous `MS`) need review by a clinical subject expert.
8. The pumping-lemma test only illustrates the argument for p = 5; the proof itself is in the report.

## Publishing to GitHub

```bash
git init
git add .
git commit -m "DSA03 NLP Assignment 1 - hospital record normalisation and search"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```
(Or create an empty repo on github.com and use *Add file → Upload files* with the unzipped contents.)
