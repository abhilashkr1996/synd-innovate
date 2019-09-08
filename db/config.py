import os, sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

FIRESTORE_CREDENTIALS = parentdir + "/resources/synd-fa75d-9b3fda4b9dfd.json"