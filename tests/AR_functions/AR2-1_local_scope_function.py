"""Test file for AR2-1 check.
AR2-1 check detects functions in local scopes, i.e. class methods and 
nested functions.

It is possible to allow and deny functions in config.py file's 
ALLOWED_FUNCTIONS and DENIED_FUNCTIONS sets.

By default __init__ is allowed and everything else is denied.
"""

class ARCLASS():
    def __init__(self):
        pass

    def nested_method(self):
        def nested_method_2(self):
            return None
        return None


def AR2_1(): 
    def nest1():
        async def nest2():
            def nest3():
                return None
            return None
        return None
    return None
# AR2-1()