def recognize_dialog_act(sentence):
    text = sentence.lower().strip()

    if text.endswith("?"):
        return "Question"
    elif text.startswith(("hi", "hello", "hey")):
        return "Greeting"
    elif text.startswith(("please", "could you", "can you")):
        return "Request"
    elif text.startswith(("thank you", "thanks")):
        return "Thanking"
    else:
        return "Statement"

dialog = [
    "Hello!",
    "What is your name?",
    "Please help me",
    "Thank you",
    "Python is useful"
]

for sentence in dialog:
    print(sentence, "->", recognize_dialog_act(sentence))
