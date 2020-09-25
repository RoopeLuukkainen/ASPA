"""Class file. Contains ExamAnalyser class."""
__version__ = "0.3.1"
__author__ = "RL"

import ast


import utils_lib as utils

class ExamAnalyser(ast.NodeVisitor):
    """Class to do static analysis by visiting nodes of Abstract Syntax
    Tree. Uses 'ast' module and local 'utils_lib'.
    TODO: Make this basic command analyser, e.g. if, while, for etc.
    """
    def __init__(self, model):
        self.model = model
        self.required_commands = {"round", "print", "range", "int", "len", "float", "str"} # Examples


   # Grammar info
    # From : https://docs.python.org/3.7/library/ast.html#abstract-grammar

    #    stmt can be: FunctionDef, AsyncFunctionDef, ClassDef, Return, Delete,
    #                 Assign, AugAssign, AnnAssign, For, AsyncFor, While, If,
    #                 With, AsyncWith, Raise, Try, Assert, Import, ImportFrom,
    #                 Global, Nonlocal, Expr, Pass, Break, Continue

    #    expr can be: BoolOp, BinOp, UnaryOp, Lambda, IfExp, Dict, Set,
    #                 ListComp, SetComp, DictComp, GeneratorExp, Await, Yield,
    #                 YieldFrom, Compare, Call, Num, Str, FormattedValue,
    #                 JoinedStr, Bytes, NameConstant, Ellipsis, Constant,
    #                 Attribute, Subscript, Starred, Name, List, Tuple

   # Visits
    def visit_Call(self, node, *args, **kwargs):
        try:
            if(isinstance(node.func, ast.Name) 
                    and node.func.id in self.required_commands):
                self.model.add_msg("PT1", node.func.id, lineno=node.lineno)
        except AttributeError:
            pass
        self.generic_visit(node)

    def visit_While(self, node, *args, **kwargs):
        # Found a while loop
        try:
            # Check if there is no break in infinite loop
            if(utils.is_always_true(node.test)
                    and not utils.get_child_instance(node, (ast.Break, ast.Return))):
                self.model.add_msg("PT4-1", lineno=node.lineno)
        except AttributeError:
            pass
        self.generic_visit(node)

    # Rest are placeholders
    def visit_For(self, node, *args, **kwargs):
        # Found a for loop
        self.generic_visit(node)

    def visit_If(self, node, *args, **kwargs):
        # Found an if statement
        self.generic_visit(node)

    def visit_Subscript(self, node, *args, **kwargs):
        # Found a string slice, string[]
        # Subscript can be:
        #          | Subscript(expr value, slice slice, expr_context ctx)
        # Slice can be:
        #     slice = Slice(expr? lower, expr? upper, expr? step)
        #             | ExtSlice(slice* dims)
        #             | Index(expr value)a

        self.generic_visit(node)

    def visit_Slice(self, node, *args, **kwargs):
        self.generic_visit(node)

    def visit_Index(self, node, *args, **kwargs):
        self.generic_visit(node)