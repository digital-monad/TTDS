from ast import arg
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

import re, os, sys
sys.path.insert(0, './QueryParser') 
import DBQuery as dbq

from julia.api import Julia

from preprocess import preprocess

JL = Julia(compiled_modules=False)
JL.eval('include("./setOperations.jl")')
JL.eval('include("./search.jl")')

from julia import Main


# SONGCOUNT = 1200000
# LYRICCOUNT = 60000000

class QueryParser:
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

        self.connection = dbq.DBQuery()
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

        print(argument)

        clause_results = [self.evaluate(arg) for arg in argument]

        assert(len(clause_results) == 2)

        Main.df1 = clause_results[0]
        Main.df2 = clause_results[1]

        return JL.eval("@time and(df1,df2)")
        
       

        if (range_max) == 0:
            return [(doc_id,scores[doc_id]) for doc_id in scores]        
        else:
            return [(doc_id,scores[doc_id]/(range_max)) for doc_id in scores]


    def evaluateOr(self, argument):
      
        clause_results = [self.evaluate(arg) for arg in argument]

        assert(len(clause_results) == 2)

        Main.df1 = clause_results[0]
        Main.df2 = clause_results[1]

        return JL.eval("@time or(df1,df2)")
        
        # clause_results = [self.evaluate(arg) for arg in argument]
    
        # clause_doc_ids = [[elm[0] for elm in clause] for clause in clause_results]
        
        # doc_ids = set.union(*map(set,clause_doc_ids))

        # scores = {doc_id : 0 for doc_id in doc_ids}

        # for clause in clause_results:
        #     for id, score in clause:
        #         if id in doc_ids and score > scores[id]:
        #             scores[id] = score

        # return [(doc_id,scores[doc_id]) for doc_id in scores]

    def evaluateNot(self, argument):

        print("NOT")
        print(argument)
        
        Main.df = self.evaluate(argument[0])
        
        if(self.isSong):
            Main.count = self.songCount
        else:
            Main.count = self.lyricCount

        return JL.eval("@time not(count,df)")

    def evaluateParenthesis(self, argument):

        if len(argument) > 1:
            print(argument)
            raise BaseException("?")

        return self.evaluate(argument[0])

    def evaluatePhrase(self, argument):
        
        # Phrase search 

        print("phrase")
        print(argument)
        print(list(list(zip(*preprocess(argument[0][0])[0]))[0]))

        Main.terms = list(list(zip(*preprocess(argument[0][0])[0]))[0])
        Main.isSong = self.isSong

        return JL.eval("call_ps(terms,isSong)")

    def evaluateProximity(self, argument):
        
        # Proximity search 

        # print("proximity")

        if(len(argument) != 3):
            raise BaseException("??")

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

        Main.term1 = preprocess(term1)[0][0][0]
        Main.term2 = preprocess(term2)[0][0][0]
        
        Main.proximity = distance
        Main.isSong = self.isSong

        return JL.eval("call_prox(term1, term2, proximity, isSong)")



    def evaluateWord(self, argument):

        # Do search over argument
        searchReturn = True

        print("ranked search")
        print(argument)
        print(list(list(zip(*preprocess(argument[0])[0]))[0]))
        
        
        Main.terms = list(list(zip(*preprocess(argument[0])[0]))[0])
        Main.isSong = self.isSong

        return JL.eval("call_BM25(terms,isSong)")


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

        Main.unsorted_query_results = unsorted_query_results

        res = JL.eval("@time sort_and_convert(unsorted_query_results)")

        print("IN PYTHON")
        print(res)

        return res
        
# x = QueryParser()

# # x.query('! bean', True)
# x.query('"nowhere left to run" && #(20, Thriller, Killer)', True)
