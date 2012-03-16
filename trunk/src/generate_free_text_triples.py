"""
    Generates a free text index from an ntriples file.
"""

__author__ = 'Janos G. Hajagos'

import FreeTextTriples
import sys

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("""Usage:
python generate_free_text_triples.py reach.nt 'http://www.w3.org/2008/05/skos#prefLabel'""")
    else:
        if len(sys.argv) == 2:
            FreeTextTriples.main(sys.argv[1])
        else:
            FreeTextTriples.main(sys.argv[1], sys.argv[2:])