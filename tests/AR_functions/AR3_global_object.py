"""Test file for AR3 check.
AR3 check detects global variables. Global constants are allowed.

Originally file for AR3-2 check but it is not used currently.
"""

class EXAMPLE:
    foo = 1
global_object = EXAMPLE()
global_object2 = EXAMPLE()
CONSTANT_OBJECT = EXAMPLE()

def paaohjelma():
    global_object.foo = 2
    global_object2.foo += 3
    return None