# To change this template, choose Tools | Templates
# and open the template in the editor.

import unittest
from xml.etree.ElementTree import XMLParser
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

    def test_EmbeddedQuote(self):
        ts = pyTripleSimple.SimpleTripleStore()
        ts.load_ntriples([r'<http://link.informatics.stonybrook.edu/umls/SUI/S7018982> <http://www.w3.org/2000/01/rdf-schema#label> "Instruct parent/caregiver of infant 0-3 months to limit water intake to Z\\\"x oz to 1 oz at a time, 4 oz daily" .',
                          r'<http://link.informatics.stonybrook.edu/umls/SUI/S11718919> <http://www.w3.org/2000/01/rdf-schema#label> "Vetscription Worm Away 7 Praziquantel 30 MG \\\" Pyrantel Pamoate 30 MG Chewable Tablet" .'])
        triples = list(ts.iterator_triples())
        self.assertEquals(triples[0].object,r"Instruct parent/caregiver of infant 0-3 months to limit water intake to Z\\\"x oz to 1 oz at a time, 4 oz daily")
        self.assertEquals(triples[1].object,r"Vetscription Worm Away 7 Praziquantel 30 MG \\\" Pyrantel Pamoate 30 MG Chewable Tablet")
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

    def test_simple_pattern_match(self):
        ts = pyTripleSimple.SimpleTripleStore()
        f = open("acme.nt","r")
        ts.load_ntriples(f)

        r1 = ts.simple_pattern_match([("a","p","b")],[("p","in",["<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"])],("b"))
        self.assertEquals(5,len(r1))

        r2 = ts.simple_pattern_match([("a","p","b")],[("p","in",["<http://example.org/predicateDoesNotExist>"])],("b"))
        self.assertEquals(0,len(r2))

        r3 = ts.simple_pattern_match([("a","p","b"),("a","r","ca"),("b","r","cb")],[("r","in",["<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"])],("p","ca","cb"))
        self.assertEquals(5,len(r3))

        r4 = ts.simple_pattern_match([("a","p","b"),("a","r","ca"),("b","r","cb")],[("p", "!=", "r"),("r","in",["<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"])],("p","ca","cb"))
        self.assertEquals(2,len(r4))

        r5 = ts.simple_pattern_match([('a','p','b')], [],['a','p','b'])
        self.assertEquals(57,len(r5))

        r6 = ts.simple_pattern_match([('a','p','b')], [('p','in',['<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>'])],['a','p','b'])
        self.assertEquals(14,len(r6))

        r7 = ts.simple_pattern_match([('a','p','b')], [('p','not in',['<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>'])],['a','p','b'])
        self.assertEquals(57 - 14,len(r7))

        r8 = ts.simple_pattern_match([('a','p','b')], [('b','in',['Hollywood'])],['a','p','b'])
        self.assertEquals(2,len(r8))

        r9 = ts.simple_pattern_match([('a','p','b')], [('b','not in',['Hollywood'])],['a','p','b'])
        self.assertEquals(57 - 2,len(r9))

        r10 = ts.simple_pattern_match([('s','p','o')],[],[pyTripleSimple.is_literal('o')])
        self.assertEquals(2,len(r10))


class  TestTriplePatterns(unittest.TestCase):
    def setup(self):
        pass
    def test_patterns(self):
        pattern1 = [('a','b','c')]
        pattern_obj1 = pyTripleSimple.TriplePatterns(pattern1)

        self.assertEquals(3,len(pattern_obj1.variables_dict))

        pattern2 = [('a','b','c','d','e')]
        pattern_obj2 = pyTripleSimple.TriplePatterns(pattern2)
        self.assertEquals(2,len(pattern_obj2.checked_patterns))

        self.assertEquals(5,len(pattern_obj2.variables_dict))

        pattern3 = [('a','b','c','d','e','f','g')]
        pattern_obj3 = pyTripleSimple.TriplePatterns(pattern3)
        self.assertEquals(3,len(pattern_obj3.checked_patterns))

        pattern4 = [("a","p","b"),("a","r","ca"),("b","r","cb")]
        pattern_obj4 = pyTripleSimple.TriplePatterns(pattern4)

        self.assertEquals(1, pattern_obj4.variables()["p"])
        self.assertEquals(2, pattern_obj4.variables()["b"])
        self.assertEquals(0, pattern_obj4.variables()["a"])

class  TestTripleRestrictions(unittest.TestCase):
    def setup(self):
        pass
    def test_restrictions(self):
        restrictions1 = [("a","!=","b"),("a", "in", ("<http://example.org/1>","<http://example.org/2>"))]
        restrictions1_obj = pyTripleSimple.TripleRestrictions(restrictions1)

        restrictions2 = [("a","!=","b"),("a", "in", ["<http://example.org/1>","<http://example.org/2>"])]
        restrictions2_obj = pyTripleSimple.TripleRestrictions(restrictions2)

        restrictions3 = [("a","!=","b"),("a", "in", [""])]
        restrictions3_obj = pyTripleSimple.TripleRestrictions(restrictions3)

class TestExtractGraphFromSimpleTripleStore(unittest.TestCase):
    def setup(self):
        pass
    def test_generate_graphml(self):
        self.ts = pyTripleSimple.SimpleTripleStore()
        f = open("acme.nt")
        self.ts.load_ntriples(f)
        f.close()
        egfrsts_obj = pyTripleSimple.ExtractGraphFromSimpleTripleStore(self.ts)
        egfrsts_obj.register_label()
        egfrsts_obj.register_class()
        egfrsts_obj.add_pattern_for_links([['a','b','c']],[('b','in',['<http://acme.com/rdf#isLabeller>'])],("a","c"), "labeller")
        result_xml = egfrsts_obj.translate_into_graphml_file()

        from xml.etree.ElementTree import XML
        elements = XML(result_xml)
        xml_tags = []
        for element in elements:
            xml_tags.append(element.tag)
        self.assertTrue("{http://graphml.graphdrawing.org/xmlns}key" in xml_tags)
        self.assertTrue("{http://graphml.graphdrawing.org/xmlns}graph" in xml_tags)

        try:
            import networkx
            fo = open("acme.graphml","w")
            fo.write(result_xml)
            fo.close()
            networkx.read_graphml("acme.graphml")
            f.close()
        except ImportError:
            pass

if __name__ == '__main__':
    unittest.main()

