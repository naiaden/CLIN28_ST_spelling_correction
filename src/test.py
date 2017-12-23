from lm import LanguageModel
import utils
import inspect
import correctors
import collections

class TestSuite():
    def __init__(self, lm):
        self.lm = lm
        self.verbose = False

    results = {}

    def updateResults(self, caller, test_id, result):
        if caller not in self.results:
            self.results[caller] = {}
    
        if test_id in self.results[caller]:
            print("FIX YOUR DOUBLE TEST IDS")
        else:
            self.results[caller][test_id] = result

    def assertEqual(self, test_id, a, b):
        caller = inspect.currentframe().f_back.f_code.co_name
                
        result = a==b
        self.updateResults(caller, test_id, result)
        
            
    def assertNotEqual(self, test_id, a, b):
        caller = inspect.currentframe().f_back.f_code.co_name
        
        result = a!=b
        self.updateResults(caller, test_id, result)
  
    def assertTrue(self, test_id, a):
        caller = inspect.currentframe().f_back.f_code.co_name
        
        result = a
        self.updateResults(caller, test_id, result)
    
    def assertFalse(self, test_id, a):
        caller = inspect.currentframe().f_back.f_code.co_name
        
        result = not a
        self.updateResults(caller, test_id, result)

    def assertCorrection(self, test_id, correction, truth):
        caller = inspect.currentframe().f_back.f_code.co_name
        
        result = correction[0] and self.lm.ts(correction[1]) == truth
        self.updateResults(caller, test_id, result)
    
    def assertNoCorrection(self, test_id, correction):
        caller = inspect.currentframe().f_back.f_code.co_name
        
        result = not correction[0]
        self.updateResults(caller, test_id, result)
        
    def reset(self):
        self.results = {}

    def report(self):
        total_pass = 0
        total_all = 0
        for caller, tests in self.results.items():
            caller_pass = 0
            caller_all = 0
            for testid, result in tests.items():
                if self.verbose:
                    print("\t[" + caller +":" + testid + "]\t" + str(result))
                caller_all += 1
                total_all += 1
                if result:
                    caller_pass += 1
                    total_pass += 1
            print("[" + caller + "]\tPASS: " + str(caller_pass) + "\tFAIL:" + str(caller_all - caller_pass) )
        print("[-ALL-]\tPASS: " + str(total_pass) + "\tFAIL:" + str(total_all - total_pass) )
            
    def run_tests(self):
        self.test_pattern()
        self.test_counts()
        self.test_split()
        self.test_missing()
        self.test_runon()

    def test_pattern(self):
        self.assertEqual("s1", self.lm.ts(self.lm.bp("mogelijkheden")), "mogelijkheden")
        self.assertEqual("s2", self.lm.ts(self.lm.bp("qwem,n82")), "{?}")
        self.assertNotEqual("s3", self.lm.ts(self.lm.bp("mogelijkheden")), "{?}")

    def test_counts(self):
        self.assertTrue("s1", self.lm.oc("mogelijkheden") > 0)
        self.assertTrue("s2", self.lm.oc(self.lm.bp("mogelijkheden")) > 0)
        
        self.assertTrue("s3", self.lm.fr("mogelijkheden") > 0)
        self.assertTrue("s4", self.lm.fr(self.lm.bp("mogelijkheden")) > 0)
        
        self.assertFalse("s5", self.lm.oc("asdgfafzxcv2") > 0)
        self.assertFalse("s6", self.lm.oc(self.lm.bp("asdgfafzxcv2")) > 0)
        
        self.assertFalse("s7", self.lm.fr("asdgfafzxcv2") > 0)
        self.assertFalse("s8", self.lm.fr(self.lm.bp("asdgfafzxcv2")) > 0)
        
    def test_split(self):
        splitter = correctors.Splitter(self.lm)
    
        s1 = utils.cs(self.lm, ", die er naar streefden", "page1020.text.p.1.s.2")
        self.assertCorrection("s1", splitter.correct(s1), "ernaar")
        
        s2 = utils.cs(self.lm, "de experimentele Cobra -beweging ,", "page1020.text.div.1.p.1.s.1")
        self.assertCorrection("s2", splitter.correct(s2), "Cobra-beweging")
        
        s3 = utils.cs(self.lm, "het Franse Barbizon -gebeuren en", "page1020.text.p.1.s.2")
        self.assertCorrection("s3", splitter.correct(s3), "Barbizon-gebeuren")
        
        s4 = utils.cs(self.lm, "bezetting ) als ook de", "page1310.text.div.1.p.3.s.3")
        self.assertCorrection("s4", splitter.correct(s4), "alsook")
        
        s5 = utils.cs(self.lm, "nu , dank zij hem", "page1065.text.div.4.p.2.s.6")
        self.assertCorrection("s5", splitter.correct(s5), "dankzij")
        
        s6 = utils.cs(self.lm, "onder Japan weg duikt .", "page1291.text.div.6.div.1.p.2.s.2")
        self.assertCorrection("s6", splitter.correct(s6), "wegduikt")
        
        s7 = utils.cs(self.lm, "Mozart een motet -uitvoering (", "page1310.text.div.5.div.1.p.1.s.6")
        self.assertCorrection("s7", splitter.correct(s7), "motetuitvoering")
        
        s8 = utils.cs(self.lm, "zee , gebruik makend van", "page1310.text.div.5.div.1.p.1.s.9")
        self.assertCorrection("s8", splitter.correct(s8), "gebruikmakend")
        
        s9 = utils.cs(self.lm, ". Philipp Spitta 's biografie", "page1310.text.div.5.div.1.p.2.s.2")
        self.assertCorrection("s9", splitter.correct(s9), "Spitta's")
        
        s10 = utils.cs(self.lm, "en van Stravinsky 's versie", "page1310.text.div.5.div.2.p.2.s.6")
        self.assertCorrection("s10", splitter.correct(s10), "Stravinsky's")
        
        s11 = utils.cs(self.lm, "majeur en mineur toonsoort .", "page1310.text.div.7.div.1.p.1.s.3")
        self.assertCorrection("s11", splitter.correct(s11), "mineurtoonsoort")
        
        s12 = utils.cs(self.lm, "van de hindoe filosofie )", "page1014.text.div.1.div.4.p.3.s.1")
        self.assertCorrection("s12", splitter.correct(s12), "hindoefilosofie")
        
        s13 = utils.cs(self.lm, "elkaar ontdekt . </s> </s>", "page1144.text.div.1.p.1.s.1")
        self.assertNoCorrection("s13", splitter.correct(s13))

    def test_missing(self):
        s1 = utils.cs(self.lm, "meestal gesloten , volgen", "page1027.text.div.1.div.6.p.1")
        # dan nog
        
        s2 = utils.cs(self.lm, "geregeld leven en hij zich", "page1065.text.div.3.p.1.s.4")
        # kon
        
        s3 = utils.cs(self.lm, "gekend volkse tafereel . Het", "page1065.text.div.4.p.3.s.7")
        # is
        
        s4 = utils.cs(self.lm, "voor veel componisten met hem", "page1310.text.p.2.s.2")
        # zowel
        
        s5 = utils.cs(self.lm, "korte koraalvoorspelen voor orgel -", "page1310.text.div.1.p.1.s.8")
        # het
        
        s6 = utils.cs(self.lm, "' suites voor klavecimbel .", "page1310.text.div.1.div.2.p.3.s.1")
        # de
        
        s7 = utils.cs(self.lm, "persoonlijke koraalvoorspelenboekje voor orgel uit", "page1310.text.div.1.div.2.p.6.s.1")
        # het
        
        s8 = utils.cs(self.lm, "en kleine terts-toonsoorten zijn geschreven", "page1310.text.div.1.div.2.p.6.s.3")
        # in
        
        s9 = utils.cs(self.lm, "en de alom Leipziger Messe", "page1310.text.div.1.div.3.p.1.s.1")
        # bekende
        
        s10 = utils.cs(self.lm, "( circa 200 ) bewaard", "page1310.text.div.1.div.3.p.1.s.3")
        # cantates
        
        s11 = utils.cs(self.lm, "zijn dood raakten componist en", "page1310.text.div.3.p.2.s.1")
        # de
        
        s12 = utils.cs(self.lm, "Zijn stijl werd ouderwets beschouwd", "page1310.text.div.5.div.1.p.1.s.2")
        # als
    
    def test_runon(self):
        s1 = utils.cs(self.lm, "De boeken - meest papyrusrollen", "page1008.text.div.1.p.3.s.5.w.3")
        #self.assertCorrection("s1", splitter.correct(s1), "- vooral")
        
        s2 = utils.cs(self.lm, "geest , etcetera ) .", "page1014.text.div.1.div.5.p.2.s.4.w.43")
        # et cetera
        
        s3 = utils.cs(self.lm, "Poort Het Teylersmuseum ( het", "page1041.text.list.1.item.4.s.1.w.2")
        # Teylers museum
        
        s4 = utils.cs(self.lm, "orgeltabulatuur ) van twee grote", "page1310.text.div.1.p.2.s.2.w.26")
        # geen spatie na )
        # van
        
        s5 = utils.cs(self.lm, "Blasiikirche . Begin-1708 voerde Bach", "page1310.text.div.1.p.4.s.2.w.1")
        # Begin 1708
        
        s6 = utils.cs(self.lm, "naar deze vacant-geworden positie te", "page1310.text.div.1.div.2.p.5.s.3.w.46")
        # vacant geworden
        
        s7 = utils.cs(self.lm, "is een kleur loos edelgas", "page1144.text.p.1.s.2.w.4")
        #self.assertCorrection("s7", splitter.correct(s7), "kleurloos")
    
    def test_replace(self):
        pass
        

