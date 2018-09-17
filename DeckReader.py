keyword_dict = {'KEYWORD1': (1, lambda l: l.split(), (str,)),
                'MULTIKEYW': (2, lambda l: l.split(), (str, float))}

class keyword():

    __init__(self, line, expected_params, func, verification):
        output = func(line)
