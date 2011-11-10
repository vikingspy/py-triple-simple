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
        self.assertEquals(30,len(result2),"Wrong number of triples iterated")


    def test_find_triples(self):
        ts = pyTripleSimple.SimpleTripleStore()
        ts.load_ntriples(self.test_source)

        r1 = ts.find_triples(subjects="<http://example.org/resource999>")
        self.assertEquals(set([]),r1,"Should return an empty list")

        r2  = ts.find_triples(subjects="<http://example.org/resource9>")
        self.assertEquals(1,len(r2))

        r3 = ts.find_triples(predicates="http://example.org/property")
        self.assertEquals(30,len(r3))

        r4 = ts.find_triples(objects="<http://example.org/resource2>")
        self.assertEquals(7,len(r4))

        r5 = ts.find_triples(literals="chat")
        self.assertEquals(3,len(r5))

        r6 = ts.find_triples(subjects=['<http://example.org/resource26>','http://example.org/resource25'])
        self.assertEquals(3,len(r6))

        r7 = ts.find_triples(subjects=['<http://example.org/resource26>','http://example.org/resource25'], predicates="<http://example.org/property>")
        self.assertEquals(3,len(r7))

        r8 = ts.find_triples(['<http://example.org/resource26>','http://example.org/resource25'], predicates="<http://example.org/propertyX>")
        self.assertEquals(0,len(r8))

        r9 = ts.find_triples("<http://example.org/resource14>", "<http://example.org/property>", literals="x")
        self.assertEquals(1,len(r9))

        r10 = ts.find_triples("<http://example.org/resource14>", "<http://example.org/property>", objects="x")
        self.assertEquals(0,len(r10))

class  TestTriplePatterns(unittest.TestCase):
    def setup(self):
        pass
    def test_patterns(self):
        pattern1 = [('a','b','c')]
        pattern_obj1 = pyTripleSimple.TriplePatterns(pattern1)

        self.assertEquals(3,len(pattern_obj1.variables))

        pattern2 = [('a','b','c','d','e')]
        pattern_obj2 = pyTripleSimple.TriplePatterns(pattern2)
        self.assertEquals(2,len(pattern_obj2.checked_patterns))

        self.assertEquals(5,len(pattern_obj2.variables))

        print(pattern_obj2.variables)

        pattern3 = [('a','b','c','d','e','f','g')]
        pattern_obj3 = pyTripleSimple.TriplePatterns(pattern3)
        self.assertEquals(3,len(pattern_obj3.checked_patterns))

class  TestTripleRestrictions(unittest.TestCase):
    def setup(self):
        pass
    def test_restrictions(self):
        restrictions1 = [("a","!=","b"),("a", "in", ("<http://example.org/1>","<http://example.org/2>"))]
        restrictions1_obj = pyTripleSimple.TripleRestrictions(restrictions1)


if __name__ == '__main__':
    unittest.main()