"""Test file for PK4 check.
PK4 check detects file operations without exception handling.
"""

class TEMP():
    fhandle = None

def PK4():
    t = TEMP()
    try:
        t.fhandle = open("test.txt", "w")
        t.fhandle.write("123\n")
    except Exception:
        pass
    t.fhandle.write()

    try:
        t.fhandle.close()
    except Exception:
        pass

    try:
        f = open("test.txt", "r")
        f.readline()
    except Exception:
        pass
    line = f.readline()
    everyting = f.read()
    f.readlines()
    for _ in f: pass

    print(line, everyting)

    try:
        f.close()
    except Exception:
        pass

    return None

def foo():
    """
    This is a bug, because creates error of for loop considered as a
    file operation. This is because the check does not confirm that file
    is opened in same function. Only check the filehandle name.
    """

    f = [1, 2, 3]
    for this_is_a_bug in f:
        print(this_is_a_bug)
    return None
# PK4()