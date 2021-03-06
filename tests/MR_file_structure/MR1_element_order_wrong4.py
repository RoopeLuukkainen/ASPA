"""Test file for MR1 check.
MR1 check detects correct element order from the file.
"""

# Importit
import os
import math # names[name]
from datetime import datetime # names[name]
import sys

# Kiintoarvot
CONST = 1 # targets[id]

# Luokat
class A: # name
    a = 1

class B:
    a = 1

class C:
    var = 100

# Aliohjelmat
def aliohjelma(a): # name
    print(a)
    return None

async def bar(): # name
    return None

def foo(a): # name
    return None

# paaohjelmakutsu
paaohjelma() # value.func.id = 'paaohjelma'

# paaohjelma
def paaohjelma(): # name='paaohjelma'
    return None
