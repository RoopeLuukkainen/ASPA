"""Test file for TR2-3 check.
TR2-3 check detects class definitions which are not at the global scope.
"""

class BAR():
    class BARBAR():
        pass

def TR2_3(thing):
    class FOO():
        attr = 1

    bar = FOO()
    bar.attr = 2
    print(bar.attr)

    thing.a.b.c.d = FOO()
    return None
# TR2_3()