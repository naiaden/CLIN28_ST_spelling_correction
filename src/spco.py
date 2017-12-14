import colibricore
import Levenshtein
import copy
import json
import string
import unidecode
import pprint

import argparse

import random

argparser = argparse.ArgumentParser(description="Spelling correction based on 5-grams.", epilog="Developed for the CLIN28 shared task on spelling correction for contemporary Dutch. Reach me at louis@naiaden.nl for questions or visit https://github.com/naiaden/COCOCLINSPCO/")
argparser.add_argument('classfile', help="encoded classes")
argparser.add_argument('datafile', help="encoded data")
argparser.add_argument('modelfile', help="(un)indexed pattern model")
argparser.add_argument('outputdir', help="output directory")
#args, unknownargs = argparser.parse_known_args()

classfile = '/home/louis/Data/corpus/small.colibri.cls'#args.classfile
datafile = '/home/louis/Data/corpus/small.colibri.dat'#args.datafile
modelfile = '/home/louis/Data/corpus/small.colibri.model'#args.modelfile
outputdir = '/home/louis/Programming/COCOCLINSPCO/data/output/'#args.outputdir

######################
## Global functions on colibricore.Pattern

def ts(pattern):
    return pattern.tostring(classdecoder)

def oc(pattern):
    return model.occurrencecount(pattern)

def fr(pattern):
    return model.frequency(pattern)

######################
## Global functions on other stuff

def id(folia_id):
    return folia_id.split(".w.")[0]

def window(iterable, size=2):
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

######################
## Run the game

# add stuff to encoder? Nah!

import json
# page1144 = json.load(open('/home/louis/Programming/COCOCLINSPCO/data/test/pagesmall.json'))
page1144 = json.load(open('/home/louis/Programming/COCOCLINSPCO/data/validation/page1.json'))
page1144_corrections = page1144['corrections']
page1144_words = page1144['words']

sos_filler = ['id-not-available', '<s>', classencoder.buildpattern(" "), True, 'in-not-available']
eos_filler = ['id-not-available', '</s>', classencoder.buildpattern(" "), True, 'in-not-available']


######################
## Correction units

def is_year(number):
    try:
        number = int(number)
        return number > 1750 and number < 2100
    except (ValueError, TypeError):
            return False;

def number_to_text(number):
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


# archaic, non-word and confusables:
# Compare frequency of (a b c d e) with (a b X d e)
def replaceables_window(ws):
    words = [w[1] for w in ws]

    something_happened = False

    c = ws[2][1]

    best_s = classencoder.buildpattern(" ".join(words))
    best_f = fr(best_s)
    best_w = c

    if is_year(c):
        return (False, best_s, {})

    # 2-2 word context
    for word,count in model.filter(1, size=1):
        if not word.unknown() and Levenshtein.distance(ts(word), c) < 2:
            a_b_X_d_e = " ".join(words[0:2]) + " " + ts(word) + " " + " ".join(words[3:5])
            #print(a_b_X_d_e)
            p_a_b_X_d_e = classencoder.buildpattern(a_b_X_d_e)
            if fr(p_a_b_X_d_e) > best_f:
                something_happened = True
                best_f = fr(p_a_b_X_d_e)
                best_s = a_b_X_d_e
                best_w = ts(word)

    # 1-1 word context
    if not something_happened:
        for word,count in model.filter(1, size=1):
            if not word.unknown() and Levenshtein.distance(ts(word), c) < 2:
                a_b_X_d_e = " ".join(words[1:2]) + " " + ts(word) + " " + " ".join(words[3:4])
                p_a_b_X_d_e = classencoder.buildpattern(a_b_X_d_e)
                if fr(p_a_b_X_d_e) > best_f:
                    something_happened = True
                    best_f = fr(p_a_b_X_d_e)
                    best_s = a_b_X_d_e
                    best_w = ts(word)
        if something_happened:
            best_s = ws[0][1] + " " + best_s + " " + ws[4][1]

    # no context
    if not something_happened and not model.occurrencecount(ws[2][2]):
        for word,count in model.filter(1, size=1):
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

# Compare frequency of (a b cd e f) with (a b c d e f)
def runon_errors_window(ws):
    words = [w[1] for w in ws]

    something_happened = False

    middle = words[2]#"".join(words[2:4])

    best_s = classencoder.buildpattern(" ".join(words))
    best_candidate = middle
    best_f = fr(ws[2][2])

    for x in range(len(middle)+1):
        candidate = copy.copy(middle)
        candidate = '{0} {1}'.format(candidate[:x], candidate[x:])

        p_candidate = classencoder.buildpattern(candidate)
        # print(candidate + "\t" + str(fr(p_candidate)))
        f_candidate = fr(p_candidate)
        if f_candidate > best_f:# and s_candidate.strip().split(" "):
            something_happened = True
            best_f = f_candidate
            best_s = ws[0][1] + " " + ws[1][1] + " " + candidate + " " + ws[3][1] + " " + ws[4][1]
            best_candidate = candidate

    correction = {}
    correction['class'] = "runonerror"
    correction['span'] = [ws[2][0]]
    correction['text'] = best_candidate
    return (something_happened, best_s, correction)

# Compare frequency of (a b c d e) with (a b cd e)
def split_errors_window(ws):
    words = [w[1] for w in ws]

    something_happened = False

    best_s = classencoder.buildpattern(" ".join(words))
    best_candidate = ws[2][1] + " " + ws[3][1]
    best_f = fr(classencoder.buildpattern(best_candidate))
    best_span = ""
    # print(best_candidate + "\t" + str(best_f))

    a_b_cd_e = ws[2][1]+ws[3][1]
    p_a_b_cd_e = classencoder.buildpattern(a_b_cd_e)
    f_a_b_cd_e = fr(p_a_b_cd_e)
    # print(a_b_cd_e + "\t" + str(f_a_b_cd_e) + "\t" + str(oc(classencoder.buildpattern(ws[1][1]+" "+ws[2][1]))))

    if f_a_b_cd_e > best_f:# and not oc(classencoder.buildpattern(ws[1][1]+" "+ws[2][1])):
        something_happened = True
        best_f = f_a_b_cd_e
        best_s = ws[0][1] + " " + ws[1][1] + " " + ws[2][1]+ws[3][1] + " " + ws[4][1]
        best_candidate = ws[2][1] + ws[3][1]
        best_span = [ws[2][0],ws[3][0]]

    correction = {}
    correction['class'] = "spliterror"
    correction['span'] = best_span
    correction['text'] = best_candidate
    return (something_happened, best_s, correction)

def missing_words_window(ws):
    words = [w[1] for w in ws]

    # at most 1 insertion
    if ws[3][0].endswith("M") or ws[2][0].endswith("M"):
        return (False, "", {})

    something_happened = False
    #
    best_s = classencoder.buildpattern(" ".join(words))
    best_f = fr(best_s)
    best_w = ""
    #
    for word,count in model.filter(1, size=1):
        if not word.unknown():
            a_b_c_X_d_e = " ".join(words[0:3]) + " " + ts(word) + " " + " ".join(words[3:4])
            p_a_b_c_X_d_e = classencoder.buildpattern(a_b_c_X_d_e)
            f_a_b_c_X_d_e = fr(p_a_b_c_X_d_e)
            if f_a_b_c_X_d_e > best_f:
                something_happened = True
                best_f = f_a_b_c_X_d_e
                best_s = a_b_c_X_d_e
                best_w = ts(word)
        # backoff option?
    correction = {}
    correction['class'] = "missingword"
    correction['after'] = ws[2][0]
    correction['text'] = best_w
    return (something_happened and best_s != " ".join(words), best_s, correction)





def action_in_sentence(sentence, correction):
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
    return (rv, sentence)

correction_cache = {}

def process(something):


    string_sentence = " ".join([x[1] for x in something])
    wip_sentence = copy.copy(something)



    corrections = []

    change = True

    print("\nSENTENCE: " + string_sentence)
    while change:
        change = False
        temp_sent = copy.copy(wip_sentence)
        for w in window(temp_sent, 5):

            # id_list = " ".join([x[0] for x in w]) + " ".join([x[1] for x in w])
            # if id_list in correction_cache:
            #     print(">>> From cache: no change")
            #     break


            local_corrections = []
            local_change = False



            string_window = " ".join([x[1] for x in w])
            print("\t===" + string_window)

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
                local_corrections.append(split[2])
                wip_sentence = action_in_sentence(wip_sentence, split[2])
                print([(x[0],x[1]) for x in wip_sentence])

            missing = missing_words_window(w)
            local_change |= missing[0]
            if missing[0]:
                local_corrections.append(missing[2])
                wip_sentence = action_in_sentence(wip_sentence, missing[2])
                print([(x[0],x[1]) for x in wip_sentence])

            change |= local_change
            corrections += local_corrections
            # correction_cache[id_list] = local_change
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
