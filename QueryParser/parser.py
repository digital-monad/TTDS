from numpy import Infinity
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

        clause_results = [self.evaluate(arg) for arg in argument]

        clause_doc_ids = [[elm[0] for elm in clause] for clause in clause_results]
        
        doc_ids = set.intersection(*map(set,clause_doc_ids))

        scores = {doc_id : 0 for doc_id in doc_ids}

        range_max = 0

        for clause in clause_results:
            for id, score in clause:
                if id in doc_ids:

                    scores[id] += score

                    if(scores[id] > range_max):
                        range_max = scores[id]

        if (range_max) != 0:

            return [(doc_id,scores[doc_id]/(range_max)) for doc_id in scores]
        
        else:

            return [(doc_id,scores[doc_id]) for doc_id in scores]

    def evaluateOr(self, argument):
      
        clause_results = [self.evaluate(arg) for arg in argument]

        clause_doc_ids = [[elm[0] for elm in clause] for clause in clause_results]
        
        doc_ids = set.union(*map(set,clause_doc_ids))

        scores = {doc_id : 0 for doc_id in doc_ids}

        for clause in clause_results:
            for id, score in clause:
                if id in doc_ids and score > scores[id]:
                    scores[id] = score

        return [(doc_id,scores[doc_id]) for doc_id in scores]

    def evaluateNot(self, argument):
        
        clause_result = self.evaluate(argument[0])

        # This will be the number of documents in the whole dataset. 
        all_doc_ids = set(range(100))

        clause_doc_ids = set([elm[1] for elm in clause_result])

        return [(doc_id,clause_result[doc_id]) for doc_id in all_doc_ids - clause_doc_ids]

    def evaluateParenthesis(self, argument):

        if len(argument) > 1:
            print("PARATHESSISSS")
            print(argument)

        return self.evaluate(argument[0])

    def evaluatePhrase(self, argument):
        
        # Phrase search 

        print("phrase")
        print(argument)

        return [(1,0.5),(2,0.8)]

    def evaluateProximity(self, argument):
        
        # Phrase search 
        print("proximity")
        print(argument)

        return [(1,1)]


    def evaluateWord(self, argument):

        # Do search over argument
        searchReturn = True

        print("ranked search")
        print(argument)

        return [(1,0.25)]


    def evaluate(self, argument):
    
        return self._methods[argument.getName()](argument)

    def Parse(self, query):

        parsed = self._parser(query)

        print("--")
        print(parsed)
        print("--")
        
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

        # get top N results (skipping the first `skip` results)
        # return a list of (id, score) tuples, sorted from highest to lowest by score (e.g. [(19, 1.5), (6, 1.46), ...]
        unsorted_query_results = self.Parse(expr)

        print("results")
        print(unsorted_query_results)
        

