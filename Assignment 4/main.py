"""
DSA03 NLP Assignment 4 - Semantic Systems Mini Demonstration
Python standard library only. This is an educational, rule-based demonstration,
not a production NLP parser or trained language model.
Run: python main.py
"""
from dataclasses import dataclass
import re

def task1_event_frame():
    sentence = "Leena sent the report to Arun after the meeting."
    frame = {
        "event": "SEND",
        "agent": "Leena",
        "theme": "the report",
        "recipient": "Arun",
        "time_relation": "after the meeting",
    }
    graph = [
        ("Leena", "AGENT_OF", "SEND"),
        ("the report", "THEME_OF", "SEND"),
        ("Arun", "RECIPIENT_OF", "SEND"),
        ("SEND", "OCCURS_AFTER", "meeting"),
    ]
    return sentence, frame, graph

def task2_logic_demo():
    # A tiny finite knowledge base for a transparent consistency/inference trace.
    facts = {
        ("Learner", "Asha"), ("Learner", "Bala"),
        ("Course", "NLP"), ("Course", "AI"),
        ("Enrolled", "Asha", "NLP"),
        ("Completed", "Asha", "NLP"),
        ("Prerequisite", "NLP", "Logic"),
        ("Completed", "Asha", "Logic"),
    }
    rule = "If Enrolled(x,c) and Course(c), then Learner(x) is eligible for course processing."
    query = ("Completed", "Asha", "NLP")
    return facts, rule, query, query in facts

def task3_attachment_demo():
    sentence = "The analyst noticed the student with the camera near the library."
    readings = [
        {
            "attachment": "'with the camera' attaches to 'student'",
            "meaning": "The student has/is carrying the camera.",
            "representation": "NOTICE(analyst, student); HAS(student, camera); NEAR(student, library)"
        },
        {
            "attachment": "'with the camera' attaches to 'noticed'",
            "meaning": "The analyst used the camera while noticing the student.",
            "representation": "NOTICE(analyst, student); INSTRUMENT(NOTICE, camera); NEAR(student, library)"
        },
    ]
    return sentence, readings

SENSES = {
    "light": {
        "noun_illumination": {"light", "lamp", "switch", "turn", "room", "bulb"},
        "adjective_low_weight": {"bag", "weight", "heavy", "carry", "easy"},
        "adjective_small_meal": {"meal", "food", "breakfast", "dinner", "eat"},
    },
    "bank": {
        "financial": {"cash", "deposit", "money", "account", "loan", "atm"},
        "river_edge": {"river", "water", "shore", "fishing", "sat"},
        "aircraft_turn": {"aircraft", "pilot", "plane", "wing", "left", "turn"},
    },
    "crane": {
        "bird": {"bird", "wings", "nest", "wetland", "feathers"},
        "machine": {"construction", "lift", "load", "building", "operator"},
    },
}

def simple_wsd(sentence, target):
    """Context-overlap baseline. Returns best sense and evidence; ties remain uncertain."""
    words = set(re.findall(r"[a-z]+", sentence.lower()))
    candidates = SENSES.get(target.lower(), {})
    scores = {sense: len(words & cues) for sense, cues in candidates.items()}
    if not scores:
        return {"target": target, "sense": "UNKNOWN", "scores": {}, "evidence": []}
    best = max(scores.values())
    winners = [s for s, score in scores.items() if score == best]
    if best == 0 or len(winners) > 1:
        chosen = "UNCERTAIN"
    else:
        chosen = winners[0]
    evidence = sorted(words & candidates.get(chosen, set())) if chosen in candidates else []
    return {"target": target, "sense": chosen, "scores": scores, "evidence": evidence}

def task4_wsd_demo():
    examples = [
        ("Turn on the light.", "light", "noun_illumination"),
        ("This bag is light.", "light", "adjective_low_weight"),
        ("The light meal was served early.", "light", "adjective_small_meal"),
        ("The backpack is light to carry.", "light", "adjective_low_weight"),
    ]
    return [(s, t, simple_wsd(s, t), expected) for s, t, expected in examples]

DOCUMENTS = [
    ("D1", "Word sense disambiguation uses context to identify the intended meaning of an ambiguous word.", True),
    ("D2", "A dictionary lists several definitions and example usages of words.", False),
    ("D3", "Contextual language models select a word meaning from surrounding words and sentence structure.", True),
    ("D4", "A bank provides savings accounts, loans and cash services.", False),
    ("D5", "Lexical semantics studies word meanings, senses and relations between concepts.", True),
    ("D6", "A spelling checker detects typographical errors in written text.", False),
]

def retrieval_demo(query="How can a system identify the intended meaning of a word in context?"):
    q = set(re.findall(r"[a-z]+", query.lower()))
    rows = []
    for doc_id, text, relevant in DOCUMENTS:
        terms = set(re.findall(r"[a-z]+", text.lower()))
        lexical = len(q & terms) / max(1, len(q))
        # Transparent concept cue score for meaning-oriented query.
        semantic_cues = {"meaning", "ambiguous", "word", "context", "sense", "disambiguation"}
        semantic = len(semantic_cues & terms) / len(semantic_cues)
        score = 0.4 * lexical + 0.6 * semantic
        rows.append({"id": doc_id, "lexical": lexical, "semantic": semantic,
                     "score": score, "relevant": relevant, "text": text})
    return sorted(rows, key=lambda x: (-x["score"], x["id"]))

def task6_crane_demo():
    sentence = "I watched the crane by the bank, then it moved."
    candidates = [
        {
            "reading": "A bird was near a river bank and then moved.",
            "crane_sense": "bird", "bank_sense": "river_edge",
            "representation": "WATCH(speaker, crane_bird); LOCATED_NEAR(crane_bird, river_bank); MOVED(crane_bird)"
        },
        {
            "reading": "A construction crane was near a financial bank/building and then moved.",
            "crane_sense": "machine", "bank_sense": "financial",
            "representation": "WATCH(speaker, crane_machine); LOCATED_NEAR(crane_machine, bank_building); MOVED(crane_machine)"
        },
    ]
    return sentence, candidates

def main():
    print("=" * 72)
    print("DSA03 NLP ASSIGNMENT 4 - SEMANTIC SYSTEMS DEMONSTRATION")
    print("=" * 72)

    s, frame, graph = task1_event_frame()
    print("\nTASK 1 - EVENT / ROLE REPRESENTATION")
    print("Input:", s)
    print("Frame:", frame)
    print("Graph relations:")
    for edge in graph:
        print(" ", " --".join(edge))

    facts, rule, query, follows = task2_logic_demo()
    print("\nTASK 2 - FINITE KNOWLEDGE BASE")
    print("Facts stored:", len(facts))
    print("Rule:", rule)
    print("Query:", query, "=>", "TRUE (fact found)" if follows else "NOT PROVED")

    s, readings = task3_attachment_demo()
    print("\nTASK 3 - PREPOSITIONAL ATTACHMENT")
    print("Input:", s)
    for i, r in enumerate(readings, 1):
        print(f"Reading {i}: {r['attachment']}")
        print(" Meaning:", r["meaning"])
        print(" Representation:", r["representation"])

    print("\nTASK 4 - RULE-BASED WORD SENSE DISAMBIGUATION")
    for sentence, target, result, expected in task4_wsd_demo():
        print("Input:", sentence)
        print(" Selected:", result["sense"], "| scores:", result["scores"],
              "| evidence:", result["evidence"], "| expected:", expected)

    print("\nTASK 5 - SEMANTIC INFORMATION RETRIEVAL")
    print("Query: How can a system identify the intended meaning of a word in context?")
    print("Rank  ID   Lexical  Semantic  Final  Label")
    for rank, row in enumerate(retrieval_demo(), 1):
        print(f"{rank:>4}  {row['id']:<3}  {row['lexical']:.3f}    {row['semantic']:.3f}     "
              f"{row['score']:.3f}  {'Relevant' if row['relevant'] else 'Distractor'}")

    s, candidates = task6_crane_demo()
    print("\nTASK 6 - INTEGRATED AMBIGUITY")
    print("Input:", s)
    for i, c in enumerate(candidates, 1):
        print(f"Candidate {i}: crane={c['crane_sense']}, bank={c['bank_sense']}")
        print(" Meaning:", c["reading"])
        print(" Representation:", c["representation"])

    print("\nLIMITATION: This is a small rule-based teaching demo. It does not use a")
    print("trained parser, neural language model, or live document index.")
    print("Use the written report to explain assumptions, ambiguity and evaluation.")
    print("=" * 72)

if __name__ == "__main__":
    main()
