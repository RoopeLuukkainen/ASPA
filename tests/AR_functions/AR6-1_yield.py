"""Test file for AR6-1 check.
AR6-1 check detects usage of generators 'yield' and 'yield from'.
"""
# FIXME currently also AR6-7, missing return as yield or yield from are
# not counted as returns.

def AR6_1(num):
    for i in range(1, num + 1):
        if(i % 2 == 0):
            yield i

def AR6_1_b(func):
    yield from func