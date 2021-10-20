"""Test file for TK1 check.
TK1 check detects file handles which are left open.

FIXME case where file is opened in two different branches but closed
only after the branches. Current analyser sees this as an error.
"""


def TK1(argument):
    try:
        if argument:
            f = open("test.txt", "w") # FIXME, this is not left open
        else:
            f = open("test.txt", "a")
        f.write("qwerty\n")
        f.close()
    except OSError:
        pass

    try:
        f2 = open("test.txt", "r") # FIXME, this is not left open
        f2.write("qwerty\n")
    except Exception:
        try:
            f2 = open("test.txt", "w")
            f2.read()
        except OSError:
            pass
    f2.close()

    return None
# TK1()