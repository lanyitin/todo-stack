from pyparsing import *
todo_content = lineStart + OneOrMore(Word(printables)) + Optional(OneOrMore("@" + Word( alphanums )))
