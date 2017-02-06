class Parser(object):
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.current_token = next(self.tokenizer)

    def parse(self):
        pass