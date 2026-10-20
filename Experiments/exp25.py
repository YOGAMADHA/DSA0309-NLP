from openai import OpenAI

client = OpenAI()  # Set OPENAI_API_KEY in environment variables

response = client.completions.create(
    model="gpt-3.5-turbo-instruct",
    prompt="Artificial intelligence is",
    max_tokens=40,
    temperature=0.7
)

print(response.choices[0].text.strip())
