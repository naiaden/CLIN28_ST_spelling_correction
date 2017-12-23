from lm import LanguageModel
import utils
import inspect
import correctors
import collections

def test_register(cls):
    cls._propdict = {}
    for methodname in dir(cls):
        method = getattr(cls, methodname)
        if hasattr(method, '_prop'):
            cls._propdict.update({methodname: method})
    return cls

def register(*args):
    def wrapper(func):
        func._prop = args
        return func
    return wrapper

@test_register
class TestSuite():
    def __init__(self, lm):
        self.lm = lm
        self.verbose = True

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
        
        result = correction[0] and self.lm.ts(correction[2]['text']) == truth
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
        for function, args in self._propdict.items():
            getattr(self, function)()
    
    @register()
    def test_pattern(self):
        self.assertEqual("s1", self.lm.ts(self.lm.bp("mogelijkheden")), "mogelijkheden")
        self.assertEqual("s2", self.lm.ts(self.lm.bp("qwem,n82")), "{?}")
        self.assertNotEqual("s3", self.lm.ts(self.lm.bp("mogelijkheden")), "{?}")

    @register()
    def test_counts(self):
        self.assertTrue("s1", self.lm.oc("mogelijkheden") > 0)
        self.assertTrue("s2", self.lm.oc(self.lm.bp("mogelijkheden")) > 0)
        
        self.assertTrue("s3", self.lm.fr("mogelijkheden") > 0)
        self.assertTrue("s4", self.lm.fr(self.lm.bp("mogelijkheden")) > 0)
        
        self.assertFalse("s5", self.lm.oc("asdgfafzxcv2") > 0)
        self.assertFalse("s6", self.lm.oc(self.lm.bp("asdgfafzxcv2")) > 0)
        
        self.assertFalse("s7", self.lm.fr("asdgfafzxcv2") > 0)
        self.assertFalse("s8", self.lm.fr(self.lm.bp("asdgfafzxcv2")) > 0)
    
    @register()
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
        
        s14 = utils.cs(self.lm, "is een kleur loos edelgas", "page1144.text.p.1.s.2.w.4")
        self.assertCorrection("s14", splitter.correct(s14), "kleurloos")

    @register()
    def test_missing(self):
        inserter = correctors.Inserter(self.lm)
    
        s1 = utils.cs(self.lm, "meestal gesloten , volgen", "page1027.text.div.1.div.6.p.1")
        self.assertCorrection("s1", inserter.correct(s1), "dan nog")
        
        s2 = utils.cs(self.lm, "geregeld leven en hij zich", "page1065.text.div.3.p.1.s.4")
        self.assertCorrection("s2", inserter.correct(s2), "kon")
        
        s3 = utils.cs(self.lm, "gekend volkse tafereel . Het", "page1065.text.div.4.p.3.s.7")
        self.assertCorrection("s3", inserter.correct(s3), "is")
        
        s4 = utils.cs(self.lm, "voor veel componisten met hem", "page1310.text.p.2.s.2")
        self.assertCorrection("s4", inserter.correct(s4), "zowel")
        
        s5 = utils.cs(self.lm, "korte koraalvoorspelen voor orgel -", "page1310.text.div.1.p.1.s.8")
        self.assertCorrection("s5", inserter.correct(s5), "het")
        
        s6 = utils.cs(self.lm, "' suites voor klavecimbel .", "page1310.text.div.1.div.2.p.3.s.1")
        self.assertCorrection("s6", inserter.correct(s6), "de")
        
        s7 = utils.cs(self.lm, "persoonlijke koraalvoorspelenboekje voor orgel uit", "page1310.text.div.1.div.2.p.6.s.1")
        self.assertCorrection("s7", inserter.correct(s7), "het")
        
        s8 = utils.cs(self.lm, "en kleine terts-toonsoorten zijn geschreven", "page1310.text.div.1.div.2.p.6.s.3")
        self.assertCorrection("s8", inserter.correct(s8), "in")
        
        s9 = utils.cs(self.lm, "en de alom Leipziger Messe", "page1310.text.div.1.div.3.p.1.s.1")
        self.assertCorrection("s9", inserter.correct(s9), "bekende")
        
        s10 = utils.cs(self.lm, "( circa 200 ) bewaard", "page1310.text.div.1.div.3.p.1.s.3")
        self.assertCorrection("s10", inserter.correct(s10), "cantates")
        
        s11 = utils.cs(self.lm, "zijn dood raakten componist en", "page1310.text.div.3.p.2.s.1")
        self.assertCorrection("s11", inserter.correct(s11), "de")
        
        s12 = utils.cs(self.lm, "Zijn stijl werd ouderwets beschouwd", "page1310.text.div.5.div.1.p.1.s.2")
        self.assertCorrection("s12", inserter.correct(s12), "als")
    
    # grep -B 1 -A 5 "capitalization" ../data/validation/page*.json
    # grep -B 13 -A 16 '"id": "page1.text.div.2.p.1.s.5.w.30"' ~/Programming/COCOCLINSPCO/data/validation/page*.json
    @register()
    def test_capitalization(self):
        replacer = correctors.Replacer(self.lm)
    
        s1 = utils.cs(self.lm, "eeuw de Moslims kwamen oordeelde", "page1008.text.div.1.p.3.s.4")
        self.assertCorrection("s1", replacer.correct(s1), "moslims")
        
        s2 = utils.cs(self.lm, "In de Islamitische wereld bouwde", "page1008.text.div.2.p.1.s.1")
        self.assertCorrection("s2", replacer.correct(s2), "islamitische")
        
        s3 = utils.cs(self.lm, "In de Middeleeuwen werden opnieuw", "page1008.text.div.2.p.2.s.1")
        self.assertCorrection("s3", replacer.correct(s3), "middeleeuwen")
        
        s4 = utils.cs(self.lm, "In de Renaissance verspreidde zich", "page1008.text.div.2.p.2.s.2")
        self.assertCorrection("s4", replacer.correct(s4), "renaissance")
        
        s5 = utils.cs(self.lm, "God of Goden ? En", "page1014.text.div.1.div.1.list.1.item.1.s.1")
        self.assertCorrection("s5", replacer.correct(s5), "goden")
        
        s6 = utils.cs(self.lm, "God / God(en) en de", "page1014.text.div.1.div.1.p.2.s.1")
        self.assertCorrection("s6", replacer.correct(s6), "god(en)")
        
        s7 = utils.cs(self.lm, ". De Kabbala , de", "page1014.text.div.1.div.1.list.2.item.10.s.2")
        self.assertCorrection("s7", replacer.correct(s7), "kabbala")
        
        s8 = utils.cs(self.lm, ", de Joodse mystiek ,", "page1014.text.div.1.div.1.list.2.item.10.s.2")
        self.assertCorrection("s8", replacer.correct(s8), "joodse")
        
        s9 = utils.cs(self.lm, ". ( zie ook God", "page1014.text.div.1.div.2.p.2.s.4")
        self.assertCorrection("s9", replacer.correct(s9), "Zie")
        
        s10 = utils.cs(self.lm, "schepper ) Abrahamitisch-monotheïstische eigenschappen van", "page1014.text.div.1.div.2.p.2.s.4")
        self.assertCorrection("s10", replacer.correct(s10), "abrahamitisch-monotheïstische")
        
        s11 = utils.cs(self.lm, "tot het Zoroastrisme zoals grondgelegd", "page1014.text.div.1.div.2.p.3.s.1")
        self.assertCorrection("s11", replacer.correct(s11), "zoroastrisme")
        
        s12 = utils.cs(self.lm, "Neopaganisten , Wicca-aanhangers in het", "page1014.text.div.1.div.3.p.1.s.4")
        self.assertCorrection("s12", replacer.correct(s12), "wicca-aanhangers")
        
        s13 = utils.cs(self.lm, "of de Paus , en", "page1014.text.div.1.div.4.p.1.s.1")
        self.assertCorrection("s13", replacer.correct(s13), "paus")
        
        s14 = utils.cs(self.lm, "van die Ene God .", "page1014.text.div.1.div.4.p.2.s.2")
        self.assertCorrection("s14", replacer.correct(s14), "ene")
        
        s15 = utils.cs(self.lm, "De Haagse school is ontstaan", "page1020.text.p.1.s.1")
        self.assertCorrection("s15", replacer.correct(s15), "School")
        
        s16 = utils.cs(self.lm, "Feestdagen en Schoolvakanties in 2011", "page1027.text.div.8.list.1.item.1.s.1")
        self.assertCorrection("s16", replacer.correct(s16), "schoolvakanties")
        
        s17 = utils.cs(self.lm, "Verzamelhobbies verzamelen Filatelie , Modeltrein", "page1037.text.list.1.item.4.p.1.s.1")
        self.assertCorrection("s17", replacer.correct(s17), "filatelie")
        
        s18 = utils.cs(self.lm, "van de olympische spelen in", "page1.text.div.2.p.1.s.5")
        self.assertCorrection("s18", replacer.correct(s18), "Olympische")
        
        s19 = utils.cs(self.lm, "van de olympische Spelen in Peking", "page1.text.div.2.p.1.s.5")
        self.assertCorrection("s19", replacer.correct(s19), "Spelen")
        
        s20 = utils.cs(self.lm, "van de Olympische Spelen in Peking", "page1.text.div.2.p.1.s.5")
        self.assertCorrection("s20", replacer.correct(s20), "Spelen")
    
    @register()
    def test_runon(self):
        attacher = correctors.Attacher(self.lm)
    
        s1 = utils.cs(self.lm, "De boeken - meest papyrusrollen", "page1008.text.div.1.p.3.s.5.w.3")
        #self.assertCorrection("s1", attacher.correct(s1), "- vooral")
        
        s2 = utils.cs(self.lm, "geest , etcetera ) .", "page1014.text.div.1.div.5.p.2.s.4.w.43")
        self.assertCorrection("s2", attacher.correct(s2), "et cetera") 
        
        s3 = utils.cs(self.lm, "Poort Het Teylersmuseum ( het", "page1041.text.list.1.item.4.s.1.w.2")
        self.assertCorrection("s3", attacher.correct(s3), "Teylers museum")
        
        s4 = utils.cs(self.lm, "orgeltabulatuur ) van twee grote", "page1310.text.div.1.p.2.s.2.w.26")
        # geen spatie na )
        # van
        
        s5 = utils.cs(self.lm, "Blasiikirche . Begin-1708 voerde Bach", "page1310.text.div.1.p.4.s.2.w.1")
        self.assertCorrection("s5", attacher.correct(s5), "Begin 1708")
        
        s6 = utils.cs(self.lm, "naar deze vacant-geworden positie te", "page1310.text.div.1.div.2.p.5.s.3.w.46")
        self.assertCorrection("s6", attacher.correct(s6), "vacant geworden")
        
        s7 = utils.cs(self.lm, "scheikundig element metsymbool He en", "page1144.text.p.1.s.1")
        self.assertCorrection("s7", attacher.correct(s7), "met symbool")
    
    @register()
    def test_replace(self):
        pass
        

