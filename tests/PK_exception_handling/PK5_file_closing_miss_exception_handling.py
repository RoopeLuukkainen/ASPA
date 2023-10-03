"""Test file for PK5 check.
PK5 check detects file closing without exception handling.
"""

class TEMP():
    fhandle = None

def PK5():
    t = TEMP()
    try:
        t.fhandle = open("test.txt", "w")
        t.fhandle.write("123\n")
    except Exception:
        pass

    try:
        t.fhandle.write()
    except Exception:
        pass

    t.fhandle.close()

    try:
        f = open("test.txt", "r")
        f.readline()
    except Exception:
        pass

    f.close()
    return None

# PK5()
