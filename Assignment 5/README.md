# NLP Assignment 5 – CO5: Language Generation and Discourse Analysis

## Run
1. Install Python 3.10 or newer.
2. Open this folder in VS Code.
3. Run `python src/main.py` (Windows: `py src/main.py`).

No external packages are required.

## Project contents
- `src/main.py` – sentence segmentation, small-domain mention inventory, pronoun resolver, instrumentation, scoring example and dialogue-act demo.
- `tests/test_main.py` – repeatable checks.
- `outputs/sample_output.txt` – captured run output.
- `screenshots/output.png` – screenshot-style capture of the actual program output.

## Important scope note
This is a transparent educational prototype, not a full NLP parser. It uses a small hand-written entity lexicon for the supplied lab incident report and simple rules for dialogue acts. It does not claim measured BLEU/chrF scores, production-grade coreference, neural machine translation, or universal discourse parsing. For B1–B4, the report gives reproducible toy experiments and explicitly labels synthetic operation/quality estimates as such. Replace the toy gold annotation and add a labelled corpus before claiming real-world accuracy.

