__author__ = 'Janos G. Hajagos'

import unittest
import FreeTextTriples
import pprint
import pyTripleSimple

try:
    import nltk
except ImportError:
    pass


class testWordExtractionNLTK(unittest.TestCase):
    def setUp(self):
        self.abstract_text = '''The group C of Sry-related high-mobility group (HMG) box (Sox) transcription factors has three members in most vertebrates: Sox4, Sox11 and Sox12. Sox4 and Sox11 have key roles in cardiac, neuronal and other major developmental processes, but their molecular roles in many lineages and the roles of Sox12 remain largely unknown. We show here that the three genes are co-expressed at high levels in neuronal and mesenchymal tissues in the developing mouse, and at variable relative levels in many other tissues. The three proteins have conserved remarkable identity through evolution in the HMG box DNA-binding domain and in the C-terminal 33 residues, and we demonstrate that the latter residues constitute their transactivation domain (TAD). Sox11 activates transcription several times more efficiently than Sox4 and up to one order of magnitude more efficiently than Sox12, owing to a more stable alpha-helical structure of its TAD. This domain and acidic domains interfere with DNA binding, Sox11 being most affected and Sox4 least affected. The proteins are nevertheless capable of competing with one another in reporter gene transactivation. We conclude that the three SoxC proteins have conserved overlapping expression patterns and molecular properties, and might therefore act in concert to fulfill essential roles in vivo.'''


class testBasicWordExtraction(unittest.TestCase):
    def setUp(self):
        self.free_text = """
        Hero. Good Margaret, run thee to the parlour.
    There shalt thou find my cousin Beatrice
    Proposing with the Prince and Claudio.
    Whisper her ear and tell her, I and Ursley
    Walk in the orchard, and our whole discourse
    Is all of her. Say that thou overheard'st us;
    And bid her steal into the pleached bower,
    Where honeysuckles, ripened by the sun,
    Forbid the sun to enter--like favourites,
    Made proud by princes, that advance their pride
    Against that power that bred it. There will she hide her
    To listen our propose. This is thy office.
    Bear thee well in it and leave us alone.
  Marg. I'll make her come, I warrant you, presently.    [Exit.]
  Hero. Now, Ursula, when Beatrice doth come,
    As we do trace this alley up and down,
    Our talk must only be of Benedick.
    When I do name him, let it be thy part
    To praise him more than ever man did merit.
    My talk to thee must be how Benedick
    Is sick in love with Beatrice. Of this matter
    Is little Cupid's crafty arrow made,
    That only wounds by hearsay.""" # - Shakespeare Etext - "Much ado about nothing"

    def test_lex(self):
        lex = FreeTextTriples.FreeTextLexer()
        result = lex.lex(self.free_text)
        #pprint.pprint(result)
        self.assertTrue(len(result))
        self.assertFalse("" in result)

    def test_generate_index(self):
        ts = pyTripleSimple.SimpleTripleStore()
        ts.load_ntriples(open("acme.nt","r"))

        ft = FreeTextTriples.FreeTextSimpleTripleStore(ts)
        ft.generate()
        file_names = ft.write_out_to_ntriples()

        ts_result = pyTripleSimple.SimpleTripleStore()
        ts_result.load_ntriples(open(file_names[0],"r"))
        result_set = list(ts_result.iterator_ntriples())
        self.assertTrue(len(result_set))

    def test_parse_triples(self):
        ft = FreeTextTriples.FreeTextExpander(3)
        string_to_parse1 = "albumin-EPO fusion protein expressed in CHO cell. "
        result = ft.parse(string_to_parse1)
        self.assertTrue("CHO cell" in result[-2])

        ft = FreeTextTriples.FreeTextExpander(3)
        string_to_parse2 = "albumin-EPO fusion protein expressed in CHO cell"
        result = ft.parse(string_to_parse2)
        self.assertTrue("CHO cell" in result[-2])

    def test_expansion_generation(self):
        abstract = "Objective Age is known to influence the risk of both cerebral ischemic lesions and impaired cognitive function. Diabetes mellitus (DM) can also be associated with cognitive impairment. However, there has been no study of neuropsychological performance in association with glucose metabolism status and cerebral ischemic lesions in same-aged, community-dwelling elderly persons. The present study was performed to clarify which cognitive domains are associated with impaired glucose metabolism/DM and whether the association is independent of cerebral ischemic lesions. Subjects and Methods A total of 172 residents in Takahata, Japan, all of whom were 78 years old, were evaluated in multiple domains through neuropsychological tests and brain MR images, as well as a medical check-up including tests for glucose metabolism status and conventional vascular risk factors. Glucose metabolism status was determined by analysis of HbA1c level. Results In multiple regression analyses, performance on a verbal fluency (VF) test and the Trail Making Test-Part B, both of which represent executive function, was associated with HbA1c level, even after adjustment for sex, education, cerebral ischemic lesions, and conventional vascular risk factors. The subjects with DM also showed lower VF scores than did those without DM. Conclusion The results of the present study demonstrate that impaired glucose metabolism, independent of the conventional vascular risk factors and cerebral ischemic lesions, may be associated with a decline in executive function in community-dwelling elderly."
        ts = pyTripleSimple.SimpleTripleStore()
        ts.load_ntriples(['<http://example.org/123> <http://purl.org/ontology/bibo/abstract> "%s" .' % abstract])
        fte = FreeTextTriples.FreeTextExpanderTripleStore(ts, ["http://purl.org/ontology/bibo/abstract"])
        fte.generate()
        file_names = fte.write_out_to_ntriples()

        ts_result = pyTripleSimple.SimpleTripleStore()
        ts_result.load_ntriples(open(file_names[0],"r"))
        result_set = list(ts_result.iterator_triples())
        self.assertTrue(len(result_set))
        self.assertTrue(result_set[-1].object,"community-dwelling elderly" )


    def test_align_ntriples(self):
        align_ntriples = FreeTextTriples.align_ntriples("article_titles.nt","suis_to_align.nt", ["http://purl.org/dc/elements/1.1/title"] )

if __name__ == '__main__':
    unittest.main()
