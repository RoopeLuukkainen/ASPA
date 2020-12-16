"""Test file for TR2-2 check.
TR2-2 check detects object creation which misses parenthesis, i.e.
object = CLASS, instead of object = CLASS().
"""

class FOO():
    attr = 1


def TR2_2(thing):
    bar = FOO
    bar.attr = 2
    print(bar.attr)

    thing.a.b.c.d = FOO
    return None
# TR2_2()