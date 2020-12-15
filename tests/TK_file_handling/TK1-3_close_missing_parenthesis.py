"""Test file for TK1-3 check.
TK1-3 check detects file closes which miss function call parenthesis,
i.e. filehandle.close instead of filehandle.close().
"""

def TK1_3():
    try:
        f1 = open("test.txt", "w")
        f1.write("qwerty\n")
        f1.close
    except OSError:
        pass

    return None
# TK1_3()