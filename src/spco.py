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

######################
## Correction units

# Compare frequency of (a b c d e) with (a b cd e) and (a bc d e)
def split_errors(pattern):
    spattern = ts(pattern)
    f_a_b_c_d_e = fr(pattern)
    #print("a b c d e:\t" + str(o_a_b_c_d_e) + "\t" + str(f_a_b_c_d_e) + "\t" + spattern)

    t_spattern = spattern.split(" ")

    a_bc_d_e = t_spattern[0] + " " + t_spattern[1] + t_spattern[2] + " " + t_spattern[3] + " " + t_spattern[4]
    p_a_bc_d_e = classencoder.buildpattern(a_bc_d_e)
    f_a_bc_d_e = fr(p_a_bc_d_e)
    #print("a bc d e:\t" + str(f_a_bc_d_e) + "\t" + a_bc_d_e)

    a_b_cd_e = t_spattern[0] + " " + t_spattern[1] + " " + t_spattern[2] + t_spattern[3] + " " + t_spattern[4]
    p_a_b_cd_e = classencoder.buildpattern(a_b_cd_e)
    f_a_b_cd_e = fr(p_a_b_cd_e)
    #print("a bc d e:\t" + str(f_a_b_cd_e) + "\t" + a_b_cd_e)

    f_max = max(f_a_b_c_d_e, f_a_bc_d_e, f_a_b_cd_e)
    if f_a_b_c_d_e == f_max:
        return (False, spattern)
    elif f_a_bc_d_e == f_max:
        return (True, a_bc_d_e)
    else:
        return (True, a_b_cd_e)

#p2 = classencoder.buildpattern("een vlinder ui t de")
#split_errors(p2)

# Compare frequency of (a b cd e) and (a bc d e) with (a b c d e)
def runon_errors(pattern):
    something_happened = False

    best_f = fr(pattern)
    best_s = ts(pattern)

    t_pattern = ts(pattern).split(" ")
    middle = "".join(t_pattern[1:4])

    for x in range(len(middle)):
        for y in range(len(middle)):
            candidate = copy.copy(middle)
            candidate = '{0} {1}'.format(candidate[:x], candidate[x:])
            candidate = '{0} {1}'.format(candidate[:y], candidate[y:])

            s_candidate = (t_pattern[0] + " " + candidate + " " + t_pattern[4]).replace("  ", " ")
            p_candidate = classencoder.buildpattern(s_candidate)
            f_candidate = fr(p_candidate)
            if f_candidate > best_f:
                something_happened = True
                best_f = f_candidate
                best_s = s_candidate

    return (something_happened and best_s != ts(pattern), best_s)

#p1 = classencoder.buildpattern("een vlinder uit de familie")
#runon_errors(p1)

# archaic, non-word and confusables:
# Compare frequency of (a b c d e) with (a b X d e)
def replaceables(pattern):
    nothing_happened = True

    best_f = fr(pattern)
    best_s = ts(pattern)
    c = ts(pattern[2])

    for word,count in model.filter(1, size=1):
        if not word.unknown() and Levenshtein.distance(ts(word), c) < 2:
            a_b_X_d_e = ts(pattern[0:2]) + " " + ts(word) + " " + ts(pattern[3:5])
            p_a_b_X_d_e = classencoder.buildpattern(a_b_X_d_e)
            if fr(p_a_b_X_d_e) > best_f:
                nothing_happened = False
                best_f = fr(p_a_b_X_d_e)
                best_s = a_b_X_d_e

    if nothing_happened:
        for word,count in model.filter(1, size=1):
            if not word.unknown() and Levenshtein.distance(ts(word), c) < 2:
                a_b_X_d_e = ts(pattern[1:2]) + " " + ts(word) + " " + ts(pattern[3:4])
                p_a_b_X_d_e = classencoder.buildpattern(a_b_X_d_e)
                if fr(p_a_b_X_d_e) > best_f:
                    nothing_happened = False
                    best_f = fr(p_a_b_X_d_e)
                    best_s = a_b_X_d_e
        if not nothing_happened:
            best_s = ts(pattern[0]) + " " + best_s + " " + ts(pattern[4])
    return (not nothing_happened and best_s != ts(pattern), best_s)

#p3a = classencoder.buildpattern("een vlinder vit de familie")
#replaceables(p3a)
p3b = classencoder.buildpattern("is een vlnder uit familie")
replaceables(p3b)

# Compare frequency of (a b c d e) with (a b c X d e) (e is ignored)
def missing_words(pattern):
    something_happened = False

    best_f = fr(pattern)
    best_s = ts(pattern)

    for word,count in model.filter(1, size=1):
        if not word.unknown():
            a_b_c_X_d_e = ts(pattern[0:3]) + " " + ts(word) + " " + ts(pattern[3:4])
            p_a_b_c_X_d_e = classencoder.buildpattern(a_b_c_X_d_e)
            f_a_b_c_X_d_e = fr(p_a_b_c_X_d_e)
            if f_a_b_c_X_d_e > best_f:
                something_happened = True
                best_f = f_a_b_c_X_d_e
                best_s = a_b_c_X_d_e
    return (something_happened and best_s != ts(pattern), best_s)



#p4 = classencoder.buildpattern("een vlinder uit familie van")
#missing_words(p4)

######################
## Set the stage

classencoder = colibricore.ClassEncoder("/home/louis/Data/corpus/small.colibri.cls")
classdecoder = colibricore.ClassDecoder("/home/louis/Data/corpus/small.colibri.cls")
options = colibricore.PatternModelOptions(minlength=1, maxlength=5)
model = colibricore.UnindexedPatternModel()
model.train("/home/louis/Data/corpus/small.colibri.dat", options)

######################
## Run the game

test_sentence = "\"Argyroploce lutosana\" is een vlnder uit familie van de bladrollers (Tortricidae)."
pts = classencoder.buildpattern(test_sentence, allowunknown=False, autoaddunknown=True)

classencoder.save('/tmp/ce')
classdecoder = colibricore.ClassDecoder('/tmp/ce')

ts(pts)
change = True
final_sentence = copy.copy(test_sentence)
while change:
    change = False
    pts = classencoder.buildpattern(final_sentence, allowunknown=False, autoaddunknown=True)
    print("--------------" + final_sentence + "--------------")

    for fivegram in pts.ngrams(5):
        print("===" + ts(fivegram) + "===")

        runon = runon_errors(fivegram)
        change |= runon[0]
        if runon[0]:
            final_sentence = final_sentence.replace(ts(fivegram), runon[1])
            print("RUNON:\t" + "replace " + ts(fivegram) + " with " + runon[1])

        split = split_errors(fivegram)
        change |= split[0]
        if split[0]:
            final_sentence = final_sentence.replace(ts(fivegram), split[1])
            print("SPLIT:\t" + "replace " + ts(fivegram) + " with " + split[1])

        replace = replaceables(fivegram)
        change |= replace[0]
        if replace[0]:
            final_sentence = final_sentence.replace(ts(fivegram), replace[1])
            print("REPLA:\t" + "replace " + ts(fivegram) + " with " + replace[1])

        missing = missing_words(fivegram)
        change |= missing[0]
        if missing[0]:
            final_sentence = final_sentence.replace(ts(fivegram[0:4]), missing[1])
            print("MISNG:\t" + "replace " + ts(fivegram) + " with " + missing[1])
    print(change)

print(final_sentence)

######################
## what

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
## Going for the finals['text']

# add stuff to encoder?

import json
page1144 = json.load(open('/home/louis/Programming/COCOCLINSPCO/data/test/pagesmall.json'))
page1144_corrections = page1144['corrections']
page1144_words = page1144['words']

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
    correction = {}
    correction['class'] = "missingword"
    correction['after'] = ws[2][0]
    correction['text'] = best_w
    return (something_happened and best_s != " ".join(words), best_s, correction)

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

    a_b_cd_e = ws[2][1]+ws[3][1]
    p_a_b_cd_e = classencoder.buildpattern(a_b_cd_e)
    f_a_b_cd_e = fr(p_a_b_cd_e)

    if f_a_b_cd_e > best_f and not oc(classencoder.buildpattern(ws[1][1]+" "+ws[2][1])):
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
    print(sentence)

def process(something):
    string_sentence = " ".join([x[1] for x in something])
    wip_sentence = copy.copy(something)
    print("\nSENTENCE: " + string_sentence)
    for w in window(something, 5):
        string_window = " ".join([x[1] for x in w])
        print("\t===" + string_window)
        #print(missing_words_window(w))

        runon = runon_errors_window(w)
        #change |= split[0]
        if runon[0]:
            action_in_sentence(wip_sentence, runon[2])
            # string_sentence = string_sentence.replace(string_window, runon[1])
            # print("\tRUNON:\t" + "replace [" + string_window + "] with [" + runon[1] + "]")
            # print("\t\t>: " + string_sentence)

        replaceable = replaceables_window(w)
        #change |= split[0]
        if replaceable[0]:
            action_in_sentence(wip_sentence, replaceable[2])
            # string_sentence = string_sentence.replace(string_window, replaceable[1])
            # print("\tREPLA:\t" + "replace [" + string_window + "] with [" + replaceable[1] + "]")
            # print("\t\t>: " + string_sentence)

        split = split_errors_window(w)
        #change |= split[0]
        if split[0]:
            pass
            # string_sentence = string_sentence.replace(string_window, split[1])
            # print("\tSPLIT:\t" + "replace [" + string_window + "] with [" + split[1] + "]")
            # print("\t\t>: " + string_sentence)
    print("\nRESULT: " + string_sentence)

sentence = []
current_in = page1144_words[0]['in']
for item in page1144_words:
    if current_in != item['in']:
        current_in = item['in']
        process(sentence)
        sentence = []
    sentence.append([item['id'],
                     item['text'],
                     classencoder.buildpattern(item['text'], allowunknown=False, autoaddunknown=True),
                     item['space'],
                     item['in']])
process(sentence)
