"""Test file for PT5 check.
PT5 check detects unreachable code blocks.
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
# PT5()
