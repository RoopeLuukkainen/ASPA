"""Test file for MR1 check.
MR1 check detects correct element order from the file.
"""

# Luokat
class A: # name
    a = 1

class B:
    a = 1

class C:
    var = 100

# Importit
import os
import math # names[name]
from datetime import datetime # names[name]
import sys

# Kiintoarvot
CONST = 1 # targets[id]



# paaohjelma
def paaohjelma(): # name='paaohjelma'
    return None

# paaohjelmakutsu
paaohjelma() # value.func.id = 'paaohjelma'
