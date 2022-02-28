from pyparsing import (
    Word,
    alphanums,
    Keyword,
    Group,
    Forward,
    Suppress,
    OneOrMore,
    oneOf,
)
import re

class BooleanSearchParser:
    def __init__(self):
        self._methods = {
            "and": self.evaluateAnd,
            "or": self.evaluateOr,
            "not": self.evaluateNot,
            "parenthesis": self.evaluateParenthesis,
            "phrase": self.evaluatePhrase,
            "proximity": self.evaluateProximity,
            "word": self.evaluateWord
        }
        self._parser = self.parser()
        self.text = ""
        self.words = []

    def parser(self):
        """
        This function returns a parser.
        Grammar:
        - a query consists of alphanumeric words
        - a sequence of words between quotes is a phrase search
        - words can be used together by using operators ('&&', '||', '~')
        - words with operators can be grouped with parenthesis
        - phrase or proximity search can be preceded by a 'not' operator
        """
        operatorOr = Forward()

        alphabet = alphanums + ' '

        notKeyword = Keyword("~") 

        andKeyword = Keyword("&&")

        orKeyword = Keyword("||")

        operatorWord = Group(Word(alphabet)).setResultsName("word")

        operatorBooleanContent = Forward()

        operatorBooleanContent << ((operatorWord + operatorBooleanContent) | operatorWord)

        operatorPhrase = (
            Group(Suppress('"') + operatorBooleanContent + Suppress('"')).setResultsName(
                "phrase"
            )
            | operatorWord
        )

        operatorProximity = (
            Group(Suppress('#(') + operatorBooleanContent + Suppress(')')).setResultsName(
                "proximity"
            )
            | operatorWord
        )

        operatorParenthesis = (
            Group(Suppress("(") + operatorOr + Suppress(")")).setResultsName(
                "parenthesis"
            )
            | operatorPhrase | operatorProximity
        )


        operatorNot = Forward()
        operatorNot << (
            Group(Suppress(notKeyword) + operatorNot).setResultsName(
                "not"
            )
            | operatorParenthesis
        )

        operatorAnd = Forward()
        operatorAnd << (
            Group(
                operatorNot + Suppress(andKeyword) + operatorAnd
            ).setResultsName("and")
            | operatorNot
        )

        operatorOr << (
            Group(
                operatorAnd + Suppress(orKeyword) + operatorOr
            ).setResultsName("or")
            | operatorAnd
        )

        return operatorOr.parseString

    def evaluateAnd(self, argument):
        return all(self.evaluate(arg) for arg in argument)

    def evaluateOr(self, argument):

        print("OR")
        print(argument)
        return any(self.evaluate(arg) for arg in argument)

    def evaluateNot(self, argument):
        return self.GetNot(self.evaluate(argument[0]))

    def evaluateParenthesis(self, argument):
        return self.evaluate(argument[0])

    def evaluatePhrase(self, argument):
        
        # Phrase search 

        print("phrase")
        print(argument)

        return True

    def evaluateProximity(self, argument):
        
        # Phrase search 

        print("proximity")
        print(argument)

        return True

    def evaluateWord(self, argument):

        # Do search over argument
        searchReturn = True

        print("ranked search")
        print(argument)

        return searchReturn

    def evaluateWordWildcardPrefix(self, argument):
        return self.GetWordWildcard(argument[0], method="endswith")

    def evaluateWordWildcardSufix(self, argument):
        return self.GetWordWildcard(argument[0], method="startswith")

    def evaluate(self, argument):
    
        return self._methods[argument.getName()](argument)

    def Parse(self, query):

        parsed = self._parser(query)

        print(parsed)
        return self.evaluate(self._parser(query)[0])

    def GetNot(self, not_set):
        return not not_set

    def _split_words(self, text):
        words = []
        """
        >>> import string
        >>> string.punctuation
        '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
        """
        # it will keep @, # and
        # usernames and hashtags can contain dots, so a double check is done
        r = re.compile(r"[\s{}]+".format(re.escape("!\"$%&'()*+,-/:;<=>?[\\]^`{|}~")))
        _words = r.split(text)
        for _w in _words:
            if "." in _w and not _w.startswith("#") and not _w.startswith("@"):
                for __w in _w.split("."):
                    words.append(__w)
                continue

            words.append(_w)

        return words

    def query(self, expr):

        return self.Parse(expr)

x = BooleanSearchParser()

print(x.query('"beef beeeeef beef" && ranked query && ("chicken") && #(fish) && (#(beans)) && (rice || "cheese")'))