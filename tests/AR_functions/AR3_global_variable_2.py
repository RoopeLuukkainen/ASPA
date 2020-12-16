"""2nd test file for AR3 check.
AR3 check detects global variables. Global constants are allowed.
"""

# GLOBAL VARIABLES
abc = foo()
# value to a is assigned again later, therefore it is global
a = 1                   # Assign(targets=[Name(id='a', ctx=Store())], value=Constant(value=1, kind=None), type_comment=None)
d = []                  # Assign(targets=[Name(id='d', ctx=Store())], value=List(elts=[], ctx=Load()), type_comment=None)
e = {}                  # Assign(targets=[Name(id='e', ctx=Store())], value=Dict(keys=[], values=[]), type_comment=None)
g = set()               # Assign(targets=[Name(id='g', ctx=Store())], value=Call(func=Name(id='set', ctx=Load()), args=[], keywords=[]), type_comment=None)
d2 = list()             # Assign(targets=[Name(id='d2', ctx=Store())], value=Call(func=Name(id='list', ctx=Load()), args=[], keywords=[]), type_comment=None)
e2 = dict()             # Assign(targets=[Name(id='e2', ctx=Store())], value=Call(func=Name(id='dict', ctx=Load()), args=[], keywords=[]), type_comment=None)

# g2 is considered a global, because tuple() creates a Call node not Tuple.
g2 = tuple()            # Assign(targets=[Name(id='g2', ctx=Store())], value=Call(func=Name(id='tuple', ctx=Load()), args=[], keywords=[]), type_comment=None)

# j is considered a global, because it is not Constant nor Tuple node but BinOp.
j = 1 + 2               # Assign(targets=[Name(id='j', ctx=Store())], value=BinOp(left=Constant(value=1, kind=None), op=Add(), right=Constant(value=2, kind=None)), type_comment=None)

# CONTANTS
a2 = 1j                 # Assign(targets=[Name(id='a2', ctx=Store())], value=Constant(value=1j, kind=None), type_comment=None)
b = "2"                 # Assign(targets=[Name(id='b', ctx=Store())], value=Constant(value='2', kind=None), type_comment=None)"
b2 = """b"""            # Assign(targets=[Name(id='b2', ctx=Store())], value=Constant(value='b', kind=None), type_comment=None)
c = 3.0                 # Assign(targets=[Name(id='c', ctx=Store())], value=Constant(value=3.0, kind=None), type_comment=None)
f = ()                  # Assign(targets=[Name(id='f', ctx=Store())], value=Tuple(elts=[], ctx=Load()), type_comment=None)
h = True                # Assign(targets=[Name(id='h', ctx=Store())], value=Constant(value=True, kind=None), type_comment=None)
i = None                # Assign(targets=[Name(id='i', ctx=Store())], value=Constant(value=None, kind=None), type_comment=None)
k = l = 1                 # Assign(targets=[Name(id='a', ctx=Store()), Name(id='b', ctx=Store())], value=Constant(value=1, kind=None), type_comment=None)
m, n = 2, 3               # Assign(targets=[Tuple(elts=[Name(id='c', ctx=Store()), Name(id='d', ctx=Store())], ctx=Store())],
                                 # value=Tuple(elts=[Constant(value=2, kind=None), Constant(value=3, kind=None)], ctx=Load()), type_comment=None)

A = 1234
class CLASS:
    var = A + 100
    attr = A + 200


def foo():
    obj = CLASS()
    obj.var = 3
    print(CLASS.var)
    print(CLASS.attr)
    print(obj.var)
    global a
    print(a)
    a = 7
    print(a)
    return a
def paaohjelma():
    foo()
    print("AA")
    return None

