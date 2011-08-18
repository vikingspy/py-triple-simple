__author__ = 'Janos G. Hajagos'

import unittest
import FreeTextTriples
#import pprint
import pyTripleSimple

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

if __name__ == '__main__':
    unittest.main()
