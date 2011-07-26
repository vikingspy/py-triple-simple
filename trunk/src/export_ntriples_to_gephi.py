import pyTripleSimple
import gexf
import sys
import os
import time

class GexfTripleEngine(pyTripleSimple.TripleEngine,gexf.GexfTriples):
    pass


def main(ntriples_file_name, gexf_file_name):
    ts = pyTripleSimple.GexfTripleEngine()
    print('Loading "%s"' % os.path.abspath(ntriples_file_name))
    f = open(ntriples_file_name,"r")
    start_time = time.clock()
    ts.load_ntriples(f)
    end_time = time.clock()
    print("Finished loading ntriples file")
    
    ts.export_to_gexml(gexf_file_name)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(sys.argv[1],sys.argv[2])
    else:
        main("subject_areas_aligned.nt", "subject_areas_aligned.gexf")