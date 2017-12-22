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

from lm import LanguageModel
from test import TestSuite
from produce import ProcessSuite

argparser = argparse.ArgumentParser(description="Spelling correction based on 5-grams.", epilog="Developed for the CLIN28 shared task on spelling correction for contemporary Dutch. Reach me at louis@naiaden.nl for questions or visit https://github.com/naiaden/COCOCLINSPCO/")
argparser.add_argument('classfile', help="encoded classes")
argparser.add_argument('datafile', help="encoded data")
argparser.add_argument('modelfile', help="(un)indexed pattern model")
argparser.add_argument('outputdir', help="output directory")
args, unknown_args = argparser.parse_known_args()

if not unknown_args:
    print("Missing input files. \n A B O R T")
    sys.exit()

try:
    lm = LanguageModel(encoder=args.classfile, data=args.datafile, model=args.modelfile)
#lm = LanguageModel(encoder='/home/louis/Data/corpus/small.colibri.cls', data='/home/louis/Data/corpus/small.colibri.dat', model='/home/louis/Data/corpus/small.colibri.model')
except RuntimeError as err:
    print("Caught a run-time error:", err)
    sys.exit(-2)

outputdir = args.outputdir
#outputdir = '/home/louis/Programming/COCOCLINSPCO/data/output/'

run_tests = True

if run_tests:
    testsuite = TestSuite(lm)
    testsuite.run_tests()
    testsuite.report()
else:
    productionsuite = ProcessSuite(lm, outputdir)
    for f in unknown_args:
        # if in do-not-process list: do not process
        try:
            productionsuite.process_file(f)
        except FileNotFoundError as err:
            print("Caught a file not found error:", err)
            print("I will ignore this file")
            


