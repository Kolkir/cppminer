from context import Context


class Path:
    def __init__(self, tokens, validate=False):
        self.tokens = tokens
        if validate:
            self.__validate()

    def __validate(self):
        for sub_token in self.tokens:
            assert len(sub_token) > 0, "Invalid sub-token in the path: {0}".format(self.tokens)
            Context.validate_sub_token(sub_token)
