"""Run the complete experiment suite:  python run_all.py   (writes data/ and results/)"""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))
from hospital_nlp.evaluate import run_all

if __name__ == "__main__":
    print(json.dumps(run_all(), indent=2))
