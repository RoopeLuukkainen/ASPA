"""Test file for AR5-1, AR5-2 and AR5-3 checks.
AR5-1 check detects function calls with too few parameters.
AR5-2 check detects function calls with too many parameters.
AR5-1 check detects function calls with invalid keyword parameter names.
itself.
"""

# import example_lib as lib # FIXME
# from example_lib import * # FIXME
import example_lib

def func0():
    return None

def func1(a, b):
    return None

def func2(a, b, *args):
    return None

def func3(a, b, *args, c=3):
    return None

def func4(a, b, *args, c=3, **kwargs):
    return None

def func5(**kwargs):
    return None

def func6(*args, **kwargs):
    return None


def AR5_1():
    # Too few (1, 2, 3 and 4)
    func0()
    func1(1)                # pylint: disable=no-value-for-parameter
    func2(1)                # pylint: disable=no-value-for-parameter
    func3(1, c=123)         # pylint: disable=no-value-for-parameter
    func4(1, c=123, d=123)  # pylint: disable=no-value-for-parameter
    func5()
    func6(1, d=4, e="5", f=(6,7), g=None)

    example_lib.func1(1)                # pylint: disable=no-value-for-parameter
    example_lib.func2(1)                # pylint: disable=no-value-for-parameter
    example_lib.func3(1, c=123)         # pylint: disable=no-value-for-parameter
    example_lib.func4(1, c=123, d=123)  # pylint: disable=no-value-for-parameter
    example_lib.func5()
    example_lib.func6(1, d=4, e="5", f=(6,7), g=None)
    return None


def AR5_2():
    # Too many (0, 1 and 5)
    func0(1, 2, 3)      # pylint: disable=too-many-function-args
    func1(1, 2, 3)      # pylint: disable=too-many-function-args
    func2(1, 2, 3)
    func3(1, 2, 3, c=123)
    func4(1, 2, 3, c=123, d=123)
    func5(1, 2, 3)      # pylint: disable=too-many-function-args
    func6(1, 2, 3, d=4, e="5", f=(6,7), g=None)

    example_lib.func1(1, 2, 3)      # pylint: disable=too-many-function-args
    example_lib.func2(1, 2, 3)
    example_lib.func3(1, 2, 3, c=123)
    example_lib.func4(1, 2, 3, c=123, d=123)
    example_lib.func5(1, 2, 3)      # pylint: disable=too-many-function-args
    example_lib.func6(1, 2, 3, d=4, e="5", f=(6,7), g=None)
    return None


def AR5_3():
    # Wrong keywords arguments (2 and 3)
    func2(1, 2, 3, d=3)             # pylint: disable=unexpected-keyword-arg
    func3(1, 2, 3, c=123, d=123)    # pylint: disable=unexpected-keyword-arg
    func4(1, 2, 3, c=123, d=123)
    func4(1, 2, 3, d=123, c=123)

    example_lib.func2(1, 2, 3, d=3)             # pylint: disable=unexpected-keyword-arg
    example_lib.func3(1, 2, 3, c=123, d=123)    # pylint: disable=unexpected-keyword-arg
    example_lib.func4(1, 2, 3, c=123, d=123)
    example_lib.func4(1, 2, 3, d=123, c=123)

    # Fixed - check case where function is called with keywords when positional
    # arguments would be enough.
    func1(1, b=2)
    example_lib.func1(1, b=2)

    return None


def paaohjelma():
    AR5_1()
    AR5_2()
    AR5_3()
    return None
paaohjelma()