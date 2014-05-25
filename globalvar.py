#!/usr/bin/env python
from database import *
from sys import argv
import os

scriptPath = os.path.abspath(os.path.dirname(argv[0]))

bcolors = {
    "HEADER": '\033[95m',
    "OKBLUE": '\033[94m',
    "OKGREEN": '\033[92m',
    "WARNING": '\033[93m',
    "FAIL": '\033[91m',
    "ENDC": '\033[0m',
}

ratingThreshold = 0.1