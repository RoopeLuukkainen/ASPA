"""Test file for PK1-1 check.
PK1-1 check detects except branches without exception type.
By default the last except is allowed to be without type IF there are 
mutliple except-branches.
"""

def PK1_1():
    try:
        1/0
    except: # Error
        pass

    try:
        1/0
    except Exception:
        pass
    # The last except is allowed to be without type IF there are 
    # mutliple except-branches
    except:
        pass
    else:
        pass
    finally:
        pass

    return None
# PK1_1()