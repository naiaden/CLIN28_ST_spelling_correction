import json
import copy

import utils

from correctors import Correctors
from applicator import Applicator

class ProcessSuite:
    def __init__(self, lm, outputdir):
        self.lm = lm
        self.output_dir = outputdir

        self.sos_filler = ['no-id', '<s>', self.lm.bp("<s>"), True, 'no-in']
        self.eos_filler = ['no-id', '</s>', self.lm.bp("</s>"), True, 'no-in']

        self.sent_iter = 0

        self.correctors = Correctors(self.lm)
        self.applicator = Applicator(self.lm)
        
        self.application_cache = {}
        
    def open_file(self, input_file):
        self.file_corrections = []
        self.file_words = []
        self.output_file = input_file.split("/")[-1]

        
        with open(input_file, 'r') as f:
            input_json = json.load(f)
            self.file_words = input_json['words']

        return input_json

    def close_file(self):
        utils.cout({'corrections': self.file_corrections,
                       'words': self.file_words})
        with open(self.output_dir + '/aaa' + self.output_file + '.json', 'w') as f:
            json.dump({'corrections': self.file_corrections,
                       'words': self.file_words}, f)

    def new_sentence(self):
        self.sent_iter += 1
        sentence = []
        sentence.append(self.sos_filler)
        sentence.append(self.sos_filler)
        return sentence

    def close_sentence(self, sentence):
        sentence.append(self.eos_filler)
        sentence.append(self.eos_filler)
        
        if self.sent_iter:
            self.process_sentence(sentence)

    def process_file(self, input_file):
        self.sent_iter = 0
        sentence = self.new_sentence()
        
        self.open_file(input_file)
      
        current_in = self.file_words[0]['in']
        for item in self.file_words:
            if current_in != item['in']:
                current_in = item['in']

                self.close_sentence(sentence)
                sentence = self.new_sentence()
            sentence.append([item['id'],
                             item['text'],
                             self.lm.bp(item['text'], allowunknown=False, autoaddunknown=True),
                             item['space'],
                             item['in']])
        self.close_sentence(sentence)
        
        self.close_file()

                             
    

    def process_sentence(self, sentence):
    
        shadow_wip = copy.copy(sentence)
        sentence_corrections = []

        change = True
        while change:
            utils.cout("[" + str(self.sent_iter) + "] " + utils.word_string(shadow_wip), tabs=1)
            change = False
            for fivegram in utils.window(shadow_wip, size=5):
                utils.cout(utils.word_string(fivegram), tabs=2)
                
                if utils.fake_hash(fivegram) in self.application_cache:
                    utils.cout(">> from cache", tabs=3)
                    corrections = self.application_cache[utils.fake_hash(fivegram)]
                else:
                    corrections = self.correctors.correct(fivegram)
                    self.application_cache[utils.fake_hash(fivegram)] = corrections
                (applied_corrections, shadow_wip, shadow_corrections) = self.applicator.apply(shadow_wip, corrections)
                #sentence_corrections += shadow_corrections
                sentence_corrections += [row[2] for row in shadow_corrections]
                if applied_corrections:
                    change = True
                    break
            
        self.file_corrections += sentence_corrections
        return shadow_wip

        # change
        # corrections
        #self.correctors.correct(sentence)
        

