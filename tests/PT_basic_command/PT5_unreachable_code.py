"""Test file for PT5 check.
PT5 check detects unreachable code blocks.

Include TK1-1 check which notes that using with open is not desired 
method in THIS course.
"""

import sys

def PT5():
    for n in range(5):
        if(n % 2 == 0):
            break
            continue
            raise Exception
            print("Lopetetaan")
        else:
            quit(0)
            exit(0)
            sys.exit(0)
            pass
    return None
    return None

# FUNCTION BODY
def paaohjelma():
    # IF-ELIF-ELSE
    if True:
        return None
        pass
    elif False:
        sys.exit(1)
        exit(0)
        quit(1)
        pass
    else:
        return None
        pass

    # FOR-ELSE
    for _ in range(1):
        continue
        break
        pass
    else:
        return None
        raise KeyboardInterrupt
        pass

    # TRY-EXCEPT-ELSE-FINALLY
    try:
        # WITH
        with open("a.txt", "r") as f:
            return None
            pass
        return None
        pass
    except Exception:
        return None
        pass
    else:
        return None
        pass
    finally:
        return None
        pass

    # WHILE-ELSE
    while(True):
        return None
        pass
    else:
        return None
        pass
    return None

# PT5()
