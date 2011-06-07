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
        print(ts.export_to_ntriples_string())
        
        self.assertEquals(30,ts.n_triples(),"Wrong number of triples extracted")

if __name__ == '__main__':
    unittest.main()