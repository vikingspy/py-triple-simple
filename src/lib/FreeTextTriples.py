__author__ = 'janos'

import re
import pyTripleSimple
import urllib
import os
import string
import time
import pprint

rdfs_label = pyTripleSimple.common_prefixes["rdfs"] + "label"

class Lexer(object):
    def __init__(self):
        self.regex_rules = re.compile(r"[ ]")
    def lex(self, string_to_lex):
        lex_results = re.split(self.regex_rules,string_to_lex)
        return [x for x in lex_results if len(x) > 0]

class FreeTextLexer(Lexer):
    def __init__(self):
        self.regex_rules = re.compile(r"[ \t\n\.\!\?,;\:]+")

class FreeTextSimpleTripleStore(object):
    """Generates a free text index of a SimpleTripleStore"""
    def __init__(self, triple_simple_store, predicates_to_index = [rdfs_label]):
        self.predicate_for_word = "http://vivoweb.org/ontology/core#freetextKeyword"
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

class FreeTextExpander(object):
    def __init__(self, n_words_look_ahead):
        self.n_words_look_ahead = n_words_look_ahead
        self.regex_rules = re.compile(r"[ \t\n\.\!\?,;\:]+")

    def parse(self, phrase):
        match_positions = [(x.start(),x.end()) for x in list(self.regex_rules.finditer(" " + phrase + " "))]
        word_boundaries = []
        for i in range(len(match_positions)-1):
            word_boundaries.append((match_positions[i][1], match_positions[i+1][0]))

        number_of_words = len(word_boundaries)
        words_phrases = []
        for i in range(number_of_words):
            word_phrase = []
            for j in range(self.n_words_look_ahead):
                if i + j < number_of_words:
                    word_phrase.append(phrase[word_boundaries[i][0]-1:word_boundaries[i+j][1]-1])
            words_phrases.append(word_phrase)
        return words_phrases

class FreeTextExpanderTripleStore(FreeTextSimpleTripleStore):
    def generate(self, n_look_ahead = 3):
        self.n_look_ahead = n_look_ahead
        for predicate_to_index in self.predicates_to_index:
            triples = self.triple_simple_store.predicates(predicate_to_index)
            if triples:
                for triple in triples:
                    phrases_obj = FreeTextExpander(self.n_look_ahead)
                    for phrase_words in phrases_obj.parse(triple[2][1:-1]):
                        i = 1
                        for phrase_word in phrase_words:
                            self.predicates_triple_store[predicate_to_index].add_triple(pyTripleSimple.SimpleTriple(triple[0][1:-1], self.predicate_for_word + str(i), phrase_word,"uul"))
                            i = i + 1


def align_ntriples(ntriples_file_to_align, alignment_file, predicates_to_align =  [rdfs_label], alignment_uri = "http://example.org/aligned",number_of_words = 5):

    print("Generating file to align into memory")
    ff = open(ntriples_file_to_align)
    triples_to_fragment = pyTripleSimple.SimpleTripleStore()
    triples_to_fragment.load_ntriples(ff)

    ff.close()

    print("Reading alignment file into memory")

    fte_obj = FreeTextExpanderTripleStore(triples_to_fragment, predicates_to_align)
    fte_obj.generate(number_of_words)
    alignment_files = fte_obj.write_out_to_ntriples()

    alignment_obj = pyTripleSimple.SimpleTripleStore()
    fa = open(alignment_file)
    alignment_obj.load_ntriples(fa)
    fa.close()

    aligned_obj = pyTripleSimple.SimpleTripleStore()

    for alignment_file in alignment_files:
        faf = open(alignment_file)
        fragments_obj = pyTripleSimple.SimpleTripleStore()
        print("Loading fragments to align into memory '%s'" % alignment_file)
        fragments_obj.load_ntriples(faf)
        for fragment in fragments_obj.iterator_triples():
            result = alignment_obj.simple_pattern_match([("s","p","o")], [("o", "in", [fragment.object])],["s"])

            if result:
                aligned_obj.load_ntriples(["<%s> <%s> %s ." % (fragment.subject, alignment_uri, result[0][0][0])])

    ntriples_aligned_file = ntriples_file_to_align + ".alignment.nt"
    print("Exporting aligned file")

    fo = open(ntriples_aligned_file,"w")
    aligned_obj.export_to_ntriples_file(fo)
    fo.close()

def main(ntriples_file_name,free_text_predicates=None):
    f = open(ntriples_file_name,"r")

    ts = pyTripleSimple.SimpleTripleStore() #pyTripleSimple.ShelveTripleEngine(ntriples_file_name)

    print('Loading "%s"' % os.path.abspath(ntriples_file_name))
    start_time = time.clock()
    ts.load_ntriples(f)
    end_time = time.clock()
    print("Finished loading ntriples file")
    #print("Number of triples %s loaded in %s seconds (%s triples/second)" % (number_of_triples, end_time - start_time,(number_of_triples * 1.0)/ (end_time - start_time)))

    if free_text_predicates is not None:
        ft = FreeTextSimpleTripleStore(ts, predicates_to_index = free_text_predicates)
    else:
        ft = FreeTextSimpleTripleStore(ts)

    ft.generate()
    file_names = write_out_to_ntriples(ntriples_file_name + ".")

    print("Generated free text triples '%s'" % ntriples_file_name)
    for file_name in file_names:
        print("Wrote '%s'" % file_name)

    return file_names

