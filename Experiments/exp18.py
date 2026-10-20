import re

def parse_fopc(expression):
    pattern = r'^(forall|exists)\s+[a-z]\s*\(.*\)$'
    if re.match(pattern, expression):
        return "Valid FOPC expression"
    return "Invalid FOPC expression"

expressions = [
    "forall x (Human(x) -> Mortal(x))",
    "exists y (Student(y))",
    "Human(x)"
]

for exp in expressions:
    print(exp, ":", parse_fopc(exp))
