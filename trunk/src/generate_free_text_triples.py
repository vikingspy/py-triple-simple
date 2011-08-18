"""
    Creates a free text index from ntriples based file.
"""

__author__ = 'Janos G. Hajagos'

import FreeTextTriples
import pyTripleSimple
import time
import sys
import os

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
        ft = FreeTextTriples.FreeTextSimpleTripleStore(ts, predicates_to_index = free_text_predicates)
    else:
        ft = FreeTextTriples.FreeTextSimpleTripleStore(ts)
    
    ft.generate()
    file_names = ft.write_out_to_ntriples(ntriples_file_name + ".")

    print("Generated free text triples '%s'" % ntriples_file_name)
    for file_name in file_names:
        print("Wrote '%s'" % file_name)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("""Usage:
python generate_free_text_triples.py reach.nt 'http://www.w3.org/2008/05/skos#prefLabel'""")
    else:
        if len(sys.argv) == 2:
            main(sys.argv[1])
        else:
            main(sys.argv[1], sys.argv[2:])