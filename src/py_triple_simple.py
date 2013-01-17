#!/usr/bin/env python
"""
    By default loads a N-Triples file into an in-memory triple store
    and performs basic statistics on the resulting N-Triples file

    @author: Janos
"""

import time
import os
import pprint
import StringIO

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
                      help="Supported commands are: 'statistics' and 'query'")

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

    parser.add_option("-o","--output-format",
                      action ="store",
                      dest="output_format",
                      default="stdout",
                      help="Query output format: stdout, json, delimited, ntriples")

    parser.add_option("-w","--output-file",
                          action ="store",
                          dest="output_file_name",
                          default=0,
                          help="Send results to named file")

    parser.add_option("--header",
                      action = "store",
                      dest = "header",
                      default = 1,
                      help = "For table output add a header row")


    parser.add_option("--delimiter",
                      action = "store",
                      dest = "delimiter",
                      default = "\t",
                      help = "Delimiter to use in table output")

    parser.add_option("--clean",
                      action = "store",
                      dest = "clean",
                      default = 0,
                      help = "Strips string and <> uri designations")

    (options, args) = parser.parse_args()

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

        if options.output_file_name:
            try:
                fo = open(options.output_file_name,'w')
            except IOError:
                raise

        else:
            fo = StringIO.StringIO()


        if options.command == "statistics":

            fo.write('Loading "%s"\n' % os.path.abspath(file_name))
            start_time = time.clock()
            ts.load_ntriples(f)
            end_time = time.clock()
            fo.write("Finished loading ntriples file\n")

            number_of_triples = ts.n_triples()
            Nt = number_of_triples

            fo.write("Number of triples %s loaded in %s seconds (%s triples/second)\n" % (number_of_triples, end_time - start_time,(number_of_triples * 1.0)/ (end_time - start_time)))

            object_breakdown = ts.simple_pattern_match([("s","p","o")],[],[pyTripleSimple.is_literal("o")])

            number_of_literals = 0
            for result in object_breakdown:
                if result[0][0] == '"1"':
                    number_of_literals = result[1]
            Nl = number_of_literals

            number_of_objects = number_of_triples - number_of_literals
            No = number_of_objects

            rdf_type_breakdown = ts.simple_pattern_match([("a","r","c")], [("r","in",["<" + pyTripleSimple.common_prefixes["rdf"] + "type>"])],["r"])

            if len(rdf_type_breakdown):
                number_of_instances = rdf_type_breakdown[0][1]
            else:
                number_of_instances = 0

            Ni = number_of_instances

            number_of_symbols = ts.n_symbols()
            Ns = number_of_symbols

            number_of_distinct_literals = ts.n_literals()
            Ndl = number_of_distinct_literals

            classes_results = ts.simple_pattern_match( [("a","r","c")], [("r","in",["<" + pyTripleSimple.common_prefixes["rdf"] + "type>"])],["c"])
            number_of_distinct_classes = len(classes_results)
            Ndc = number_of_distinct_classes

            number_of_distinct_objects = ts.n_objects() - number_of_distinct_literals
            Ndo = number_of_distinct_objects

            number_of_distinct_subjects = ts.n_subjects()
            Nds = number_of_distinct_subjects

            number_of_distinct_predicates = ts.n_predicates()
            Ndp = number_of_distinct_predicates

            subject_uris = ts.simple_pattern_match([("s","p","o")],[],["s"])
            object_uris = ts.simple_pattern_match([("s","p","o")],[],["o"])

            subject_objects_literals_uris = ts.union_pattern_match_result_set(subject_uris,object_uris)

            subject_objects_uris = [uresult for uresult in subject_objects_literals_uris if uresult[0][0][0] != '"' and uresult[0][0][-1]]

            number_of_distinct_uris = len(subject_objects_uris)
            Nu = number_of_distinct_uris


            class_coverage = [(class_result[1] * 1.0)/Ni for class_result in classes_results]

            fo.write("\n")
            fo.write("Number of triples (Nt): %s\n" % number_of_triples)
            fo.write("Number of literals (Nl): %s\n" % number_of_literals)
            fo.write("Number of objects (No): %s\n" % number_of_objects)
            fo.write("Number of typed instances (Ni): %s\n" % number_of_instances)

            fo.write("Number of URIs excluding predicates (Nu): %s\n" % number_of_distinct_uris)
            fo.write("Number of distinct classes (Nc): %s\n" % number_of_distinct_classes)

            fo.write("Number of distinct subjects (Nds): %s\n" % number_of_distinct_subjects)
            fo.write("Number of distinct predicates (Ndp): %s\n" % number_of_distinct_predicates)

            fo.write("Number of distinct objects (Ndo): %s\n" % number_of_distinct_objects)

            fo.write("Number of distinct literals (Ndl): %s\n" % number_of_distinct_literals)
            fo.write("Number of distinct lexical symbols (Ndls): %s\n" % number_of_symbols)

            fo.write("\n")
            fo.write("Literalness (Nl/Nt): %s\n" % ((Nl * 1.0) / Nt))
            fo.write("Literal uniqueness (Ndl/Nl): %s\n" % ((Ndl * 1.0) / Nl))
            fo.write("Object uniqueness (Ndo/No): %s\n" % ((Ndo * 1.0) / No))
            fo.write("Interconnectedness (1 - (Nl+Ni)/Nt): %s\n" % (1.0 - (Nl + Ni) / (Nt * 1.0)))
            fo.write("Subject coverage (Nds/Nu): %s\n" % ((1.0 * Nds) / Nu))
            fo.write("Object coverage (Ndo/Nu): %s\n" % ((1.0 * Ndo) / Nu))
            fo.write("Class coverage: %s\n" % class_coverage)

            #fo.write("Fraction of objects that are literals: %s\n" % ((number_of_distinct_literals * 1.0) / number_of_distinct_objects))
            fo.write("\n")
            fo.write("Top subjects are:\n")
            pprint.pprint(ts.top_subjects(display_n),fo)
            fo.write("\n")
            fo.write("Top objects are:\n")
            pprint.pprint(ts.top_objects(display_n),fo)
            fo.write("\n")
            fo.write("Top predicates are:\n")
            pprint.pprint(ts.top_predicates(None),fo)
            fo.write("\n")
            fo.write("Top classes are:\n")

            pprint.pprint(classes_results,fo)

        elif options.command == "query":
            ts.load_ntriples(f)
            query = eval(options.query)
            if options.restrictions:
                restrictions = eval(options.restrictions)
            else:
                restrictions = []
            if options.variables:
                solution_variables = eval(options.variables)
            else:
                solution_variables = None

            result_set = ts.simple_pattern_match(query, restrictions, solution_variables)

            if display_n == "All":
                pass
            else:
                result_set = result_set[:display_n]

            if options.output_format == "stdout":
                pprint.pprint(result_set, fo)
                fo.write("Query returned %s results" % len(result_set))
            elif options.output_format == "ntriples":
                for result in result_set:
                    i = 1
                    for solution in result[0]:
                        if i % 3 == 1:
                            fo.write(result[0][0] + " ")
                        elif i % 3 == 2:
                            fo.write(result[0][1] + " ")
                        elif i % 3 == 0:
                            fo.write(result[0][2] + " .\n")
                        i += 1

            elif options.output_format == "json":
                import json
                json.dump(result_set, fo)
            elif options.output_format == "delimited":
                header = options.header
                delimiter = options.delimiter
                string_tab = ""
                if header:
                    if len(result_set):
                        for solution_variable in solution_variables:
                            fo.write("%s%s" % (solution_variable, delimiter))
                        fo.write("count\n")
                else:
                    pass

                for result in result_set:
                    for solution in result[0]:
                        if options.clean:
                            if len(solution):
                                solution = solution[1:-1]
                        fo.write("%s%s" % (solution, delimiter))
                    fo.write("%s\n" % result[1])

        if options.output_file_name:
            pass
        else:
            print(fo.getvalue())

        fo.close()


if __name__ == "__main__":
    main()