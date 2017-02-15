class Token(object):
    def __init__(self, token_type, value, line_num):
        self.type = token_type
        self.value = value
        self.line_num = line_num

    def __str__(self):
        return 'Token(type={type}, value={value}, line_num={line_num})'.format(
            type=self.type,
            value=repr(self.value),
			line_num=self.line_num
        )

    def __repr__(self):
        return self.__str__()