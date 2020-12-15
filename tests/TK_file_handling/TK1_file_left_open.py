"""Test file for TK1 check.
TK1 check detects file handles which are left open.

Include TK2, which is file open, operation and close are not different 
same function.

Include TK1-1 check which notes that using with open is not desired 
method in THIS course.
"""

def TK1():
    try:
        f = open("test.txt", "r")
        while True:
            sel = input()
            if sel == "0":
                # This is what students do put close in ending branch.
                # Unclear convention but allowed.
                f.close()
                break
            elif sel == "1":
                f.readline()
    except OSError:
        pass


    try:
        f2 = open("test.txt", "r") # This is left open.
        f2.readline()
    except OSError:
        pass

    try:
        with open("test.txt", "r") as f3: # with does not need close()
            f3.readlines()
    except Exception:
        pass

    try:
        f2 = open("test.txt", "w")
        f2.write("qwerty\n")
    except OSError:
        pass
    f2.close()

    return None
# TK1()