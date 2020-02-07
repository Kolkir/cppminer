def make_str_key(list_value):
    str_value = ""
    for item in list_value:
        str_value += str(item)
        str_value += "|"
    str_value = str_value[:-1]
    return str_value


class Sample:
    def __init__(self, key, contexts):
        self.key = key
        self.contexts = contexts

    def __str__(self):
        str_value = make_str_key(self.key)
        for context in self.contexts:
            str_value += " " + make_str_key(context.start_token)
            str_value += "," + str(context.path)
            str_value += "," + make_str_key(context.end_token)
        return str_value
