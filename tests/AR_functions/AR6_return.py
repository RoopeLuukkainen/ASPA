"""Test file for AR6, AR6-2, AR6-3, AR6-4, AR6-5, AR6-6 checks.
AR6 check detects functions which does not have return command as the 
last command.

AR6-2 check detects return command which are at the middle of the 
function. 

AR6-3 check detects return command without return value

AR6-4 check detects return command with constant return value.
constants are e.g. int or str types but not True, False, None.

AR6-5 check detects return command with multiple return values.

AR6-6 check detects return command with some other typed return value.
E.g. logical operation 'a or b' or arithmetic operation 'a + b'.  
"""

def AR6():
    pass

def AR6_2(num):
    if(num % 3):
        return False
    return True

def AR6_3():
    return

def AR6_4a():
    return 1

def AR6_4b():
    return "1"

def AR6_5():
    a = b = 1
    return a, b

def AR6_6a():
    a = b = 1
    return a or b # should give note

def AR6_6b():
    a = b = 1
    return a - b # should give note

def AR6_6c():
    a = b = 1
    return a > b # should give note

def AR6_6z():
    return AR6() # should NOT give note
