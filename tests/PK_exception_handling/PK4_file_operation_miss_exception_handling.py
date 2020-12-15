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
    except OSError:
        pass
    t.fhandle.write()
    t.fhandle.close()

    try:
        f = open("test.txt", "r")
        f.readline()
    except OSError:
        pass
    line = f.readline()
    everyting = f.read()
    f.readlines()
    for _ in f: pass

    print(line, everyting)
    f.close()


    return None
# PK4()