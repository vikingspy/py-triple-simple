__author__ = 'janos'

import re

class Lexer(object):
    def __init__(self):
        self.regex_rules = re.compile(r"[ ]")
    def lex(self, string_to_lex):
        return re.split(self.regex_rules,string_to_lex)
class FreeTextLexer(Lexer):
    def __init__(self):
        self.regex_rules = re.compile(r"[ \t\n\.\!\?,;]+")
