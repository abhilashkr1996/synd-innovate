import os, sys

currentdir = os.path.dirname(os.path.realpath(__file__))

if currentdir not in sys.path:
    sys.path.insert(0,currentdir)
