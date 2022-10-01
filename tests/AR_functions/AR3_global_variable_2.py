"""2nd test file for AR3 check and AR3-3.
AR3 check detects global variables. Global constants are allowed.
"""

# GLOBAL VARIABLES
# value to these are assigned again/modified later, therefore they are global
global_a = 1

global_list = []
global_list2 = []
global_list3 = list()
global_list4 = [1, 2, 3]
global_list5 = [1, 2, 3]

global_dict = {}
global_dict2 = dict()
global_dict3 = {}
global_dict4 = {"1": 2, "2": 3}
global_dict5 = {"3": 4, "4": 5}
global_dict6 = {"key": "value1"}

# CONTANTS
const_func_call = foo()
const_a2 = 1j                 # Assign(targets=[Name(id='a2', ctx=Store())], value=Constant(value=1j, kind=None), type_comment=None)
const_b = "2"                 # Assign(targets=[Name(id='b', ctx=Store())], value=Constant(value='2', kind=None), type_comment=None)"
const_b2 = """b"""            # Assign(targets=[Name(id='b2', ctx=Store())], value=Constant(value='b', kind=None), type_comment=None)
const_c = 3.0                 # Assign(targets=[Name(id='c', ctx=Store())], value=Constant(value=3.0, kind=None), type_comment=None)
const_h = True                # Assign(targets=[Name(id='h', ctx=Store())], value=Constant(value=True, kind=None), type_comment=None)
const_i = None                # Assign(targets=[Name(id='i', ctx=Store())], value=Constant(value=None, kind=None), type_comment=None)
const_k = const_l = 1                 # Assign(targets=[Name(id='a', ctx=Store()), Name(id='b', ctx=Store())], value=Constant(value=1, kind=None), type_comment=None)
const_m, const_n = 2, 3               # Assign(targets=[Tuple(elts=[Name(id='c', ctx=Store()), Name(id='d', ctx=Store())], ctx=Store())],
                                 # value=Tuple(elts=[Constant(value=2, kind=None), Constant(value=3, kind=None)], ctx=Load()), type_comment=None)
const_binop = 1 + 2               # Assign(targets=[Name(id='j', ctx=Store())], value=BinOp(left=Constant(value=1, kind=None), op=Add(), right=Constant(value=2, kind=None)), type_comment=None)

const_list = [1, 2, 3]                  # Assign(targets=[Name(id='d', ctx=Store())], value=List(elts=[], ctx=Load()), type_comment=None)
const_dict = {"1": 2}                  # Assign(targets=[Name(id='e', ctx=Store())], value=Dict(keys=[], values=[]), type_comment=None)
const_set = set()               # Assign(targets=[Name(id='g', ctx=Store())], value=Call(func=Name(id='set', ctx=Load()), args=[], keywords=[]), type_comment=None)
const_list2 = list()             # Assign(targets=[Name(id='d2', ctx=Store())], value=Call(func=Name(id='list', ctx=Load()), args=[], keywords=[]), type_comment=None)
const_dict2 = dict()             # Assign(targets=[Name(id='e2', ctx=Store())], value=Call(func=Name(id='dict', ctx=Load()), args=[], keywords=[]), type_comment=None)
const_tuple = (4, 5, 6)                  # Assign(targets=[Name(id='f', ctx=Store())], value=Tuple(elts=[], ctx=Load()), type_comment=None)
const_tuple2 = tuple()            # Assign(targets=[Name(id='g2', ctx=Store())], value=Call(func=Name(id='tuple', ctx=Load()), args=[], keywords=[]), type_comment=None)


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
    # Global modifications
    global global_a
    global global_b
    print(global_a)
    global_a = 7
    print(global_a)

    global_list.append(1)
    global_list2.insert(0, 1)
    global_list3.extend([2, 3])
    global_list4.pop()
    global_list5.sort()

    global_dict.update(const_dict)
    global_dict2["key"] = "value"
    global_dict3.clear()
    global_dict4.pop()
    global_dict5.popitem()
    global_dict6.setdefault("key2", "value")

    return global_a

def paaohjelma():
    foo()
    print("AA")
    return None

