import pathlib
from functools import singledispatch
import colibricore

class LanguageModel:
    """
    This class holds the language model
    """
    def __init__(self, encoder=None, data=None, model=None):
        if encoder and pathlib.Path(encoder).is_file():
            self.classencoder = colibricore.ClassEncoder(encoder)
            self.classdecoder = colibricore.ClassDecoder(encoder)
        else:
            raise RuntimeError("No valid encoder!")
        
        self.options = colibricore.PatternModelOptions(minlength=1, maxlength=5, mintokens=1)

        if model and pathlib.Path(model).is_file():
            self.model = colibricore.UnindexedPatternModel(model, self.options)
        else:
            if data and pathlib.Path(data).is_file():            
                self.model = colibricore.UnindexedPatternModel()
                self.model.train(data, options)
                self.model.write(model)
            else:
                raise RuntimeError("No valid model and/or data file!")
       
        # This turns out to be faster than set or frozenset
        # However, it is mutable, so do not change
        self.all_words = []
        for w, c in self.model.filter(1, size=1):
            self.all_words.append(w)

    ######################
    ## Global functions on colibricore.Pattern

    def ts(self, pattern):
        """" 
        Returns the string representation of the colibricore.Pattern argument.
        
        >>> ts(bp("patroon"))
        'patroon'
        """
        if type(pattern) is colibricore.Pattern:
            return pattern.tostring(self.classdecoder)
        return str(pattern)

    def oc(self, pattern):
        """ 
        Returns the occurrence count of the colibricore.Pattern argument in the training data.
        
        >>> oc(bp("patroon"))
        170
        """
        if type(pattern) is str:
            pattern = self.bp(pattern)
        if pattern.unknown():
            return 0
        return self.model.occurrencecount(pattern)

    def fr(self, pattern):
        """ 
        Returns the frequency of the colibricore.Pattern argument in the training data.
        The frequency is the normalized occurrence count for the length (order) of the argument.
        
        >>> fr(bp("patroon"))
        1.4490891920364536e-05
        """
        if type(pattern) is str:
            pattern = self.bp(pattern) 
        if pattern.unknown():
            return 0
        return self.model.frequency(pattern)

    def bp(self, string, allowunknown=False, autoaddunknown=False):
        """
        Returns the colibripattern.Pattern representation of string.
        
        >>> bp("patroon")
        <colibricore.Pattern at 0x7f253cf1eab0>
        """
        return self.classencoder.buildpattern(string, allowunknown=allowunknown, autoaddunknown=autoaddunknown)


