class Context:
    def __init__(self, start_token, end_token):
        self.start_token = start_token
        self.end_token = end_token
        self.path = []