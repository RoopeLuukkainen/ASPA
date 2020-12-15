"""Test file for PK3 check.
PK3 check detects file openings without exception handling.
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

    f = open("test.txt", "w") # Error 1
    f.close()
    f = open("test.txt", "r") # Error 2
    f.close()

    with open("test.txt", "r") as f: # Error 3
        pass

    return None
# PK3()