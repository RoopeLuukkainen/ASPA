"""Test file for MR1 check.
MR1 check detects correct element order from the file.
"""

# Aliohjelmat
def aliohjelma(a): # name
    print(a)
    return None

async def bar(): # name
    return None

# paaohjelma
def paaohjelma(): # name='paaohjelma'
    a = 1
    foo(a)
    bar()
    return None

def foo(a): # name
    return None

# paaohjelmakutsu
paaohjelma() # value.func.id = 'paaohjelma'
