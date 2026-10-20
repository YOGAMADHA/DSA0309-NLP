from transformers import pipeline

translator = pipeline(
    "translation_en_to_fr",
    model="Helsinki-NLP/opus-mt-en-fr"
)

text = "Hello, how are you?"
result = translator(text)

print("English:", text)
print("French:", result[0]["translation_text"])
