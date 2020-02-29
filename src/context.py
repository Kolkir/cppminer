class Context:
    def __init__(self, start_token, end_token, path, validate=False):
        self.start_token = start_token
        self.end_token = end_token
        self.path = path
        if validate:
            self.__validate()

    def __validate(self):
        self.__validate_token(self.start_token)
        self.__validate_token(self.end_token)

    def __validate_token(self, token):
        assert len(token) > 0, "Invalid token format: {0}".format(token)
        for sub_token in token:
            assert len(sub_token) > 0, "Invalid sub-token: {0}".format(token)
            self.validate_sub_token(sub_token)

    @staticmethod
    def validate_sub_token(sub_token):
        assert (' ' not in sub_token and
                '|' not in sub_token and
                ',' not in sub_token), "Invalid sub-token format: {0}".format(sub_token)
