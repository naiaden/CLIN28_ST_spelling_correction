import string

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

def create_internal_sentence(lm, sentence):
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
                                  lm.bp(w['text']),
                                  w['space'],
                                  w['in']])
    return internal_sentence
        
def cs(lm, sentence, in_id=None):
    if in_id:
        return create_internal_sentence(lm, create_sentence(sentence.split(), in_id))
    else:
        return create_internal_sentence(lm, create_sentence(sentence.split()))

def word_string(sentence):
    return " ".join([x[1] for x in sentence])

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
