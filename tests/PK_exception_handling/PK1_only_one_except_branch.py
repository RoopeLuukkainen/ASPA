"""Test file for PK1 check.
PK1 check detects exception handling structures with only one (1) except
branch. By default this is violation ignored.
"""

def PK1():
    try: # Error 1
        1/1
    except Exception:
        pass

    try: # Error 2
        1/0
    except ZeroDivisionError:
        pass
    else:
        pass

    try: # Error 3
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
    except Exception:
        pass


    return None
# PK1()