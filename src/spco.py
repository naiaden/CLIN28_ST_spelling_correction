import colibricore
import Levenshtein
import copy
import json
import string
import unidecode
import pprint

import argparse

import random

import sys

argparser = argparse.ArgumentParser(description="Spelling correction based on 5-grams.", epilog="Developed for the CLIN28 shared task on spelling correction for contemporary Dutch. Reach me at louis@naiaden.nl for questions or visit https://github.com/naiaden/COCOCLINSPCO/")
argparser.add_argument('classfile', help="encoded classes")
argparser.add_argument('datafile', help="encoded data")
argparser.add_argument('modelfile', help="(un)indexed pattern model")
argparser.add_argument('outputdir', help="output directory")
args, unknown_args = argparser.parse_known_args()

if not unknown_args:
    print("Missing input files. \n A B O R T")
    sys.exit()

classfile = args.classfile
#classfile = '/home/louis/Data/corpus/small.colibri.cls'
datafile = args.datafile
#datafile = '/home/louis/Data/corpus/small.colibri.dat'
modelfile = args.modelfile
#modelfile = '/home/louis/Data/corpus/small.colibri.model'
outputdir = args.outputdir
#outputdir = '/home/louis/Programming/COCOCLINSPCO/data/output/'

######################
## Global functions on colibricore.Pattern

def ts(pattern):
    """" 
    Returns the string representation of the colibricore.Pattern argument.
    
    >>> ts(bp("patroon"))
    'patroon'
    """
    return pattern.tostring(classdecoder)

def oc(pattern):
    """ 
    Returns the occurrence count of the colibricore.Pattern argument in the training data.
    
    >>> oc(bp("patroon"))
    170
    """
    return model.occurrencecount(pattern)

def fr(pattern):
    """ 
    Returns the frequency of the colibricore.Pattern argument in the training data.
    The frequency is the normalized occurrence count for the length (order) of the argument.
    
    >>> fr(bp("patroon"))
    1.4490891920364536e-05
     """
    return model.frequency(pattern)

def bp(string):
    """
    Returns the colibripattern.Pattern representation of string.
    
    >>> bp("patroon")
    <colibricore.Pattern at 0x7f253cf1eab0>
    """
    return classencoder.buildpattern(string)

######################
## Global functions on other stuff

def fid(folia_id):
    """ 
    Returns the folia document id and its specifiers up to sentence level of a folia id string representation. 
    
    >>> fid("page1.text.div.2.p.3.s.4.w.1")
    page1.text.div.2.p.3.s.4
    
    >>> fid("page1.text.div.2.p.3.s.4")
    page1.text.div.2.p.3.s.4
    """
    return folia_id.split(".w.")[0]

def window(iterable, size=2):
    """ 
    Generator for a sliding window over iterable with given size.
    Assumes that len(iterable) > size 
    
    >>> for w in window([1,2,3,4,5,6], 5):
            print(w)
    [1, 2, 3, 4, 5]
    [2, 3, 4, 5, 6]

    >>> for w in window([1,2,3], 5):
            print(w)
    DeprecationWarning: generator 'window' raised StopIteration
    """
    i = iter(iterable)
    win = []
    for e in range(0, size):
        win.append(next(i))
    yield win
    for e in i:
        win = win[1:] + [e]
        yield win

punct_translator = str.maketrans('', '', string.punctuation)

######################
## Test

def create_sentence(string, in_id="page1.text.div.1.p.1.s.1"):
    """
    Returns a test sentence as used by the task. An optional "in" completes the sentence.
    
    >>> create_sentence(['Dit', 'is', 'maar', 'een', 'paar', 'woorden', '.'], "page1.text.div.2.p.3.s.4")
    [{'id': 'page1.text.div.2.p.3.s.4.w.1', 'in': 'page1.text.div.2.p.3.s.4', 'space': True, 'text': 'Dit'},
     {'id': 'page1.text.div.2.p.3.s.4.w.2', 'in': 'page1.text.div.2.p.3.s.4', 'space': True, 'text': 'is'},
     {'id': 'page1.text.div.2.p.3.s.4.w.3', 'in': 'page1.text.div.2.p.3.s.4', 'space': True, 'text': 'maar'},
     {'id': 'page1.text.div.2.p.3.s.4.w.4', 'in': 'page1.text.div.2.p.3.s.4', 'space': True, 'text': 'een'},
     {'id': 'page1.text.div.2.p.3.s.4.w.5', 'in': 'page1.text.div.2.p.3.s.4', 'space': True, 'text': 'paar'},
     {'id': 'page1.text.div.2.p.3.s.4.w.6', 'in': 'page1.text.div.2.p.3.s.4', 'space': True, 'text': 'woorden'},
     {'id': 'page1.text.div.2.p.3.s.4.w.7', 'in': 'page1.text.div.2.p.3.s.4', 'space': True, 'text': '.'}]
    """
    sentence = []
    for i, w in enumerate(string):
        sentence.append({'id': in_id + '.w.' + str(i+1), 'text': w, 'space': True, 'in': in_id})
    return sentence

def create_internal_sentence(sentence):
    """
    Returns a test sentence in the interal structure based on a sentence, 
    with a colibricore.Pattern representation of the token.
    
    >>> create_internal_sentence(create_sentence(['Dit', 'is', 'maar', 'een', 'paar', 'woorden', '.'], "page1.text.div.2.p.3.s.4"))
    [['page1.text.div.5.p.2.s.1.w.1', 'Speer', <colibricore.Pattern at 0x7f253cf1e470>, True, 'page1.text.div.5.p.2.s.1'], 
     ['page1.text.div.5.p.2.s.1.w.2', 'bij', <colibricore.Pattern at 0x7f253cf1e8d0>, True, 'page1.text.div.5.p.2.s.1'], 
     ['page1.text.div.5.p.2.s.1.w.3', 'de', <colibricore.Pattern at 0x7f253cf1e050>, True, 'page1.text.div.5.p.2.s.1'], 
     ['page1.text.div.5.p.2.s.1.w.4', 'processen', <colibricore.Pattern at 0x7f253cf1e7b0>, True, 'page1.text.div.5.p.2.s.1'],
     ['page1.text.div.5.p.2.s.1.w.5', 'van', <colibricore.Pattern at 0x7f253cf1e8f0>, True, 'page1.text.div.5.p.2.s.1'], 
     ['page1.text.div.5.p.2.s.1.w.6', 'Neurenberg', <colibricore.Pattern at 0x7f253cf1e450>, True, 'page1.text.div.5.p.2.s.1'],
     ['page1.text.div.5.p.2.s.1.w.7', 'veroordeeld', <colibricore.Pattern at 0x7f253cf1e9d0>, True, 'page1.text.div.5.p.2.s.1']]
    """
    internal_sentence = []
    for w in sentence:
        internal_sentence.append([w['id'],
                                  w['text'],
                                  bp(w['text']),
                                  w['space'],
                                  w['in']])
    return internal_sentence
        



######################
## Set the stage

import pathlib

classencoder = colibricore.ClassEncoder(classfile)
classdecoder = colibricore.ClassDecoder(classfile)
options = colibricore.PatternModelOptions(minlength=1, maxlength=5, mintokens=1)

if pathlib.Path(modelfile).is_file():
    model = colibricore.UnindexedPatternModel(modelfile, options)
else:
    model = colibricore.UnindexedPatternModel()
    model.train(datafile, options)
    model.write(modelfile)

# This turns out to be faster than set or frozenset
# However, it is mutable, so do not change
all_words = []
for w,c in model.filter(1, size=1):
    all_words.append(w)

######################
## Run the game

import json
# page1144 = json.load(open('/home/louis/Programming/COCOCLINSPCO/data/test/pagesmall.json'))
#page1144 = json.load(open('/home/louis/Programming/COCOCLINSPCO/data/validation/page1.json'))
page1144 = json.load(open(unknown_args[0]))
page1144_corrections = page1144['corrections']
page1144_words = page1144['words']

sos_filler = ['id-not-available', '<s>', classencoder.buildpattern(" "), True, 'in-not-available']
eos_filler = ['id-not-available', '</s>', classencoder.buildpattern(" "), True, 'in-not-available']


######################
## Correction units

def is_year(number):
    """ A simple function to test if the input (string or number) is a year (between 1750 and 2100). """
    try:
        number = int(number)
        return number > 1750 and number < 2100
    except (ValueError, TypeError):
            return False;

def number_to_text(number):
    """ 
    No longer necessary for the shared task; this function converts an integer
    to its lexical string representation if this is according to the rules of OnzeTaal
    (https://onzetaal.nl/taaladvies/getallen-in-letters-of-cijfers/). """
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


def replaceables_window(ws):
    """
    This function tries to find a replaceable in the window 'a b c d e' for word 'c'.
    It creates a correction with the superclass 'replace', and more specific classes
    such as 'capitalizationerror', 'redundantpunctuation', 'nonworderror' and the wildcard
    'replace'. It implicitely also finds archaic and confuseables, but there are shared
    under the class 'replace'.
    
    It follows a backoff strategy, where it starts with window size 5, 2 on the left, 2 on 
    the right. If there is not a word 'c'' with a higher frequency, then it backs off to 
    a 3 word window. Analoguously it finally also tries if a word without context might be
    a better fit if the word 'c' seems to be out-of-vocabulary.
    
    Returns a triple (r1, r2, r3) where
        r1 = a correction has been found,
        r2 = the 'new' window, with word 'c' being replaced,
        r3 = the correction.
        
    >>> wss = create_internal_sentence(create_sentence("Speer bij de processen van Neurenberg".split(), 'page1.text.div.5.p.2.s.1'))
    >>> for w in window(wss, 5):
            print(replaceables_window(w))
    (False, 'Speer bij de processen van', {'superclass': 'replace', 'class': 'capitalizationerror', 'span': ['page1.text.div.5.p.2.s.1.w.3'], 'text': 'de'})
    (True, 'bij de Processen van Neurenberg', {'superclass': 'replace', 'class': 'capitalizationerror', 'span': ['page1.text.div.5.p.2.s.1.w.4'], 'text': 'Processen'})
    """
    words = [w[1] for w in ws]

    something_happened = False

    c = ws[2][1]

    best_s = classencoder.buildpattern(" ".join(words))
    best_f = fr(best_s)
    best_w = c

    if is_year(c):
        return (False, best_s, {})

    # 2-2 word context
    for word in all_words:
        if not word.unknown() and Levenshtein.distance(ts(word), c) < 2:
            a_b_X_d_e = " ".join(words[0:2] + [ts(word)] + words[3:5])
            p_a_b_X_d_e, f_a_b_X_d_e = pf_from_cache(a_b_X_d_e)

            if f_a_b_X_d_e > best_f:
                something_happened = True
                best_f = f_a_b_X_d_e
                best_s = a_b_X_d_e
                best_w = ts(word)

    # 1-1 word context
    if not something_happened:
        for word in all_words:
            if not word.unknown() and Levenshtein.distance(ts(word), c) < 2:
                a_b_X_d_e = " ".join(words[1:2] + [ts(word)] + words[3:4])               
                p_a_b_X_d_e, f_a_b_X_d_e = pf_from_cache(a_b_X_d_e)
                
                if f_a_b_X_d_e > best_f:
                    something_happened = True
                    best_f = f_a_b_X_d_e
                    best_s = a_b_X_d_e
                    best_w = ts(word)
        if something_happened:
            best_s = ws[0][1] + " " + best_s + " " + ws[4][1]

    # no context
    if not something_happened and not model.occurrencecount(ws[2][2]):
        for word in all_words:
            if not word.unknown() and Levenshtein.distance(ts(word), c) < 2:
                f = fr(word);
                if f > best_f:
                    something_happened = True
                    best_f = f
                    best_w = ts(word)
        if something_happened:
            best_s = ws[0][1] + " " + ws[1][1] + " " + best_w + " " + ws[3][1] + " " + ws[4][1]

    correction = {}
    correction['superclass'] = "replace"
    if c.lower() == best_w.lower():
        correction['class'] = "capitalizationerror"
    elif c.translate(punct_translator) == best_w.translate(punct_translator) or unidecode.unidecode(c) == unidecode.unidecode(best_w):
        correction['class'] = "redundantpunctuation"
    elif not model.occurrencecount(ws[2][2]):
        correction['class'] = "nonworderror"
    else:
        correction['class'] = "replace"
    correction['span'] = [ws[2][0]]
    correction['text'] = best_w
    return (something_happened and best_s != " ".join(words), best_s, correction)

def pf_from_cache(candidate):
    """
    If candidate is already in the pattern-frequency cache, then retrieve its
    colibricore.Pattern representation and its frequency. Otherwise compute the
    values and put it in the cache first.
    
    >>> pf_from_cache("patroon")
    (<colibricore.Pattern at 0x7f253d1c68d0>, 1.4490891920364536e-05)
    """
    if False and candidate in p_cache:
        (p_candidate, f_candidate) = p_cache[candidate]
    else:
        p_candidate = classencoder.buildpattern(candidate)
        f_candidate = fr(p_candidate)
        #p_cache[candidate] = (p_candidate, f_candidate)
    return (p_candidate, f_candidate)

def runon_errors_window(ws):
    """
    This function tries to find runon errors in the window 'a b c d e' for the words
    'c' and 'd'. If the frequency of 'cd' is higher than 'c d' (notice the the order
    of the window is now different), it replaces 'c d' with 'cd'.
    
    Returns a triple (r1, r2, r3) where
        r1 = a correction has been found,
        r2 = the 'new' window, with word 'c d' being replaced for 'cd',
        r3 = the correction.
    
    >>> wss = create_internal_sentence(create_sentence("in de wapenindustrie tewerk waren gesteld".split(), 'page1.text.div.5.p.2.s.1'))
    >>> for w in window(wss, 5):
            print(runon_errors_window(w))
    (False, <colibricore.Pattern object at 0x7f253d1c6790>, {'class': 'runonerror', 'span': ['page1.text.div.5.p.2.s.1.w.3'], 'text': 'wapenindustrie'})
    (True, 'de wapenindustrie te werk waren gesteld', {'class': 'runonerror', 'span': ['page1.text.div.5.p.2.s.1.w.4'], 'text': 'te werk'})
    """
    words = [w[1] for w in ws]

    something_happened = False

    middle = words[2]#"".join(words[2:4])

    best_s = classencoder.buildpattern(" ".join(words))
    best_candidate = middle
    best_f = fr(ws[2][2])

    for x in range(len(middle)+1):
        candidate = copy.copy(middle)
        candidate = '{0} {1}'.format(candidate[:x], candidate[x:])

        p_candidate, f_candidate = pf_from_cache(candidate)
        
        if f_candidate > best_f  and not bp(candidate[:x]).unknown() and not bp(candidate[x:]).unknown():# and s_candidate.strip().split(" "):
            something_happened = True
            best_f = f_candidate
            best_s = " ".join(ws[0][1] + ws[1][1] + candidate + ws[3][1] + ws[4][1])
            best_candidate = candidate

    correction = {'class': "runonerror", 'span': [ws[2][0]], 'text': best_candidate}
    return (something_happened, best_s, correction)

def split_errors_window(ws):
    """
    This function tries to find split errors in the window 'a b cd e' for the words
    'c' and 'd'. If the frequency of 'c d' is higher than 'cd' (notice the the order
    of the window is now different), it replaces 'c d' with 'cd'. The space is
    inserted on all possible places, and the best match is choosen to be candidate
    for the correction
    
    Returns a triple (r1, r2, r3) where
        r1 = a correction has been found,
        r2 = the 'new' window, with word 'cd' being replaced for 'c d',
        r3 = the correction.
        
    >>> wss = create_internal_sentence(create_sentence("tot 10 jaar gevangenisstraf , voornamelijk".split(), 'page1.text.div.5.p.2.s.1'))
    >>> for w in window(wss, 5):
            print(split_errors_window(w))
    (False, <colibricore.Pattern object at 0x7f253d1c6e30>, {'class': 'spliterror', 'span': '', 'text': 'jaar gevangenisstraf'})
    (True, '10 jaar gevangenisstraf, voornamelijk', {'class': 'spliterror', 'span': ['page1.text.div.5.p.2.s.1.w.4', 'page1.text.div.5.p.2.s.1.w.5'], 'text': 'gevangenisstraf,'})

    """
    words = [w[1] for w in ws]

    something_happened = False

    best_s = classencoder.buildpattern(" ".join(words))
    best_candidate = ws[2][1] + " " + ws[3][1]
    best_f = fr(classencoder.buildpattern(best_candidate))
    best_span = ""

    a_b_cd_e = ws[2][1]+ws[3][1]
   
    p_a_b_cd_e, f_a_b_cd_e = pf_from_cache(a_b_cd_e)

    if not p_a_b_cd_e.unknown() and f_a_b_cd_e > best_f:# and not oc(classencoder.buildpattern(ws[1][1]+" "+ws[2][1])):
        something_happened = True
        best_f = f_a_b_cd_e
        best_s = ws[0][1] + " " + ws[1][1] + " " + ws[2][1]+ws[3][1] + " " + ws[4][1]
        best_candidate = ws[2][1] + ws[3][1]
        best_span = [ws[2][0],ws[3][0]]

    correction = {'class': "spliterror", 'span': best_span, 'text': best_candidate}
    return (something_happened, best_s, correction)


p_cache = {}


def missing_words_window(ws):
    """
    This function tries to find a missing word in the window 'a b c d e' after the
    word 'c'. If the frequency of 'c f d' is higher than 'c d' (notice that the order
    of the window is now different), it inserts 'f' after 'c'.
    
    Returns a triple (r1, r2, r3) where
        r1 = a correction has been found,
        r2 = the 'new' window, with word 'f' being inserted after 'c',
        r3 = the correction.
    """
    words = [w[1] for w in ws]

    # at most 1 insertion
    if ws[3][0].endswith("M") or ws[2][0].endswith("M"):
        return (False, "", {})

    something_happened = False
    #
    joinwords = " ".join(words)
    best_s = classencoder.buildpattern(joinwords)
    best_f = fr(best_s)
    best_w = ""

    #
    for word in all_words:
        if not word.unknown():
            tsword = ts(word)
            a_b_c_X_d_e = " ".join(words[0:3] +[tsword] + words[3:4])
            p_a_b_c_X_d_e, f_a_b_c_X_d_e = pf_from_cache(a_b_c_X_d_e)
                
            if f_a_b_c_X_d_e > best_f:
                something_happened = True
                best_f = f_a_b_c_X_d_e
                best_s = a_b_c_X_d_e
                best_w = tsword
        # backoff option?
    correction = {'class': "missingword", 'after': ws[2][0], 'text': best_w}
    return (something_happened and best_s != joinwords, best_s, correction)





def action_in_sentence(sentence, correction):
    """
    This function tries to apply a correction on the sentence.
    
    Returns the corrected sentence.
    """
    print("AIS\t" + str(correction))
    if correction['class'] == "runonerror":
        for iter,id in enumerate(sentence):
            if id[0] == correction['span'][0]:
                id[1] = correction['text'].split(" ")[0]
                #print(id[1] + " " + str(iter))
                id[2] = classencoder.buildpattern(correction['text'].split(" ")[0], allowunknown=False, autoaddunknown=True)
                break
        new_entry = [id[0] + "R",
                     correction['text'].split(" ")[1],
                     classencoder.buildpattern(correction['text'].split(" ")[1], allowunknown=False, autoaddunknown=True),
                     item['space'],
                     item['in']]
        sentence.insert(iter+1, new_entry)
    if correction.get('superclass', "") == "replace":
        for iter,id in enumerate(sentence):
            if id[0] == correction['span'][0]:
                id[1] = correction['text']
                id[2] = classencoder.buildpattern(correction['text'], allowunknown=False, autoaddunknown=True)
                break
    if correction['class'] == "spliterror":
        for iter,id in enumerate(sentence):
            if id[0] == correction['span'][0]:
                id[1] = correction['text']
                id[2] = classencoder.buildpattern(correction['text'], allowunknown=False, autoaddunknown=True)
            if id[0] == correction['span'][1]:
                break
        del sentence[iter]
    if correction['class'] == "missingword":
        for iter, id in enumerate(sentence):
            if id[0] == correction['after']:
                #print("MW:\t" + str(iter) + "\t" + str(id))
                break
        new_entry = [id[0] + "." + str(random.randint(1,100)) + "M",
                     correction['text'],
                     classencoder.buildpattern(correction['text'], allowunknown=False, autoaddunknown=True),
                     item['space'],
                     item['in']]
        sentence.insert(iter+1, new_entry)

    return sentence

def apply_on_corrections(correction, corrections, sentence):
    """
    This function checks whether a correction is due to be applied on
    another correction, in which case it will try to gracefully handle
    the situation by updating the previous correction (with the word,
    not a new correction class).
    
    Returns a tuple (r1, r2) where
        r1 = the correction has been applied on another correction,
        r2 = the updated sentence.
        
        
    >>> correction = {'class': 'spliterror', 'span': ['page1.text.div.4.p.1.s.2.w.18', 'page1.text.div.4.p.1.s.2.w.18.47M'], 'text': 'zonet'}    
    >>> corrections = [{'class': 'missingword', 'after': 'page1.text.div.4.p.1.s.2.w.18', 'text': 'net'}]
    >>> sentence = [['page1.text.div.4.p.1.s.2.w.16', 'en', bp('en'), True, 'page1.text.div.4.p.1.s.2'], 
                    ['page1.text.div.4.p.1.s.2.w.17', 'wist', bp('wist'), True, 'page1.text.div.4.p.1.s.2'], 
                    ['page1.text.div.4.p.1.s.2.w.18', 'zo', bp('zo'), True, 'page1.text.div.4.p.1.s.2'], 
                    ['page1.text.div.4.p.1.s.2.w.18.47M', 'net', bp('net'), True, 'page1.text.div.4.p.1.s.2'], 
                    ['page1.text.div.4.p.1.s.2.w.19', 'de', bp('de'), True, 'page1.text.div.4.p.1.s.2']]
    >>> apply_on_corrections(c1, C1, s1)
    (True, [['page1.text.div.4.p.1.s.2.w.16', 'en', <colibricore.Pattern at 0x7f253cf80b70>, True, 'page1.text.div.4.p.1.s.2'],
            ['page1.text.div.4.p.1.s.2.w.17', 'wist', <colibricore.Pattern at 0x7f253cf809d0>, True, 'page1.text.div.4.p.1.s.2'],
            ['page1.text.div.4.p.1.s.2.w.18', 'zonet', <colibricore.Pattern at 0x7f253cf80950>, True, 'page1.text.div.4.p.1.s.2'], 
            ['page1.text.div.4.p.1.s.2.w.19', 'de', <colibricore.Pattern at 0x7f253cf80270>, True, 'page1.text.div.4.p.1.s.2']])
    """  
    rv = False
    if correction.get('superclass', "") == 'replace':
        if correction['span'][0].endswith("M"):
            print("correction: " + str(correction))
            f_id = correction['span'][0]

            for c in corrections:
                print("          : " + str(c))
                if 'span' in c and c['span'][0] == f_id:
                    c['text'] = correction['text']
                    print("          :>" + str(c))
                    rv = True

                    for id in sentence:
                        if id[0] == f_id:
                            id[1] = correction['text']
                            id[2] = classencoder.buildpattern(correction['text'], allowunknown=False, autoaddunknown=True)
                            break

                    break
                if 'after' in c and c['after'] == ".".join(f_id.split(".")[0:-1]):
                    c['text'] = correction['text']
                    print("          :>" + str(c))
                    rv = True

                    for id in sentence:
                        if id[0] == f_id:
                            id[1] = correction['text']
                            id[2] = classencoder.buildpattern(correction['text'], allowunknown=False, autoaddunknown=True)
                            break

                    break
    if correction['class'] == 'spliterror':
        if fid(correction['span'][0]) == fid(correction['span'][1]) and correction['span'][1].endswith("M"):
            
            for iter, wid in enumerate(sentence):
                print(wid)
                if wid[0] == correction['span'][0]:
#                    print("--" + str(wid))                    
                    wid[1] = correction['text']
                    wid[2] = classencoder.buildpattern(correction['text'], allowunknown=False, autoaddunknown=True)
                    
                    rv = True
                if  wid[0] == correction['span'][1]:
#                    print(">>" + str(wid) + "\t\t(" + str(iter) + ")")
                    break
            if sentence[iter][0].endswith("M"):
                del sentence[iter]
    return (rv, sentence)

correction_cache = {}
correction_cache_words = {}

only_sentence = ''
#only_sentence = 'page1.text.div.5.p.2.s.1'

def process(something):


    string_sentence = " ".join([x[1] for x in something])
    wip_sentence = copy.copy(something)

    

    corrections = []
    if only_sentence and something[3][4] != only_sentence:
#        print("ignoring " + str(something[3][4]))
        return corrections

    change = True

    print("\nSENTENCE: " + string_sentence)
    while change:
        change = False
        temp_sent = copy.copy(wip_sentence)
        for w in window(temp_sent, 5):
#            print(wip_sentence)

            id_word_list = " ".join([x[0] for x in w]) + " ".join([x[1] for x in w])
            word_list = " ".join([x[1] for x in w])
            id_list = " ".join([x[0] for x in w])
            
            
            string_window = " ".join([x[1] for x in w])
            
            if correction_cache.get(id_word_list, False):
                print(">>> from cache: no change for [" + string_window + "]")
                continue

            if w[2][1] in correction_cache_words.get(id_list, []):
                print(">>> from cache: weer/meer for [" + string_window + "]: " + str(correction_cache_words.get(id_list, [])))
                continue
            
            if " ".join([x[0] for x in w]) not in correction_cache_words:
                correction_cache_words[id_list] = []
            
            correction_cache_words[id_list].append(w[2][1])


            local_corrections = []
            local_change = False



#            string_window = " ".join([x[1] for x in w])
            print("--- " + string_window)

            # test if correction on correction

            runon = runon_errors_window(w)
            local_change |= runon[0]
            if runon[0]:
                local_corrections.append(runon[2])
                wip_sentence = action_in_sentence(wip_sentence, runon[2])
                print([(x[0],x[1]) for x in wip_sentence])

            replaceable = replaceables_window(w)
            local_change |= replaceable[0]
            if replaceable[0]:
                # print(replaceable[2])
                (rv, wip_sentence) = apply_on_corrections(replaceable[2], corrections, wip_sentence)
                if not rv:
                    local_corrections.append(replaceable[2])
                    #print(wip_sentence)
                    wip_sentence = action_in_sentence(wip_sentence, replaceable[2])
                    print("Process\t:" + str([(x[0],x[1]) for x in wip_sentence]))
                    #print(wip_sentence)

            split = split_errors_window(w)
            local_change |= split[0]
            if split[0]:
                (rv, wip_sentence) = apply_on_corrections(split[2], corrections, wip_sentence)
                if not rv:
                    local_corrections.append(split[2])
                    wip_sentence = action_in_sentence(wip_sentence, split[2])
                    print([(x[0],x[1]) for x in wip_sentence])

            missing = missing_words_window(w)
            local_change |= missing[0]
            if missing[0]:
                (rv, wip_sentence) = apply_on_corrections(missing[2], corrections, wip_sentence)
                if not rv:
                    local_corrections.append(missing[2])
                    wip_sentence = action_in_sentence(wip_sentence, missing[2])
                    print([(x[0],x[1]) for x in wip_sentence])

            change |= local_change
            corrections += local_corrections
            
#            if not local_change:
#                print("NO LOCAL CHANGE! for " + id_word_list)
            
            correction_cache[id_word_list] = not local_change
            
        print("\nRESULT: " + " ".join([x[1] for x in wip_sentence]))

    return corrections

sent_iter = 1

sentence = []
sentence.append(sos_filler)
sentence.append(sos_filler)
page_corrections = []
current_in = page1144_words[0]['in']
for item in page1144_words:
    if current_in != item['in']:
        current_in = item['in']

        sentence.append(eos_filler)
        sentence.append(eos_filler)
        page_corrections += process(sentence)
        # if sent_iter > 1:
        #     break
        sent_iter += 1
        sentence = []
        sentence.append(sos_filler)
        sentence.append(sos_filler)
        # page1144_words.insert(0, sos_filler)
        # page1144_words.insert(0, sos_filler)
    sentence.append([item['id'],
                     item['text'],
                     classencoder.buildpattern(item['text'], allowunknown=False, autoaddunknown=True),
                     item['space'],
                     item['in']])
page_corrections += process(sentence)

pp = pprint.PrettyPrinter(indent=4)
pp.pprint({'corrections': page_corrections, 'words': page1144_words})

with open('/home/louis/Programming/COCOCLINSPCO/data/output/test4.json', 'w') as f:
    json.dump({'corrections': page_corrections, 'words': page1144_words}, f)
