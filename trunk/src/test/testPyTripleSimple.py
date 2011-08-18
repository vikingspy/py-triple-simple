# To change this template, choose Tools | Templates
# and open the template in the editor.

import unittest
import pyTripleSimple

class  TestPyTripleSimpleTestCase(unittest.TestCase):
    def setUp(self):
        f = open('test.nt','r')
        self.test_source = f
        self.parser = pyTripleSimple.SimpleNtriplesParser()

    def test_PyTripleSimpleStore(self):
        ts = pyTripleSimple.SimpleTripleStore()
        ts.load_ntriples(self.test_source)
        self.assertEquals(30,ts.n_triples(),"Wrong number of triples extracted")

    def test_TripleIterator(self):
        ts = pyTripleSimple.SimpleTripleStore()
        ts.load_ntriples(self.test_source)
        result1 = list(ts.iterator_triples())
        
        self.assertEquals(30,len(result1),"Wrong number of triples iterated")
        result2 = list(ts.iterator_ntriples())
        self.assertEquals(30,len(result1),"Wrong number of triples iterated")
        

if __name__ == '__main__':
    unittest.main()