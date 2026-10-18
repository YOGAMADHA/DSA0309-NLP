
def plural(noun):
    if noun.endswith(('s', 'sh', 'ch', 'x', 'z')):
        return noun + 'es'
    elif noun.endswith('y') and len(noun) > 1 and noun[-2] not in 'aeiou':
        return noun[:-1] + 'ies'
    else:
        return noun + 's'

words = ["cat", "bus", "box", "baby", "dish"]

for word in words:
    print(word, "->", plural(word))
