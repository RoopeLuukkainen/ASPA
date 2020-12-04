"""Test file for AR1 check.
AR1 check detects naming of 'main' function which name is defined in
the config.py file's MAIN_FUNC_NAME variable. Originally the name is 
'paaohjelma'.
"""

# When there is a function call at global scope it should be 
# 1. paaohjelma() and 2. then there should be def paaohjelma() as well.
# Because of the 2. reason this files gives warning also AR1() being
# in wrong place (should only be paaohjelma()-call at global scope).
def AR1():
    return None
AR1()