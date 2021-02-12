"""Test file for PK1 check.
PK1 check detects exception handling structures without any except
branches.
"""

def PK1():
    try: # Error 1
        1/1
    finally:
        try: # Error 2
            a = 1
        finally:
            pass

    try:
        1/0
    except ZeroDivisionError:
        pass
    else:
        pass

    # try:
    #     1/1
    # else: # Syntax error
    #     pass

    try:
        a = []
        a[1] = 2
    except IndexError:
        pass
    else:
        pass
    finally:
        pass

    try:
        1/0
    except ZeroDivisionError:
        pass
    finally:
        pass


    return None
# PK1()