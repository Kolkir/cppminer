from .context import Context


def make_str_key(list_value):
    str_value = ""
    for item in list_value:
        str_value += str(item)
        str_value += "|"
    str_value = str_value[:-1]
    return str_value


class Sample:
    def __init__(self, key, contexts, source_mark, validate=False):
        self.key = key
        self.contexts = contexts
        self.source_mark = source_mark
        if validate:
            self.__validate()

    def __validate(self):
        assert len(self.key) > 0, "Invalid target key format: {0}".format(self.key)
        for sub_token in self.key:
            assert len(sub_token) > 0, "Invalid sub-token in the target key: {0}".format(self.key)
            Context.validate_sub_token(sub_token)

    def __str__(self):
        str_value = make_str_key(self.key)
        for context in self.contexts:
            str_value += " " + make_str_key(context.start_token)
            str_value += "," + make_str_key(context.path.tokens)
            str_value += "," + make_str_key(context.end_token)
        return str_value
