# To change this template, choose Tools | Templates
# and open the template in the editor.

import unittest
import pyTripleSimple
import pprint

class  TestPyTripleSimpleTestCase(unittest.TestCase):
    def setUp(self):
        f = open('test.nt','r')
        self.test_source = f
        self.parser = pyTripleSimple.SimpleNtripleExtractor()

    def test_testPyTripleSimpleParser(self):
        pass

    def test_testPyTripleSimpleStore(self):
        ts = pyTripleSimple.SimpleTripleStore()
        ts.load_ntriples(self.test_source)
        
        
#print(ts.export_to_ntriples_string())
        
        self.assertEquals(30,ts.n_triples(),"Wrong number of triples extracted")
        
#        pprint.pprint(ts.te.symbols)
#        pprint.pprint(ts.te.objects)
#        pprint.pprint(ts.te.triples)
#        pprint.pprint(ts.te.subjects_index)
#        pprint.pprint(ts.te.predicates_index)
#        pprint.pprint(ts.te.objects_index)

if __name__ == '__main__':
    unittest.main()