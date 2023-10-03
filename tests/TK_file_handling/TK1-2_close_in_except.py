"""Test file for TK1-2 check.
TK1-2 check detects file handles which are closed in except-branch.
"""

def TK1_2():
    try:
        f1 = open("test.txt", "w")
        f1.write("qwerty\n")
    except Exception:
        f1.close()

        f2 = open("test.txt", "r")
        f2.close()

    try:
        f3 = open("test.txt", "a")
        f3.write("qwerty\n")
    except Exception:
        pass
    finally:
        f3.close()

    try:
        f4 = open("test.txt", "a")
        f4.write("qwerty\n")
    except Exception:
        pass
    else:
        f4.close()


    return None
# TK1_2()