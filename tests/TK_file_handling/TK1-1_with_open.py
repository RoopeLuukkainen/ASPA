"""Test file for TK1-1 check.
TK1-1 check detects usage of 'with open' which is not desired method in
THIS course.
"""

def TK1_1():
    try:
        with open("test.txt", "r") as f3:
            f3.readlines()
    except Exception:
        pass

    return None
# TK1_1()