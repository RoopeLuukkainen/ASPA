"""Test file for PK3 check.
PK3 check detects file openings without exception handling.
PK5 check detects file openings without exception handling.
Include TK1-1 check which notes that using with open is not desired
method in THIS course.
"""

def PK3():
    try:
        f = open("test.txt", "w")
        f.close()
    except OSError:
        pass

    try:
        f = open("test.txt", "r")
        f.close()
    except OSError:
        pass

    try:
        with open("test.txt", "r") as f:
            pass
    except Exception:
        pass

    f = open("test.txt", "w")   # 1. Error PK3
    f.close()                   # 1. Error PK5
    f = open("test.txt", "r")   # 2. Error PK3
    f.close()                   # 2. Error PK5

    with open("test.txt", "r") as f: # 3. Error PK3 and TK1-1
        pass

    return None
# PK3()