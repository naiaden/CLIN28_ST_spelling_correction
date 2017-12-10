import colibricore
import Levenshtein
import copy
import json

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

######################
## Correction units

def number_to_text(number):
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

# archaic, non-word and confusables:
# Compare frequency of (a b c d e) with (a b X d e)
def replaceables_window(ws):
    words = [w[1] for w in ws]

    something_happened = False

    c = ws[2][1]

    best_s = classencoder.buildpattern(" ".join(words))
    best_f = fr(best_s)
    best_w = c

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

######################
## Set the stage

classencoder = colibricore.ClassEncoder("/home/louis/Data/corpus/small.colibri.cls")
classdecoder = colibricore.ClassDecoder("/home/louis/Data/corpus/small.colibri.cls")
options = colibricore.PatternModelOptions(minlength=1, maxlength=5)
model = colibricore.UnindexedPatternModel()
model.train("/home/louis/Data/corpus/small.colibri.dat", options)

######################
## Run the game

# add stuff to encoder?

import json
# page1144 = json.load(open('/home/louis/Programming/COCOCLINSPCO/data/test/pagesmall.json'))
page1144 = json.load(open('/home/louis/Programming/COCOCLINSPCO/data/validation/page1.json'))
page1144_corrections = page1144['corrections']
page1144_words = page1144['words']



def action_in_sentence(sentence, correction):
    print(correction)
    if correction['class'] == "runonerror":
        for iter,id in enumerate(sentence):
            if id[0] == correction['span'][0]:
                id[1] = correction['text'].split(" ")[0]
                print(id[1] + " " + str(iter))
                id[2] = classencoder.buildpattern(correction['text'].split(" ")[0], allowunknown=False, autoaddunknown=True)
                break
        new_entry = [id[0] + "R",
                     correction['text'].split(" ")[1],
                     classencoder.buildpattern(correction['text'].split(" ")[1], allowunknown=False, autoaddunknown=True),
                     item['space'],
                     item['in']]
        sentence.insert(iter+1, new_entry)
    if correction['class'] == "replace":
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
    if correction['class'] == "missing":
        for iter, id in enumerate(sentence):
            if id[0] == correction['after'][0]:
                break
        new_entry = [id[0] + "M",
                     correction['text'],
                     classencoder.buildpattern(correction['text'], allowunknown=False, autoaddunknown=True),
                     item['space'],
                     item['in']]
        sentence.insert(iter+1, new_entry)

    return sentence

def process(something):
    string_sentence = " ".join([x[1] for x in something])
    wip_sentence = copy.copy(something)

    corrections = []

    print("\nSENTENCE: " + string_sentence)
    for w in window(something, 5):
        string_window = " ".join([x[1] for x in w])
        print("\t===" + string_window)
        #print(missing_words_window(w))

        runon = runon_errors_window(w)
        #change |= split[0]
        if runon[0]:
            corrections.append(runon[2])
            wip_sentence = action_in_sentence(wip_sentence, runon[2])
            # string_sentence = string_sentence.replace(string_window, runon[1])
            # print("\tRUNON:\t" + "replace [" + string_window + "] with [" + runon[1] + "]")
            # print("\t\t>: " + string_sentence)

        replaceable = replaceables_window(w)
        #change |= split[0]
        if replaceable[0]:
            corrections.append(replaceable[2])
            wip_sentence = action_in_sentence(wip_sentence, replaceable[2])
            # string_sentence = string_sentence.replace(string_window, replaceable[1])
            # print("\tREPLA:\t" + "replace [" + string_window + "] with [" + replaceable[1] + "]")
            # print("\t\t>: " + string_sentence)

        split = split_errors_window(w)
        #change |= split[0]
        if split[0]:
            corrections.append(split[2])
            wip_sentence = action_in_sentence(wip_sentence, split[2])
            # string_sentence = string_sentence.replace(string_window, split[1])
            # print("\tSPLIT:\t" + "replace [" + string_window + "] with [" + split[1] + "]")
            # print("\t\t>: " + string_sentence)

        missing = missing_words_window(w)
        #change |= split[0]
        if missing[0]:
            corrections.append(missing[2])
            wip_sentence = action_in_sentence(wip_sentence, missing[2])
    print("\nRESULT: " + " ".join([x[1] for x in wip_sentence]))
    return corrections

sentence = []
page_corrections = []
current_in = page1144_words[0]['in']
for item in page1144_words:
    if current_in != item['in']:
        current_in = item['in']
        page_corrections += process(sentence)
        sentence = []
    sentence.append([item['id'],
                     item['text'],
                     classencoder.buildpattern(item['text'], allowunknown=False, autoaddunknown=True),
                     item['space'],
                     item['in']])
page_corrections += process(sentence)
print(page_corrections)
