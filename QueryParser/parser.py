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

from DBQuery import DBQuery

# SONGCOUNT = 1200000
# LYRICCOUNT = 60000000

class QuerySearchParser:
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

        self.connection = DBQuery()
        self.songCount = self.connection.countSongs()
        self.lyricCount = self.connection.countLyrics()
        self._parser = self.parser()
        self.text = ""
        self.words = []
        self.isSong = True

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
            Group(Suppress('#(') + operatorBooleanContent + Suppress(',') + operatorBooleanContent +  Suppress(',') + operatorBooleanContent + Suppress(')')).setResultsName(
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

        if (range_max) == 0:
            return [(doc_id,scores[doc_id]) for doc_id in scores]        
        else:
            return [(doc_id,scores[doc_id]/(range_max)) for doc_id in scores]


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
        
        clause_result = map(list, zip(*self.evaluate(argument[0])))

        if(self.isSong):
            return [(id,0) for id in (set(range(0,self.songCount)) - set(clause_result[0]))]
        else:
            return [(id,0) for id in (set(range(0,self.lyricCount)) - set(clause_result[0]))]
        

    def evaluateParenthesis(self, argument):

        if len(argument) > 1:
            print(argument)
            raise BaseException("?")

        return self.evaluate(argument[0])

    def evaluatePhrase(self, argument):
        
        # Phrase search 

        # print("phrase")
        # print(argument)

        return [(1,0.5),(2,0.8)]

    def evaluateProximity(self, argument):
        
        # Proximity search 

        # print("proximity")

        try:
            distance = int(argument[0][0])
        except:
            raise BaseException("Proximity distance is not an int")

        term1 = argument[1][0].strip()
        term2 = argument[2][0].strip()

        if(any(term.count(' ') for term in [term1,term2])):
            raise BaseException("Proximity terms must be single words")

        # print("distance : " + str(distance))
        # print("term1 : " + str(term1))
        # print("term2 : " + str(term2))

        return [(1,1)]


    def evaluateWord(self, argument):

        # Do search over argument
        searchReturn = True

        # print("ranked search")
        # print(argument)

        return [(1,0.25)]


    def evaluate(self, argument):
        
        # print("evaluate")
        # print(argument)

        return self._methods[argument.getName()](argument)

    def Parse(self, query):

        return self.evaluate(self._parser(query)[0])

    def query(self, expr, isSong):

        print(expr)

        self.isSong = isSong

        # get top N results (skipping the first `skip` results)
        # return a list of (id, score) tuples, sorted from highest to lowest by score (e.g. [(19, 1.5), (6, 1.46), ...]
        unsorted_query_results = self.Parse(expr)

        print("results")
        print(unsorted_query_results)
        
x = QuerySearchParser()

x.query("Beef",True)

print(x.songCount)
print(list(x.connection.get_indexed_by_terms(["beans","super","god"])))
print(x.lyricCount)