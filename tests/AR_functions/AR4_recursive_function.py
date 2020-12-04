"""Test file for AR4 check.
AR4 check detects usage of direct recursion, i.e. function calling
itself.
"""

def AR4(num):
    """Countdown function."""

    print(num)
    if(num > 0): 
        AR4(num - 1)
    return None
# AR4(10)