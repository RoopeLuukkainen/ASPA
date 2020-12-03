"""Test file for PT4-1 check.
PT4-1 check detects infine loops.
"""

def PT4_1(): 
    while True:
        if(0):
            continue
        else:
            try:
                break
            except Exception:
                pass
    while True:
        pass
    return None
# PT4_1()