# To change this template, choose Tools | Templates
# and open the template in the editor.

import unittest
import pyTripleSimple
import pprint

class  TestPyTripleSimpleTestCase(unittest.TestCase):
    def setUp(self):
        f = open('test.nt','r')
        self.test_source = f
        self.parser = pyTripleSimple.SimpleNtriplesParser()

    def test_testPyTripleSimpleStore(self):
        ts = pyTripleSimple.SimpleTripleStore()
        ts.load_ntriples(self.test_source)
        self.assertEquals(30,ts.n_triples(),"Wrong number of triples extracted")

if __name__ == '__main__':
    unittest.main()