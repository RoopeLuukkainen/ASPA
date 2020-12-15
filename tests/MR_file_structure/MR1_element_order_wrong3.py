"""Test file for MR1 check.
MR1 check detects correct element order from the file.
"""

# Aliohjelmat
def aliohjelma(a): # name
    print(a)
    return None

async def bar(): # name
    return None

def foo(a): # name
    return None

# Luokat
class A: # name
    a = 1

class B:
    a = 1

class C:
    var = 100

# paaohjelma
def paaohjelma(): # name='paaohjelma'
    a = A()
    foo(a)
    bar()
    return None

# paaohjelmakutsu
paaohjelma() # value.func.id = 'paaohjelma'
