from lm import LanguageModel

import unittest

class TestSuite(unittest.TestCase):
    def __init__(self, lm):
        self.lm = lm

    def test_pattern(self):
        self.assertEqual(self.lm.ts(self.lm.bp("mogelijkheden")), "mogelijkheden")
        self.assertEqual(self.lm.ts(self.lm.bp("qwem,n82")), "{?}")

    def test_counts(self):
        self.assertTrue(self.lm.oc("mogelijkheden") > 0)
        self.assertTrue(self.lm.oc(self.lm.bp("mogelijkheden")) > 0)
        
        self.assertTrue(self.lm.fr("mogelijkheden") > 0)
        self.assertTrue(self.lm.fr(self.lm.bp("mogelijkheden")) > 0)
        
        self.assertFalse(self.lm.oc("asdgfafzxcv2") > 0)
        self.assertFalse(self.lm.oc(self.lm.bp("asdgfafzxcv2")) > 0)
        
        self.assertFalse(self.lm.fr("asdgfafzxcv2") > 0)
        self.assertFalse(self.lm.fr(self.lm.bp("asdgfafzxcv2")) > 0)
        
    def test_split(self):
        s1 = utils.cs(self.lm, ", die er naar streefden", "page1020.text.p.1.s.2"")
        # ernaar
        
        s2 = utils.cs(self.lm, "de experimentele Cobra -beweging ,", "page1020.text.div.1.p.1.s.1")
        # Cobra-beweging
        
        s3 = utils.cs(self.lm, "het Franse Barbizon -gebeuren en", "page1020.text.p.1.s.2")
        # Barbizon-gebeuren
        
        s4 = utils.cs(self.lm, "bezetting ) als ook de", "page1310.text.div.1.p.3.s.3")
        # alsook
        
        s5 = utils.cs(self.lm, "nu , dank zij hem", "page1065.text.div.4.p.2.s.6")
        # dankzij
        
        s6 = utils.cs(self.lm, "onder Japan weg duikt .", "page1291.text.div.6.div.1.p.2.s.2")
        # wegduikt
        
        s7 = utils.cs(self.lm, "Mozart een motet -uitvoering (", "page1310.text.div.5.div.1.p.1.s.6")
        # motetuitvoering
        
        s8 = utils.cs(self.lm, "zee , gebruik makend van", "page1310.text.div.5.div.1.p.1.s.9")
        # gebruikmakend
        
        s9 = utils.cs(self.lm, ". Philipp Spitta 's biografie", "page1310.text.div.5.div.1.p.2.s.2")
        # Spitta's
        
        s10 = utils.cs(self.lm, "en van Stravinsky 's versie", "page1310.text.div.5.div.2.p.2.s.6")
        # Stravinsky's
        
        s11 = utils.cs(self.lm, "majeur en mineur toonsoort .", "page1310.text.div.7.div.1.p.1.s.3")
        # mineurtoonsoort
        
        s12 = utils.cs(self.lm, "van de hindoe filosofie )", "page1014.text.div.1.div.4.p.3.s.1")
        # hindoefilosofie

    def test_missing(self):
        pass
    
    def test_runon(self):
        pass
    
    def test_replace(self):
        pass
