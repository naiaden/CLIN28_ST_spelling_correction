import json
import copy

import utils

from correctors import Correctors

class ProcessSuite:
    def __init__(self, lm, outputdir):
        self.lm = lm
        self.output_dir = outputdir

        self.sos_filler = ['no-id', '<s>', self.lm.bp("<s>"), True, 'no-in']
        self.eos_filler = ['no-id', '</s>', self.lm.bp("</s>"), True, 'no-in']

        self.sent_iter = 0

        self.correctors = Correctors(self.lm)

    def open_file(self, input_file):
        self.file_corrections = []
        self.file_words = []

        
        with open(input_file, 'r') as f:
            input_json = json.load(f)
            self.file_words = input_json['words']

        return input_json

    def close_file(self):
        with open(self.output_dir + 'asdasd.json', 'w') as f:
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
        #print(sentence)

        string_sentence = " ".join([x[1] for x in sentence])
        wip_ssentence = copy.copy(sentence)

        for fivegram in utils.window(wip_ssentence, size=5):
            print(utils.word_string(fivegram))
            self.correctors.correct(fivegram)

        # change
        # corrections
        #self.correctors.correct(sentence)
        

