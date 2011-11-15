#!/usr/bin/python
"""
    By default loads a ntriples file into a in-memory triple store
    and performs basic statistics on the resulting ntriple file
"""


import time
import os
import pprint

import pyTripleSimple

from optparse import OptionParser

def main():
    parser = OptionParser(usage="usage: %prog [options]",
                          version="%prog 1.0")
    parser.add_option("-f", "--file",
                      action="store",
                      dest="file_name",
                      default=False,
                      help="ntriples file to read in")
    
    parser.add_option("-c", "--command",
                      action="store",
                      dest="command",
                      default="statistics",
                      help="")

    parser.add_option("-q", "--query",
                      action="store",
                      dest="query",
                      default=False,
                      help="Specify the pattern to match the solution for")

    parser.add_option("-r", "--restrictions",
                      action="store",
                      dest="restrictions",
                      default=None,
                      help="Specify restrictions on the solution")

    parser.add_option("-v", "--variables",
                      action="store",
                      dest="variables",
                      default=False,
                      help="Specify the variables for output")

    parser.add_option("-n", "--limit",
                      action="store",
                      dest="display_n",
                      default="50",
                      help="Limit the number of results")


    (options, args) = parser.parse_args()

    #print args

    ts = pyTripleSimple.SimpleTripleStore() #pyTripleSimple.ShelveTripleEngine(ntriples_file_name)


    if options.display_n == "All":
        display_n = None
    else:
        display_n=int(options.display_n)

    file_name = options.file_name
    if file_name:
        try:
            f = open(file_name,"r")
        except IOError:
            raise


        print('Loading "%s"' % os.path.abspath(file_name))
        start_time = time.clock()
        ts.load_ntriples(f)
        end_time = time.clock()
        print("Finished loading ntriples file")


        if options.command == "statistics":
            number_of_triples = ts.n_triples()

            print("Number of triples %s loaded in %s seconds (%s triples/second)" % (number_of_triples, end_time - start_time,(number_of_triples * 1.0)/ (end_time - start_time)))
            print("Number of distinct lexical symbols: %s" % ts.n_symbols())

            print("Number of distinct subjects: %s" % ts.n_subjects())
            print("Number of distinct predicates: %s" % ts.n_predicates())
            n_objects = ts.n_objects()
            print("Number of distinct objects including literals: %s" % n_objects)
            n_literals = ts.n_literals()
            print("Number of literals: %s" % n_literals)
            print("Fraction of objects that are literals: %s" % ((n_literals * 1.0) / n_objects ))
            print("")
            print("Top subjects are:")
            pprint.pprint(ts.top_subjects(display_n))
            print("")
            print("Top objects are:")
            pprint.pprint(ts.top_objects(display_n))
            print("")
            print("Top predicates are:")
            pprint.pprint(ts.top_predicates(None))

        elif options.command == "query":
            query = eval(options.query)
            if options.restrictions:
                restrictions = eval(options.restrictions)
            else:
                restrictions = []
            if options.variables:
                solution_variables = eval(options.variables)
            else:
                solution_variables = None

            r = ts.simple_pattern_match(query, restrictions, solution_variables)

            if display_n == "All":
                pass
            else:
                r = r[:display_n]

            pprint.pprint(r)




if __name__ == "__main__":
    main()