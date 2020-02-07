class Path:
    def __init__(self, tokens):
        self.tokens = tokens
        self.hash_value = hash(tuple(tokens))

    def __hash__(self):
        return self.hash_value

    def __eq__(self, other):
        return self.tokens == other.tokens
