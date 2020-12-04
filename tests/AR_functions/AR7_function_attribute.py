"""Test file for AR7 check.
AR7 check detects usage of function attributes.
"""

def AR7():
    AR7.attr = 1
    return None

def func():
    AR7.another.attr.nested.attr = 2 # pylint: disable=no-member
    return None