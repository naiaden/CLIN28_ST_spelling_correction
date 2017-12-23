import string
import copy
import utils
import Levenshtein
import unidecode

class Corrector:
    def __init__(self, lm):
        self.lm = lm


    def update(self, fivegram):
        self.patterns = utils.patterns(fivegram)
        self.words = utils.words(fivegram)
        self.word_string = utils.word_string(fivegram)
        self.something_happened = False
        self.fivegram = fivegram
        
    def pf_from_cache(self, pattern):
        """
        If candidate is already in the pattern-frequency cache, then retrieve its
        colibricore.Pattern representation and its frequency. Otherwise compute the
        values and put it in the cache first.
        
        >>> pf_from_cache("patroon")
        (<colibricore.Pattern at 0x7f253d1c68d0>, 1.4490891920364536e-05)
        """
        if False and pattern in p_cache:
            (p_candidate, f_candidate) = p_cache[pattern]
        else:
            p_candidate = self.lm.bp(pattern)
            f_candidate = self.lm.fr(p_candidate)
            #p_cache[candidate] = (p_candidate, f_candidate)
        return (p_candidate, f_candidate)


class Replacer(Corrector):
    def __init__(self, lm):
#        """
#        This function tries to find a replaceable in the window 'a b c d e' for word 'c'.
#        It creates a correction with the superclass 'replace', and more specific classes
#        such as 'capitalizationerror', 'redundantpunctuation', 'nonworderror' and the wildcard
#        'replace'. It implicitely also finds archaic and confuseables, but there are shared
#        under the class 'replace'.
#        
#        It follows a backoff strategy, where it starts with window size 5, 2 on the left, 2 on 
#        the right. If there is not a word 'c'' with a higher frequency, then it backs off to 
#        a 3 word window. Analoguously it finally also tries if a word without context might be
#        a better fit if the word 'c' seems to be out-of-vocabulary.
#        
#        Returns a triple (r1, r2, r3) where
#            r1 = a correction has been found,
#            r2 = the 'new' window, with word 'c' being replaced,
#            r3 = the correction.
#            
#        >>> wss = create_internal_sentence(create_sentence("Speer bij de processen van Neurenberg".split(), 'page1.text.div.5.p.2.s.1'))
#        >>> for w in window(wss, 5):
#                print(replaceables_window(w))
#        (False, 'Speer bij de processen van', {'superclass': 'replace', 'class': 'capitalizationerror', 'span': ['page1.text.div.5.p.2.s.1.w.3'], 'text': 'de'})
#        (True, 'bij de Processen van Neurenberg', {'superclass': 'replace', 'class': 'capitalizationerror', 'span': ['page1.text.div.5.p.2.s.1.w.4'], 'text': 'Processen'})
#        """
        super().__init__(lm)
        self.replace_threshold = 5

    def correct(self, fivegram):
        self.update(fivegram)
        return self.correct_()

    def is_year(self, number):
        """ 
        A simple function to test if the input (string or number) is a year (between 1750 and 2100). 
        """
        try:
            number = int(number)
            return number > 1750 and number < 2100
        except (ValueError, TypeError):
            return False; 

    def number_to_text(self, number):
        """ 
        No longer necessary for the shared task; this function converts an integer
        to its lexical string representation if this is according to the rules of OnzeTaal
        (https://onzetaal.nl/taaladvies/getallen-in-letters-of-cijfers/). 
        """
        try:
            if number >=0 and number <= 20:
                return ["nul", "een", "twee", "drie", "vier", "vijf", "zes", "zeven",
                        "acht", "negen", "tien", "elf", "twaalf", "dertien", "veertien",
                        "vijftien", "zestien", "zeventien", "achttien", "negentien", "twintig"][number]
            elif not number%10 and number <= 100:
                return ["dertig", "veertig", "vijftig", "zestig",
                        "zeventig", "tachtig", "negentig", "honderd"][int(number/10)-3]
            elif not number%100 and number <= 1000:
                return ["tweehonderd", "driehonderd", "vierhonderd", "vijfhonderd", "zeshonderd",
                        "zevenhonderd", "achthonderd", "negenhonderd", "duizend"][int(number/100)-2]
            elif not number%1000 and number <= 12000:
                return ["tweeduizend", "drieduizend", "vierduizend", "vijfduizend", "zesduizend", "zevenduizend",
                        "achtduizend", "negenduizend", "tienduizend", "elfduizend", "twaalfduizend"][int(number/1000)-2]
            else:
                return str(number)
        except TypeError:
            return number;

    def correct_(self):
        c = self.words[2]

        best_s = self.word_string
        best_f = self.lm.fr(best_s)
        best_w = c

        # Do not convert 2,5 into 25
        if self.is_year(c) or utils.remove_punct(c).isdigit() or c in string.punctuation:
            return (False, best_s, {})

        local_threshold = self.replace_threshold

        # 2-2 word context
        for word in self.lm.all_words:
            tsword = self.lm.ts(word)
            if not word.unknown() and Levenshtein.distance(tsword, c) < 2:
                a_b_X_d_e = " ".join(self.words[0:2] + [tsword] + self.words[3:5])
                p_a_b_X_d_e, f_a_b_X_d_e = self.pf_from_cache(a_b_X_d_e)

                if f_a_b_X_d_e*local_threshold > best_f:
                    self.something_happened = True
                    best_f = f_a_b_X_d_e
                    best_s = a_b_X_d_e
                    best_w = tsword
                    print("nee")

        

        # 1-1 word context
        if not self.something_happened:
            best_f = self.lm.fr(" ".join(self.words[1:4]))
            print(str(best_f) + "\t" + " ".join(self.words[1:4]))
            for word in self.lm.all_words:
                tsword = self.lm.ts(word)
                if not word.unknown() and Levenshtein.distance(tsword, c) < 2:
                    b_X_d = " ".join(self.words[1:2] + [tsword] + self.words[3:4])               
                    p_b_X_d, f_b_X_d = self.pf_from_cache(b_X_d)
                                   
                    if f_b_X_d/local_threshold > best_f and self.lm.fr(" ".join(self.words[1:2] + [tsword] + self.words[3:5])) >= self.lm.fr(" ".join(self.words[1:5])):
                        self.something_happened = True
                        best_f = f_b_X_d
                        best_s = b_X_d
                        best_w = tsword
            if self.something_happened:
                best_s = self.words[0] + " " + best_s + " " + self.words[4]

        # no context
        if not self.something_happened and not self.lm.oc(self.patterns[2]):
            for word in self.lm.all_words:
                tsword = self.lm.ts(word)
                if not word.unknown() and Levenshtein.distance(tsword, c) < 2:
                    f = self.lm.fr(word);
                    if f > best_f:
                        self.something_happened = True
                        best_f = f
                        best_w = tsword
            if self.something_happened:
                best_s = " ".join(self.words[0:2] + [best_w] + self.words[3:5])
        


        correction = {}
        correction['superclass'] = "replace"
        if c.lower() == best_w.lower():
            correction['class'] = "capitalizationerror"
        elif utils.remove_punct(c) == utils.remove_punct(best_w) or unidecode.unidecode(c) == unidecode.unidecode(best_w):
            correction['class'] = "redundantpunctuation"
        elif not self.lm.oc(self.patterns[2]):
            correction['class'] = "nonworderror"
        else:
            correction['class'] = "replace"
        correction['span'] = [self.fivegram[2][0]]
        correction['text'] = best_w
        return (self.something_happened and best_s != " ".join(self.words), best_s, correction)


# Find split errors
# grep -B 1 -A 6 "spliterror" ../data/validation/page*.json
class Splitter(Corrector):
#        """
#        This function tries to find split errors in the window 'a b cd e' for the words
#        'c' and 'd'. If the frequency of 'c d' is higher than 'cd' (notice the the order
#        of the window is now different), it replaces 'c d' with 'cd'. The space is
#        inserted on all possible places, and the best match is choosen to be candidate
#        for the correction
#        
#        Returns a triple (r1, r2, r3) where
#            r1 = a correction has been found,
#            r2 = the 'new' window, with word 'cd' being replaced for 'c d',
#            r3 = the correction.
#            
#        >>> wss = create_internal_sentence(create_sentence("tot 10 jaar gevangenisstraf , voornamelijk".split(), 'page1.text.div.5.p.2.s.1'))
#        >>> for w in window(wss, 5):
#                print(split_errors_window(w))
#        (False, <colibricore.Pattern object at 0x7f253d1c6e30>, {'class': 'spliterror', 'span': '', 'text': 'jaar gevangenisstraf'})
#        (True, '10 jaar gevangenisstraf, voornamelijk', {'class': 'spliterror', 'span': ['page1.text.div.5.p.2.s.1.w.4', 'page1.text.div.5.p.2.s.1.w.5'], 'text': 'gevangenisstraf,'})
#
#        """
    def __init__(self, lm):
        super().__init__(lm)
    
    def correct(self, fivegram):
        self.update(fivegram)
        return self.correct_()
    
    def correct_(self):
        c_d_e = self.words[2] + " " + self.words[3] + " " + self.words[4]       
        p_c_d_e, f_c_d_e = self.pf_from_cache(c_d_e)        

        cd_e = self.words[2] + self.words[3] + " " + self.words[4]       
        p_cd_e, f_cd_e = self.pf_from_cache(cd_e)

#        print(c_d_e + " & " + cd_e + ": " + str(f_c_d_e) + " & " + str(f_cd_e))

        if not p_cd_e.unknown() and f_cd_e > f_c_d_e: #and not oc(classencoder.buildpattern(ws[1][1]+" "+ws[2][1])):
            new_swindow = self.words[0] + " " + self.words[1] + " " + self.words[2] + self.words[3] + " " + self.words[4]
            proposal = self.words[2] + self.words[3]
            span = [self.fivegram[2][0],self.fivegram[3][0]]
            
            correction = {'class': "spliterror", 'span': span, 'text': proposal, 'confidence': 1}
            return (True, new_swindow, correction)  


        c_d = self.words[2] + " " + self.words[3]    
        p_c_d, f_c_d = self.pf_from_cache(c_d)   
        o_c_d = self.lm.oc(p_c_d)    

        cd = self.words[2] + self.words[3]     
        p_cd, f_cd = self.pf_from_cache(cd)
        o_cd = self.lm.oc(p_cd)
        
        if not p_cd.unknown() and o_cd > o_c_d:
            new_swindow = self.words[0] + " " + self.words[1] + " " + self.words[2] + self.words[3] + " " + self.words[4]
            proposal = self.words[2] + self.words[3]
            span = [self.fivegram[2][0],self.fivegram[3][0]]
            
            correction = {'class': "spliterror", 'span': span, 'text': proposal, 'confidence': 0.5}
            return (True, new_swindow, correction)  
            
    
        correction = {'class': "spliterror", 'span': [], 'text': "", 'confidence': 1}
        return (False, self.word_string, correction)        





# grep -B 1 -A 3 "missingword" ../data/validation/page*.json
class Inserter(Corrector):
    def __init__(self, lm):
#        """
#        This function tries to find a missing word in the window 'a b c d e' after the
#        word 'c'. If the frequency of 'c f d' is higher than 'c d' (notice that the order
#        of the window is now different), it inserts 'f' after 'c'.
#        
#        Returns a triple (r1, r2, r3) where
#            r1 = a correction has been found,
#            r2 = the 'new' window, with word 'f' being inserted after 'c',
#            r3 = the correction.
#        """
        super().__init__(lm)

    def correct(self, fivegram):
        self.update(fivegram)
        return self.correct_()

    def correct_(self):
        # at most 1 insertion
        if self.fivegram[3][0].endswith("M") or self.fivegram[2][0].endswith("M"):
            return (False, "", {})

        #

        best_s = self.lm.bp(self.word_string)
        best_f = self.lm.fr(" ".join(self.words[0:3] + self.words[3:4]))#fr(best_s)
        best_w = ""

        #
        for word in self.lm.all_words:
            if not word.unknown():
                tsword = self.lm.ts(word)
                a_b_c_X_d_e = " ".join(self.words[0:3] + [tsword] + self.words[3:4])
                p_a_b_c_X_d_e, f_a_b_c_X_d_e = self.pf_from_cache(a_b_c_X_d_e)
                    
                if f_a_b_c_X_d_e > best_f:
                    self.something_happened = True
                    best_f = f_a_b_c_X_d_e
                    best_s = a_b_c_X_d_e
                    best_w = tsword
            # backoff option?
        correction = {'class': "missingword", 'after': self.fivegram[2][0], 'text': best_w}
        return (self.something_happened and best_s != joinwords, best_s, correction)





class Attacher(Corrector):
    def __init__(self, lm):
    #        """
    #        This function tries to find runon errors in the window 'a b c d e' for the words
    #        'c' and 'd'. If the frequency of 'cd' is higher than 'c d' (notice the the order
    #        of the window is now different), it replaces 'c d' with 'cd'.
    #        
    #        Returns a triple (r1, r2, r3) where
    #            r1 = a correction has been found,
    #            r2 = the 'new' window, with word 'c d' being replaced for 'cd',
    #            r3 = the correction.
    #        
    #        >>> wss = create_internal_sentence(create_sentence("in de wapenindustrie tewerk waren gesteld".split(), 'page1.text.div.5.p.2.s.1'))
    #        >>> for w in window(wss, 5):
    #                print(runon_errors_window(w))
    #        (False, <colibricore.Pattern object at 0x7f253d1c6790>, {'class': 'runonerror', 'span': ['page1.text.div.5.p.2.s.1.w.3'], 'text': 'wapenindustrie'})
    #        (True, 'de wapenindustrie te werk waren gesteld', {'class': 'runonerror', 'span': ['page1.text.div.5.p.2.s.1.w.4'], 'text': 'te werk'})
    #        """
        super().__init__(lm)
    def correct(self, fivegram):
        self.update(fivegram)
        return self.correct_()
            
    def correct_(self):  
        middle = self.words[2]

        best_s = self.word_string
        best_candidate = middle
        best_f = self.lm.fr(self.patterns[2])

        for x in range(len(middle)+1):
            candidate = copy.copy(middle)
            candidate = '{0} {1}'.format(candidate[:x], candidate[x:])

            p_candidate, f_candidate = self.pf_from_cache(candidate)
            
            if f_candidate > best_f  and not self.lm.bp(candidate[:x]).unknown() and not self.lm.bp(candidate[x:]).unknown():# and s_candidate.strip().split(" "):
                self.something_happened = True
                best_f = f_candidate
                best_s = " ".join(self.words[0:2] + [candidate] + self.words[3:5])
                best_candidate = candidate

        correction = {'class': "runonerror", 'span': [self.fivegram[2][0]], 'text': best_candidate}
        return (self.something_happened, best_s, correction)
        ## Maybe do something with space lacking after interpunction?
        ## See test_runon:s4

class Correctors:
    def __init__(self, lm):
        self.replacer = Replacer(lm)
        self.splitter = Splitter(lm)
        self.inserter = Inserter(lm)
        self.attacher = Attacher(lm)
           
    def correct(self, fivegram):
        if fivegram[2][1] in string.punctuation:
            print("Not correcting punctuation")
            return []

        split = self.splitter.correct(fivegram)
        print("\t\tSPLIT\t" + str(split[0]) + "\t" + split[2]['text'])
        
        runon = self.attacher.correct(fivegram)
        print("\t\tRUNON\t" + str(runon[0]) + "\t" + runon[2]['text'])

        replace = self.replacer.correct(fivegram)
        #print("\t\REPLACE\t" + str(replace[0]) + "\t" + replace[2]['text'])
        print(replace)
        
#        insert = self.inserter.correct(fivegram)
#        print("\t\tINSERT\t" + str(insert[0]) + "\t" + insert[2]['text'])










#

#

#

#
#
#    p_cache = {}
#
#

