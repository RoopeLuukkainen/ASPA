"""Test file for PT2 check.
PT2 check detects naming of identifiers.
"""

# Valid naming schema (require ascii alphabets, numbers and underscore)
# --- VALID IMPORT AS --- #
import os
import math as maa
from datetime import datetime as dt

# --- INVALID IMPORT AS --- #
import sys as systäämi
from ast import parse as pår


# --- VALID CLASS --- #
class LUOKKA:
    pass

# --- INVALID CLASS --- #
class ÄÖÅ:
    pass

# --- INVALID FUNCTION --- #
def ääkkönen():
    return None

def ÄÄKKÖNEN():
    return None

def é():
    return None

def è():
    return None

async def í(vör):
    return None

async def Ì(vääär, *årgs, Öû=1, **kwärgs):
    return None


# --- VALID FUNCTION --- #
def _foo():
    return None

def BAR(var1, var2):
    return None

async def FOO_bar(VAR1, *args, VAR3_=1, **kwargs):
    return None

def ___ba1233456_8afoo0932_():
    return None

def PT2(func):
    # --- VALID ASSING --- #
    test29 = 0
    test_29 = 1
    _test29 = 2
    abcdefghijklmnopqrstuvwxyz = 3
    ABCDEFGHIJKLMNOPQRSTUVWXYZ = 4
    abCDEFGHIJklMNOPQrSTUVWXyZ = 5

    # --- INVALID ASSING --- #
    # test29- = 2 # syntax error
    # 29test = 2 # syntax error
    å = 0
    ä = 1
    ö = 2
    ü = 3

    # --- VALID FOR --- #
    for i, j in [(1,2), (3,4)]:
        print(i)

    # --- INVALID FOR --- #
    for ääö, ÖÖÄ_ in [(1,2), (3,4)]:
        print(ääö, ÖÖÄ_)

    # --- VALID WITH --- #
    try:
        # parameter func is used here to prevent detection of 'with open'-note.
        with func("a.txt", "w") as valid:
            pass
    except Exception:
        pass

    try:
        # parameter func is used here to prevent detection of 'with open'-note.
        with func("b.txt", "w"):
            pass
    except Exception:
        pass

    # --- INVALID WITH --- #
    try:
        # parameter func is used here to prevent detection of 'with open'-note.
        with func("a.txt", "w") as învÄlÏd:
            pass
    except Exception:
        pass
    # --- VALID EXCEPT AS --- #
    try:
        1/0
    except ZeroDivisionError as ZDE:
        pass

    try:
        pass
    except (KeyError, ValueError) as KVE:
        pass

    # --- INVALID EXCEPT AS --- #
    try:
        1/0
    except ZeroDivisionError as ZÄ:
        pass

    try:
        pass
    except (KeyError, ValueError) as Kävö:
        pass

    # Usage of keywords actually gives syntax error when parsing with AST
    # if = 1
    return None
# PT2()