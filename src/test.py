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
