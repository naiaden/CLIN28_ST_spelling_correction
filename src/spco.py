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

#import ./lm

argparser = argparse.ArgumentParser(description="Spelling correction based on 5-grams.", epilog="Developed for the CLIN28 shared task on spelling correction for contemporary Dutch. Reach me at louis@naiaden.nl for questions or visit https://github.com/naiaden/COCOCLINSPCO/")
argparser.add_argument('classfile', help="encoded classes")
argparser.add_argument('datafile', help="encoded data")
argparser.add_argument('modelfile', help="(un)indexed pattern model")
argparser.add_argument('outputdir', help="output directory")
args, unknown_args = argparser.parse_known_args()

if not unknown_args:
    print("Missing input files. \n A B O R T")
    sys.exit()

#lm = LanguageModel(encoder=args.classfile, data=args.datafile, model=args.modelfile)
#lm = LanguageModel(encoder='/home/louis/Data/corpus/small.colibri.cls', data='/home/louis/Data/corpus/small.colibri.dat', model='/home/louis/Data/corpus/small.colibri.model')


outputdir = args.outputdir
#outputdir = '/home/louis/Programming/COCOCLINSPCO/data/output/'

