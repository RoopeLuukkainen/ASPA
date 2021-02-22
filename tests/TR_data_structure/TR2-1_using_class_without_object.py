"""Test file for TR2-1 check.
TR2-1 check detects direct usage of class attributes without an object.
"""

import example_lib_TR

class FOO():
    attr = 1


def TR2_1():
    FOO.attr = 2
    print(FOO.attr)

    # FIXME check for class usage from different files
    example_lib_TR.BAR.attribute = 2

    return None
# TR2_1()