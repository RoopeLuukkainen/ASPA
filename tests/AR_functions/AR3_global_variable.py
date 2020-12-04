"""Test file for AR3 check.
AR3 check detects global variables. Global constants are allowed.
"""

variable = a = "abc" # Global variable 'variable'.; Global CONSTANT 'a'.
global_list = []

# Global tuple is allowed if its value is unchanged.
global_tuple_is_allowed = ("a", "b", "c")
# Global tuple become variable if variable with same name is assigned again
unless_assigned_again = (1, 2)
unless_assigned_again = (3, 4)


def AR3(var): 
    # 'variable' is actually local variable but it is considered as 
    # global because students may try to use it similarly as global 
    # lists, i.e. without global keyword.
    variable = var
    global_list.append(variable)

    global with_global_keyword, another_global
    with_global_keyword = 987

    c = global_tuple_is_allowed # usage of tuple is allowed
    print(c, global_tuple_is_allowed)
    return None


def paaohjelma(a):
    print(a)
    b = a
    print(b)
    AR3("parameter")
    return None
paaohjelma(a)
