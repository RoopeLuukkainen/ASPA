"""Test file for PK1-1 check.
PK1-1 check detects except branches without exception type.
"""

def PK1_1():
    try:
        1/0
    except: # Error 1
        pass

    try:
        1/0
    except ZeroDivisionError:
        pass
    except: # Error 2
        pass
    else:
        pass
    finally:
        try:
            1/0
        except:  # Error 3
            pass


    return None
# PK1_1()