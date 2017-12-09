import colibricore
import Levenshtein

######################
## Global functions on colibricore.Pattern

def ts(pattern):
    return pattern.tostring(classdecoder)

def oc(pattern):
    return model.occurrencecount(pattern)

def fr(pattern):
    return model.frequency(pattern)

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
        return spattern
    elif f_a_bc_d_e == f_max:
        return a_bc_d_e
    else:
        return a_b_cd_e

#p2 = classencoder.buildpattern("een vlinder ui t de")
#split_errors(p2)

# Compare frequency of (a b cd e) and (a bc d e) with (a b c d e)
def runon_errors(pattern):
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
                best_f = f_candidate
                best_s = s_candidate

    return best_s

#p1 = classencoder.buildpattern("een vlinder uit de familie")
#runon_errors(p1)

# archaic, non-word and confusables:
# Compare frequency of (a b c d e) with (a b X d e)
def replaceables(pattern):
    best_f = fr(pattern)
    best_s = ts(pattern)
    c = ts(pattern[2])

    for word,count in model.filter(1, size=1):
        if not word.unknown() and Levenshtein.distance(ts(word), c) < 4:
            a_b_X_d_e = ts(pattern[0:2]) + " " + ts(word) + " " + ts(pattern[3:5])
            p_a_b_X_d_e = classencoder.buildpattern(a_b_X_d_e)
            if fr(p_a_b_X_d_e) > best_f:
                best_f = fr(p_a_b_X_d_e)
                best_s = a_b_X_d_e
    return best_s

#p3 = classencoder.buildpattern("een vlinder vit de familie")
#replaceables(p3)

# Compare frequency of (a b c d e) with (a b c X d e) (e is ignored)
def missing_words(pattern):
    best_f = fr(pattern)
    best_s = ts(pattern)

    for word,count in model.filter(1, size=1):
        if not word.unknown():
            a_b_c_X_d_e = ts(pattern[0:3]) + " " + ts(word) + " " + ts(pattern[3:4])
            p_a_b_c_X_d_e = classencoder.buildpattern(a_b_c_X_d_e)
            f_a_b_c_X_d_e = fr(p_a_b_c_X_d_e)
            if f_a_b_c_X_d_e > best_f:
                best_f = f_a_b_c_X_d_e
                best_s = a_b_c_X_d_e
    return best_s

#p4 = classencoder.buildpattern("een vlinder uit familie van")
#missing_words(p4)

######################
## Run the game

classencoder = colibricore.ClassEncoder("/home/louis/Data/corpus/small.colibri.cls")
classdecoder = colibricore.ClassDecoder("/home/louis/Data/corpus/small.colibri.cls")
options = colibricore.PatternModelOptions(minlength=1, maxlength=5)
model = colibricore.UnindexedPatternModel()
model.train("/home/louis/Data/corpus/small.colibri.dat", options)
