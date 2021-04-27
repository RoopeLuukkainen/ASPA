# pylint: skip-file
# ******************************************************************** #
# # Case 1
if True:
    pass
elif False:
    pass

# # Case 2 creates identical tree excluding col_offset
if True:
    pass
else:
    if False:
        pass

# Case 1 with all details
If(
    test=Constant(value=True, kind=None, lineno=1, col_offset=3, end_lineno=1, end_col_offset=7),
    body=[Pass(lineno=2, col_offset=4, end_lineno=2, end_col_offset=8)],
    orelse=[
        If(
            test=Constant(value=False, kind=None, lineno=3, col_offset=5, end_lineno=3, end_col_offset=10),
            body=[Pass(lineno=4, col_offset=4, end_lineno=4, end_col_offset=8)],
            orelse=[],
            lineno=3, col_offset=0, end_lineno=4, end_col_offset=8
        )
    ],
    lineno=1, col_offset=0, end_lineno=4, end_col_offset=8
)

# Case 2 with all details
If(
    test=Constant(value=True, kind=None, lineno=7, col_offset=3, end_lineno=7, end_col_offset=7),
    body=[Pass(lineno=8, col_offset=4, end_lineno=8, end_col_offset=8)],
    orelse=[
        If(
            test=Constant(value=False, kind=None, lineno=10, col_offset=7, end_lineno=10, end_col_offset=12),
            body=[Pass(lineno=11, col_offset=8, end_lineno=11, end_col_offset=12)],
            orelse=[],
            lineno=10, col_offset=4, end_lineno=11, end_col_offset=12
        )
    ],
    lineno=7, col_offset=0, end_lineno=11, end_col_offset=12
)

# ******************************************************************** #
# if-elif-else (having pass same or different line does nothing but
# change lineno and col_offsets)
if True: pass
elif False: pass
elif True: pass
else: a = 1
#
If(
    test=Constant(value=True, kind=None),
    body=[Pass()],
    orelse=[
        If(
            test=Constant(value=False, kind=None),
            body=[Pass()],
            orelse=[
                If(
                    test=Constant(value=True, kind=None),
                    body=[Pass()],
                    orelse=[
                        Assign(
                            targets=[Name(id='a', ctx=Store())],
                            value=Constant(value=1, kind=None), type_comment=None
                        )
                    ]
                )
            ]
        )
    ]
)

# ******************************************************************** #
# Ternary operation == oneline if
1 if True else 2
#
IfExp(
    test=Constant(value=True, kind=None),
    body=Constant(value=1, kind=None),
    orelse=Constant(value=2, kind=None)
)

# ******************************************************************** #
# attribute close (call) without parenthesis
with open("b.txt", "w") as f:
    pass
#
With(
    items=[
        withitem(
            context_expr=Call(
                func=Name(id='open', ctx=Load()),
                args=[Constant(value='b.txt', kind=None), Constant(value='w', kind=None)],
                keywords=[]
            ),
            optional_vars=Name(id='f', ctx=Store())
        )
    ],
    body=[Pass()],
    type_comment=None
)

# ******************************************************************** #
# attribute close (call) without parenthesis
t.fhandle.close
#
Expr(
    value=Attribute(
        value=Attribute(
            value=Name(
                id='t', ctx=Load()
            ),
            attr='fhandle', ctx=Load()
        ),
        attr='close', ctx=Load()
    )
)

# ******************************************************************** #
# attribute close with parenthesis
t.fhandle.close()
#
Expr(
    value=Call(
        func=Attribute(
            value=Attribute(
                value=Name(
                    id='t', ctx=Load()
                ),
                attr='fhandle', ctx=Load()
            ),
            attr='close', ctx=Load()
        ),
        args=[], keywords=[]
    )
)

# ******************************************************************** #
# FunctionDef
def TR2_2(thing):
    return None
#
FunctionDef(
    name='TR2_2',
    args=arguments(
        posonlyargs=[],
        args=[ # Positional parameters i.e. ones before *arg and **kwarg
            arg(arg='thing', annotation=None, type_comment=None)
        ],
        vararg=None, # Has *arg, value will be name after *
        kwonlyargs=[], # parameters between *arg and **kwarg
        kw_defaults=[], # default values for kwonlyargs
        kwarg=None, # Has **kwarg, value will be name after **
        defaults=[] # default values for args (if this is 2 long then values are for two last args)
    ),
    body=[
        Return(value=Constant(value=None, kind=None))
    ],
    decorator_list=[],
    returns=None,
    type_comment=None
)

# ******************************************************************** #
lambda x: print(x)
#
Lambda(
    args=arguments(
        posonlyargs=[],
        args=[arg(arg='x', annotation=None, type_comment=None)],
        vararg=None,
        kwonlyargs=[],
        kw_defaults=[],
        kwarg=None,
        defaults=[]
    ),
    body=Call(
        func=Name(id='print', ctx=Load()), args=[Name(id='x', ctx=Load())], keywords=[]
    )
)

# ******************************************************************** #
# Class def
class FOO():
    attr = 1
#
ClassDef(
    name='FOO',
    bases=[],
    keywords=[],
    body=[
        Assign(
            targets=[
                Name(id='attr', ctx=Store())
            ],
            value=Constant(value=1, kind=None),
            type_comment=None
        )
    ],
    decorator_list=[]
)

# ******************************************************************** #
bar = "foo"
#
Assign(
    targets=[Name(id='bar', ctx=Store())],
    value=Constant(value='foo', kind=None),
    type_comment=None
)

# ******************************************************************** #
bar[1:5:2]
#
Subscript(
    value=Name(id='bar', ctx=Load()),
    slice=Slice(
        lower=Constant(value=1, kind=None),
        upper=Constant(value=5, kind=None),
        step=Constant(value=2, kind=None)
    ),
    ctx=Load()
)

# ******************************************************************** #
bar[0]
#
Subscript(
    value=Name(id='bar', ctx=Load()),
    slice=Index( # NOTE there does not seem to be Index in Python 3.9
        value=Constant(value=0, kind=None)
    ),
    ctx=Load()
)

# ******************************************************************** #
bar = FOO
#
Assign(
    targets=[
        Name(id='bar', ctx=Store())
    ],
    value=Name(id='FOO', ctx=Load()),
    type_comment=None
)

# ******************************************************************** #
foo = FOO()
#
Assign(
    targets=[
        Name(id='foo', ctx=Store())
    ],
    value=Call(
        func=Name(id='FOO', ctx=Load()),
        args=[],
        keywords=[]
    ), type_comment=None
)

# ******************************************************************** #
foo.attr = 3
#
Assign(
    targets=[
        Attribute(value=Name(id='foo', ctx=Load()), attr='attr', ctx=Store())
    ],
    value=Constant(value=3, kind=None),
    type_comment=None
)

# ******************************************************************** #
thing.a.b.c = FOO
#
Assign(
    targets=[
        Attribute(
            value=Attribute(
                value=Attribute(
                    value=Attribute(
                        value=Name(id='thing', ctx=Load()),
                        attr='a', ctx=Load()
                    ),
                    attr='b', ctx=Load()
                ),
                attr='c', ctx=Load()
            ),
            attr='d', ctx=Store()
        )
    ],
    value=Name(id='FOO', ctx=Load()),
    type_comment=None
)
# ******************************************************************** #
return [1]
#
Return(
    value=List(
        elts=[Constant(value=1, kind=None)], ctx=Load()
    )
)
# ******************************************************************** #
return (1,)
#
Return(
    value=Tuple(
        elts=[Constant(value=1, kind=None)], ctx=Load()
    )
)
# ******************************************************************** #
return 1, 2
#
Return(
    value=Tuple(
        elts=[
            Constant(value=1, kind=None),
            Constant(value=2, kind=None)
        ], ctx=Load()
    )
)
# ******************************************************************** #
return {1}
#
Return(
    value=Set(
        elts=[Constant(value=1, kind=None)]
    )
)
# ******************************************************************** #
return {1:2}
#
Return(
    value=Dict(
        keys=[Constant(value=1, kind=None)],
        values=[Constant(value=2, kind=None)]
    )
)
# ******************************************************************** #
return a
#
Return(
    value=Name(id='a', ctx=Load())
)
# ******************************************************************** #
return True
#
Return(
    value=Constant(value=True, kind=None)
)
# ******************************************************************** #
return None
#
Return(
    value=Constant(value=None, kind=None)
)
# ******************************************************************** #
return
#
Return(value=None)
# ******************************************************************** #
[i for i in (1, 2)] # Similar tree with:
                    # SetComp(expr elt, comprehension* generators)
                    # GeneratorExp(expr elt, comprehension* generators) # This is done like (i for i in list)
                    # DictComp(expr key, expr value, comprehension* generators)
#
ListComp(
    elt=Name(id='i', ctx=Load()),
    generators=[
        comprehension(
            target=Name(id='i', ctx=Store()),
            iter=Tuple(elts=[Constant(value=1, kind=None), Constant(value=2, kind=None)], ctx=Load()),
            ifs=[],
            is_async=0
        )
    ]
)

# ******************************************************************** #
for i in a:
    pass
else:
    pass
#
For(
    target=Name(id='i', ctx=Store()),
    iter=Name(id='a', ctx=Load()),
    body=[Pass()],
    orelse=[Pass()],
    type_comment=None
)

# ******************************************************************** #
while True:
    break
else:
    pass
#
While(
    test=Constant(value=True, kind=None),
    body=[Break()],
    orelse=[Pass()]
)

# ******************************************************************** #
import math
#
Import(names=[alias(name='math', asname=None)])

# ******************************************************************** #
from random import randint
#
ImportFrom(module='random', names=[alias(name='randint', asname=None)], level=0)

# ******************************************************************** #
from datetime import *
#
ImportFrom(module='datetime', names=[alias(name='*', asname=None)], level=0)

# ******************************************************************** #
[]
{}
(1,)
{1}
#
List(elts=[], ctx=Load())
Dict(keys=[], values=[])
Tuple(elts=[Constant(value=1, kind=None)], ctx=Load())
Set(elts=[Constant(value=1, kind=None)])

# ******************************************************************** #
list()
dict()
tuple()
set()
#
Call(func=Name(id='list', ctx=Load()), args=[], keywords=[])
Call(func=Name(id='dict', ctx=Load()), args=[], keywords=[])
Call(func=Name(id='tuple', ctx=Load()), args=[], keywords=[])
Call(func=Name(id='set', ctx=Load()), args=[], keywords=[])

# ******************************************************************** #
try:
    pass
except Exception as e:
    pass
else: pass
finally: pass
#
Try(
    body=[Pass()],
    handlers=[
        ExceptHandler(
            type=Name(id='Exception', ctx=Load()),
            name="e",
            body=[Pass()]
        )
    ],
    orelse=[Pass()],
    finalbody=[Pass()]
)
# ******************************************************************** #
try: pass
except: pass
finally: pass
#
Try(
    body=[Pass()],
    handlers=[
        ExceptHandler(type=None, name=None, body=[Pass()])
    ],
    orelse=[],
    finalbody=[Pass()]
)

# ******************************************************************** #
1 and 2
#
BoolOp(
    op=And(),
    values=[
        Constant(value=1, kind=None),
        Constant(value=2, kind=None)
    ]
)

# ******************************************************************** #
1 or 2 or 3
#
BoolOp(
    op=Or(),
    values=[
        Constant(value=1, kind=None),
        Constant(value=2, kind=None),
        Constant(value=3, kind=None)
    ]
)

# ******************************************************************** #
1 == 2
1 != 2
1 < 2
1 > 2
1 <= 2
1 >= 2
#
Compare(
    left=Constant(value=1, kind=None),
    ops=[Eq()],
    comparators=[Constant(value=2, kind=None)]
)
Compare(
    left=Constant(value=1, kind=None),
    ops=[NotEq()],
    comparators=[Constant(value=2, kind=None)]
)
Compare(
    left=Constant(value=1, kind=None),
    ops=[Lt()],
    comparators=[Constant(value=2, kind=None)]
)
Compare(
    left=Constant(value=1, kind=None),
    ops=[Gt()],
    comparators=[Constant(value=2, kind=None)]
)
Compare(
    left=Constant(value=1, kind=None),
    ops=[LtE()],
    comparators=[Constant(value=2, kind=None)]
)
Compare(
    left=Constant(value=1, kind=None),
    ops=[GtE()],
    comparators=[Constant(value=2, kind=None)]
)

# ******************************************************************** #
1 is 2
1 is not 2
1 in [2]
1 not in [2]
#
Compare(
    left=Constant(value=1, kind=None),
    ops=[Is()],
    comparators=[Constant(value=2, kind=None)]
)
Compare(
    left=Constant(value=1, kind=None),
    ops=[IsNot()],
    comparators=[Constant(value=2, kind=None)]
)
Compare(
    left=Constant(value=1, kind=None),
    ops=[In()],
    comparators=[List(elts=[Constant(value=2, kind=None)], ctx=Load())]
)
Compare(
    left=Constant(value=1, kind=None),
    ops=[NotIn()],
    comparators=[List(elts=[Constant(value=2, kind=None)], ctx=Load())]
)

# ******************************************************************** #
# LIST and OBJECT
# ******************************************************************** #
example_list = [param.object.value]
#
Assign(
    targets=[Name(id='example_list', ctx=Store())],
    value=List(
        elts=[
            Attribute(
                value=Attribute(
                    value=Name(id='param', ctx=Load()),
                    attr='object', ctx=Load()
                ),
                attr='value', ctx=Load()
            )
        ], ctx=Load()
    ), type_comment=None
)

# ******************************************************************** #
example_list.append(obj.value)
#
Expr(
    value=Call(
        func=Attribute(
            value=Name(id='example_list', ctx=Load()),
            attr='append', ctx=Load()
        ),
        args=[
            Attribute(
                value=Name(id='obj', ctx=Load()),
                attr='value', ctx=Load()
            )
        ],
        keywords=[]
    )
)

# ******************************************************************** #
example_list.extend([obj.value, obj.value])
#
Expr(
    value=Call(
        func=Attribute(
            value=Name(id='example_list', ctx=Load()),
            attr='extend', ctx=Load()
        ),
        args=[
            List(
                elts=[
                    Attribute(
                        value=Name(id='obj', ctx=Load()),
                        attr='value', ctx=Load()
                    ),
                    Attribute(
                        value=Name(id='obj', ctx=Load()),
                        attr='value', ctx=Load()
                    )
                ], ctx=Load()
            )
        ],
        keywords=[]
    )
)

# ******************************************************************** #
example_list.extend(list(obj.value, obj.value))
#
Expr(
    value=Call(
        func=Attribute(
            value=Name(id='example_list', ctx=Load()),
            attr='extend', ctx=Load()
        ),
        args=[
            Call(
                func=Name(id='list', ctx=Load()),
                args=[
                    Attribute(
                        value=Name(id='obj', ctx=Load()),
                        attr='value', ctx=Load()
                    ),
                    Attribute(
                        value=Name(id='obj', ctx=Load()),
                        attr='value', ctx=Load()
                    )
                ],
                keywords=[]
            )
        ],
        keywords=[]
    )
)

# ******************************************************************** #
example_list.insert(0, obj.value)
#
Expr(
    value=Call(
        func=Attribute(
            value=Name(id='example_list', ctx=Load()),
            attr='insert', ctx=Load()
        ),
        args=[
            Constant(value=0, kind=None),
            Attribute(
                value=Name(id='obj', ctx=Load()),
                attr='value', ctx=Load()
            )
        ],
        keywords=[]
    )
)

# ******************************************************************** #
example_list += [obj.value]
#
AugAssign(
    target=Name(id='example_list', ctx=Store()),
    op=Add(),
    value=List(
        elts=[
            Attribute(
                value=Name(id='obj', ctx=Load()),
                attr='value', ctx=Load()
            )
        ], ctx=Load()
    )
)

# ******************************************************************** #
example_list = example_list + [obj.value]
#
Assign(
    targets=[Name(id='example_list', ctx=Store())],
    value=BinOp(
        left=Name(id='example_list', ctx=Load()),
        op=Add(),
        right=List(
            elts=[
                Attribute(
                    value=Name(id='obj', ctx=Load()),
                    attr='value', ctx=Load()
                )
            ], ctx=Load()
        )
    ), type_comment=None
)

# ******************************************************************** #
example_list += list({obj.value, param.object.value})
#
AugAssign(
    target=Name(id='example_list', ctx=Store()),
    op=Add(),
    value=Call(
        func=Name(id='list', ctx=Load()),
        args=[
            Set(
                elts=[
                    Attribute(
                        value=Name(id='obj', ctx=Load()),
                        attr='value', ctx=Load()
                    ),
                    Attribute(
                        value=Attribute(
                            value=Name(id='param', ctx=Load()),
                            attr='object', ctx=Load()
                        ),
                        attr='value', ctx=Load()
                    )
                ]
            )
        ],
        keywords=[]
    )
)

# ******************************************************************** #
