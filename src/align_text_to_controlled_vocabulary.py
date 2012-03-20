__author__ = 'janos'

import sys
import re
import FreeTextTriples as ftt

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        ntriples_to_align = sys.argv[1]
        alignment_source = sys.argv[2]
        ftt.align_ntriples(ntriples_to_align, alignment_source)
        if len(sys.argv) > 3:
            number_of_words_to_split = 5
            number = re.compile("[0-9]+")
            properties = []
            for arg in sys.argv[3:]:
                if number.match(arg):
                    number_of_words_to_split = int(arg)
                else:
                    properties.append(arg)

            if len(properties) == 0:
                ftt.align_ntriples(ntriples_to_align, alignment_source, number_of_words_to_split)
            else:
                ftt.align_ntriples(ntriples_to_align, alignment_source, properties, number_of_words=number_of_words_to_split)
