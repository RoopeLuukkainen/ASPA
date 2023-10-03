"""Test file for PK1-2 check.
PK1-2 check detects allowed exception types in filehandling.
"""
# Allowed types can be modified in config file. Currently only
# Exception is allowed in our course.


class TEMP():
    fhandle = None

def PK1_2():
    t = TEMP()
    try:
        t.fhandle = open("test.txt", "w")
        t.fhandle.write("123\n")
    except OSError:
        pass

    try:
        t.fhandle.write()
    except TypeError:
        pass

    try:
        t.fhandle.close()
    except ZeroDivisionError:
        pass

    try:
        f = open("test.txt", "r")
        f.readline()
        f.close()
    except AttributeError:
        pass

    return None

# PK1_2()
