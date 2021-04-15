"""Class file. Contains StructureDetector class."""

import ast

import src.config.config as cnf
import src.analysers.analysis_utils as a_utils

class StructureDetector(ast.NodeVisitor):
    """
    Class to detect used programming strcutures and commands. Detection
    is done by visiting nodes of Abstract Syntax Tree (AST). Uses
    Python's builtin 'ast' module.
    """

    def __init__(self, model):
        self.model = model
        self.file_operations = {
            "read": "D05B001",
            "readline": "D05B002",
            "readlines": "D05B003",
            "write": "D05C001",
            "writelines": "D05C002",
            "close": "D05D001"
        }
        self.data_structures = {
            "list": "D06A001",
            "dict": "D06B001",
            "tuple": "D06C001",
            "set": "D06D001",
        }
        self.comparisons = {
            ast.Eq: "D11B001",
            ast.NotEq: "D11B002",
            ast.Lt: "D11B003",
            ast.Gt: "D11B004",
            ast.LtE: "D11B005",
            ast.GtE: "D11B006",
            ast.Is: "D11B007",
            ast.IsNot: "D11B008",
            ast.In: "D11B009",
            ast.NotIn: "D11B010"
        }

  # General methods
    def _has_arguments(self, arguments):
        """
        Method to check if function definition has any arguments.

        Return: True/False

        Note: One could argue these are actually parameters not
        arguments.
        """

        return any([
            arguments.posonlyargs,
            arguments.args,         # list of positional arguments before *args
            arguments.kwonlyargs,   # list of keyword arguments after *args
            arguments.vararg,       # *args, None/args
            arguments.kwarg        # **kwargs, None/kwargs
        ])

    def _check_arguments(self, func): # NOTE This should not be in STRUCTURE check?
        if self._has_arguments(func.args):
            self.model.store_structure("D03B001", lineno=func.lineno)

  # Visits
   # Subscripts, i.e. indexes and slices
    def visit_Subscript(self, node, *args, **kwargs):
        """
        Currently ast.Slice and ast.Index does not have lineno,
        therefore subscript (which is always their parent_node) is used.
        """
        # NOTE if only counts are needed visit_Index and visit_Slice could be used.

        try:
            # Index, i.e. listing[0]
            if isinstance(node.slice, ast.Index):
                self.model.store_structure("D10B001", lineno=node.lineno)
            # Slice, i.e. listing[0:5:2]
            elif isinstance(node.slice, ast.Slice):
                self.model.store_structure("D10B002", lineno=node.lineno)
        except AttributeError:
            pass
        self.generic_visit(node)

   # Comparisons
    def visit_BoolOp(self, node, *args, **kwargs):
        # NOTE if only counts are needed visit_Or and visit_And could be used.
        try:
            # or
            #   creates a single Or regardless of values,
            #   1 or 2 -> ONE Or with 2 values
            #   1 or 2 or 3 -> ONE Or with 3 values
            if isinstance(node.op, ast.Or):
                self.model.store_structure("D11A001", lineno=node.lineno)
            # and
            #   creates a single And regardless of values, similarly as Or above
            elif isinstance(node.op, ast.And):
                self.model.store_structure("D11A002", lineno=node.lineno)
        except AttributeError:
            pass
        self.generic_visit(node)

    def visit_Compare(self, node, *args, **kwargs):
        # NOTE there is probably better way to do this selection from
        # dictionary but current version works.
        try:
            for _op in node.ops:
                for key, value in self.comparisons.items():
                    if isinstance(_op, key):
                        self.model.store_structure(value, lineno=node.lineno)
                        break
        except (AttributeError, KeyError) as e:
            print(e)

        self.generic_visit(node)


   # Loops
    def visit_While(self, node, *args, **kwargs):
        # Found a while loop
        self.model.store_structure("D02A001", lineno=node.lineno)

        if node.orelse: # Empty or filled list
            self.model.store_structure("D02A002", lineno=node.lineno)
        self.generic_visit(node)

    def visit_For(self, node, *args, **kwargs):
        # Found a for loop
        self.model.store_structure("D02B001", lineno=node.lineno)

        if node.orelse: # Empty or filled list
            self.model.store_structure("D02B002", lineno=node.lineno)
        self.generic_visit(node)

    # Oneline fors
    def visit_ListComp(self, node, *args, **kwargs):
        # [x for x in listing]
        self.model.store_structure("D02C001", lineno=node.lineno)
        self.generic_visit(node)

    def visit_SetComp(self, node, *args, **kwargs):
        # {x for x in listing}
        self.model.store_structure("D02C002", lineno=node.lineno)
        self.generic_visit(node)

    def visit_GeneratorExp(self, node, *args, **kwargs):
        # (x for x in listing)
        self.model.store_structure("D02C003", lineno=node.lineno)
        self.generic_visit(node)

    def visit_DictComp(self, node, *args, **kwargs):
        # {x:x for x in listing}
        self.model.store_structure("D02C004", lineno=node.lineno)
        self.generic_visit(node)

   # Conditional statement
    def visit_If(self, node, *args, **kwargs):
        self.model.store_structure("D01A001", lineno=node.lineno)

        # NOTE before the ELIF detection also elif makes IF node, when
        # elif detection is done then this detection for if's can be
        # utilised


        # try:
        #     parent = a_utils.get_parent(node, ast.If)
        #     if not parent:
        #         # Found an if statement # NOTE does not detect if's inside if's this way
        #         self.model.store_structure("D01A001", lineno=node.lineno)

        #     # IF has orelse, orelse has something else than IF OR IF is indended more than ELSE
        # except AttributeError:
        #     pass

        # TODO ELIF detection
        # elif creates both, else and if nodes in that order
        # self.model.store_structure("D01A002", lineno=node.lineno)

        # ELSE detection
        try:
            # This is a first nodes inside else/elif branch
            _elem = node.orelse[0]
            if _elem.col_offset > node.col_offset:
                # what if _elem do not have col_offset, then check
                # if not isinstance(_elem, ast.If)?
                # FOUND ELSE
                self.model.store_structure("D01A003", lineno=node.lineno)
        except (IndexError, AttributeError):
            pass
        self.generic_visit(node)

    # Oneline if == ternary operator
    def visit_IfExp(self, node, *args, **kwargs):
        # Ternary operator 1 if True else 2
        self.model.store_structure("D01B001", lineno=node.lineno)
        self.generic_visit(node)

   # Functions
    def visit_FunctionDef(self, node, *args, **kwargs):
        self.model.store_structure("D03A001", lineno=node.lineno)
        self._check_arguments(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node, *args, **kwargs):
        self.model.store_structure("D03A002", lineno=node.lineno)
        self._check_arguments(node)
        self.generic_visit(node)

    # Lambda == Anonymous function
    def visit_Lambda(self, node, *args, **kwargs):
        self.model.store_structure("D03A003", lineno=node.lineno)
        self._check_arguments(node)
        self.generic_visit(node)

    # Return
    def visit_Return(self, node, *args, **kwargs):
        # return statement
        self.model.store_structure("D03C001", lineno=node.lineno)

        try:
            # Check for return <anything but None>
            if node.value.value is not None:
                self.model.store_structure("D03C005", lineno=node.lineno)

            # Else "return None" -ast-> value=Constant(value=None, kind=None)
            else:
                self.model.store_structure("D03C004", lineno=node.lineno)

        # return without an value leads to an AttributeError.
        # "return" -ast-> Return(value=None)
        except AttributeError:
            pass
        self.generic_visit(node)

    def visit_Yield(self, node, *args, **kwargs):
        self.model.store_structure("D03C002", lineno=node.lineno)
        self.generic_visit(node)

    def visit_YieldFrom(self, node, *args, **kwargs):
        self.model.store_structure("D03C003", lineno=node.lineno)
        self.generic_visit(node)

   # File handling
    # Open
    def visit_Call(self, node, *args, **kwargs):
        try:
            _id = node.func.id
        except AttributeError:
            pass
        else:
            if _id == "open":
                if a_utils.get_parent(node, ast.With) is None:
                    self.model.store_structure("D05A001", lineno=node.lineno)
                else:
                    self.model.store_structure("D05A002", lineno=node.lineno)

            if _id in self.data_structures.keys():
                self.model.store_structure(
                    self.data_structures.get(_id),
                    lineno=node.lineno
                )

        self.generic_visit(node)

    # Operations and close
    def visit_Attribute(self, node, *args, **kwargs):
        try:
            # node.attr should work even for changed a.b.c.read() attributes.
            if (operation := node.attr) in self.file_operations.keys():
                self.model.store_structure(
                    self.file_operations.get(operation),
                    lineno=node.lineno
                )
        except AttributeError:
            pass
        self.generic_visit(node)

   # Data structures (Call of list(), set() etc are inside visit_Call)
    # List
    def visit_List(self, node, *args, **kwargs):
        self.model.store_structure(
            self.data_structures.get("list"),
            lineno=node.lineno
        )
        self.generic_visit(node)

    # Dictionary
    def visit_Dict(self, node, *args, **kwargs):
        self.model.store_structure(
            self.data_structures.get("dict"),
            lineno=node.lineno
        )
        self.generic_visit(node)

    # Tuple
    def visit_Tuple(self, node, *args, **kwargs):
        self.model.store_structure(
            self.data_structures.get("tuple"),
            lineno=node.lineno
        )
        self.generic_visit(node)

    # Set
    def visit_Set(self, node, *args, **kwargs):
        self.model.store_structure(
            self.data_structures.get("set"),
            lineno=node.lineno
        )
        self.generic_visit(node)

   # Class
    def visit_ClassDef(self, node, *args, **kwargs):
        self.model.store_structure("D07A001", lineno=node.lineno)
        self.generic_visit(node)

    # TODO object

   # Imports
    def visit_Import(self, node, *args, **kwargs):
        self.model.store_structure("D08B001", lineno=node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node, *args, **kwargs):
        if any(x.name == "*" for x in node.names):
            self.model.store_structure("D08B003", lineno=node.lineno)
        else:
            self.model.store_structure("D08B002", lineno=node.lineno)
        self.generic_visit(node)

   # Exception handling
    # Try
    def visit_Try(self, node, *args, **kwargs):
        self.model.store_structure("D09A001", lineno=node.lineno)

        # Else
        if node.orelse: # Empty or filled list
            self.model.store_structure("D09A003", lineno=node.lineno) # Lineno is Try's line

        # Finally
        if node.finalbody: # Empty or filled list
            self.model.store_structure("D09A004", lineno=node.lineno) # Lineno is Try's line

        self.generic_visit(node)

    # Except
    def visit_ExceptHandler(self, node, *args, **kwargs):
        self.model.store_structure("D09A002", lineno=node.lineno)

        # Has exception type
        if node.type: # None/ast.Name object
            self.model.store_structure("D09B001", lineno=node.lineno)

        self.generic_visit(node)

