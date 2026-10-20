import spacy

nlp = spacy.load("en_core_web_sm")
text = "Ravi bought a laptop. He uses it every day."

doc = nlp(text)

for token in doc:
    if token.pos_ == "PRON":
        print(token.text, "->", "Ravi" if token.text == "He" else "laptop")
