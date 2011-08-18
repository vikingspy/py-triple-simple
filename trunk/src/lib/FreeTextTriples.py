__author__ = 'janos'

import re
import pyTripleSimple
import urllib
import os
import string

rdfs_label = pyTripleSimple.common_prefixes["rdfs"] + "label"

class Lexer(object):
    def __init__(self):
        self.regex_rules = re.compile(r"[ ]")
    def lex(self, string_to_lex):
        lex_results = re.split(self.regex_rules,string_to_lex)
        return [x for x in lex_results if len(x) > 0]

class FreeTextLexer(Lexer):
    def __init__(self):
        self.regex_rules = re.compile(r"[ \t\n\.\!\?,;]+")

class FreeTextSimpleTripleStore(object):
    "Generates a free text index of a SimpleTripleStore"
    def __init__(self, triple_simple_store, predicates_to_index = [rdfs_label]):
        self.predicate_for_word = "http://www.w3.org/2001/sw/BestPractices/WNET/wordnet-sw-20040713.html#Word"
        self.triple_simple_store = triple_simple_store
        self.predicates_to_index = predicates_to_index
        self.lexer = FreeTextLexer()
        self.predicates_triple_store = {}

        for predicate_to_index in self.predicates_to_index:
            self.predicates_triple_store[predicate_to_index] = pyTripleSimple.SimpleTripleStore()

    def generate(self):
        for predicate_to_index in self.predicates_to_index:
            triples = self.triple_simple_store.predicates(predicate_to_index)
            if triples:
                for triple in triples:
                    words = self.lexer.lex(triple[2][1:-1])
                    for word in words:
                        self.predicates_triple_store[predicate_to_index].add_triple(pyTripleSimple.SimpleTriple(triple[0][1:-1],self.predicate_for_word,word,"uul"))

    def write_out_to_ntriples(self, prefix = ".", directory = "./"):
        file_names_to_write = []
        for predicate_to_index in self.predicates_to_index:
            file_name_to_write = os.path.join(directory, prefix + string.join(urllib.quote(predicate_to_index + ".nt").split("/"),"_"))
            f = open(file_name_to_write,'w')
            self.predicates_triple_store[predicate_to_index].export_to_ntriples_file(f)
            f.close()
            file_names_to_write.append(file_name_to_write)
        return file_names_to_write
            

