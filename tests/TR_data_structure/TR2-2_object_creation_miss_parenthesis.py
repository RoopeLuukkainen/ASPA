"""Test file for TR2-2 check.
TR2-2 check detects object creation which misses parenthesis, i.e.
object = CLASS, instead of object = CLASS().
"""

import example_lib_TR

class FOO():
    attr = 1


def TR2_2(thing):
    bar = FOO
    bar.attr = 2
    print(bar.attr)

    thing.a.b.c.d = FOO

    foo = FOO()
    foo.attr = 3

    # FIXME check for class usage from different files
    obj = example_lib_TR.BAR

    return None
# TR2_2()