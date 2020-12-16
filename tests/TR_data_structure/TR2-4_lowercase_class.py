"""Test file for TR2-4 check.
TR2-4 check detects class names which are not UPPERCASE, i.e. name 
instead of NAME.
"""

class bar():
    pass

class BaRBaR():
    pass

class F00(): # All letters are uppercase, therefore OK.
    attr = 1

class FOO(): # All letters are uppercase, therefore OK.
    attr = 1

def TR2_4(thing):

    return None
# TR2_4()