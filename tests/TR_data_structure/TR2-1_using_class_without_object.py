"""Test file for TR2-1 check.
TR2-1 check detects direct usage of class attributes without an object.
"""

class FOO():
    attr = 1


def TR2_1():
    FOO.attr = 2
    print(FOO.attr)

    return None
# TR2_1()