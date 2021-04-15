"""Class file. Contains StructureDetector class."""

import ast

import src.analysers.analysis_utils as a_utils
import src.config.config as cnf
import src.config.templates as templates

class StructureDetector(ast.NodeVisitor):
    """
    Class to detect used programming strcutures and commands. Detection
    is done by visiting nodes of Abstract Syntax Tree (AST). Uses
    Python's builtin 'ast' module.
    """

    def __init__(self):
        self.structures = []
        self._file_operations = {
            "read": "D05B001",
            "readline": "D05B002",
            "readlines": "D05B003",
            "write": "D05C001",
            "writelines": "D05C002",
            "close": "D05D001"
        }
        self._data_structures = {
            "list": "D06A001",
            "dict": "D06B001",
            "tuple": "D06C001",
            "set": "D06D001",
        }
        self._comparisons = {
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

  # Getters
    def get_structures(self):
        return self.structures[:]

  # General methods
    def clear_all(self):
        self.structures.clear()

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
            self.structures.append(
                templates.StructureTemplate("D03B001", func.lineno, func.args)
            )

  # Visits
   # Subscripts, i.e. indexes and slices
    def visit_Subscript(self, node, *args, **kwargs):
        """
        Currently ast.Slice and ast.Index does not have lineno,
        therefore subscript (which is always their parent_node) is used.
        """
        # NOTE if only counts are needed visit_Index and visit_Slice could be used.

        try:
            _slice = node.slice
            # Index, i.e. listing[0]
            if isinstance(_slice, ast.Index):
                self.structures.append(
                    templates.StructureTemplate("D10B001", node.lineno, _slice)
                )
            # Slice, i.e. listing[0:5:2]
            elif isinstance(_slice, ast.Slice):
                self.structures.append(
                    templates.StructureTemplate("D10B002", node.lineno, _slice)
                )
        except AttributeError:
            pass
        self.generic_visit(node)

   # Comparisons
    def visit_BoolOp(self, node, *args, **kwargs):
        # NOTE if only counts are needed visit_Or and visit_And could be used.
        try:
            _op = node.op
            # or
            #   creates a single Or regardless of values,
            #   1 or 2 -> ONE Or with 2 values
            #   1 or 2 or 3 -> ONE Or with 3 values
            if isinstance(_op, ast.Or):
                self.structures.append(
                    templates.StructureTemplate("D11A001", node.lineno, _op)
                )
            # and
            #   creates a single And regardless of values, similarly as Or above
            elif isinstance(_op, ast.And):
                self.structures.append(
                    templates.StructureTemplate("D11A002", node.lineno, _op)
                )
        except AttributeError:
            pass
        self.generic_visit(node)

    def visit_Compare(self, node, *args, **kwargs):
        # NOTE there is probably better way to do this selection from
        # dictionary but current version works.
        try:
            for _op in node.ops:
                for key, value in self._comparisons.items():
                    if isinstance(_op, key):
                        self.structures.append(
                            templates.StructureTemplate(
                                identifier=value,
                                lineno=node.lineno,
                                astree=_op
                            )
                        )
                        break
        except (AttributeError, KeyError):
            pass

        self.generic_visit(node)


   # Loops
    def visit_While(self, node, *args, **kwargs):
        # Found a while loop
        self.structures.append(
            templates.StructureTemplate("D02A001", node.lineno, node)
        )

        if node.orelse: # Empty or filled list
            self.structures.append(
                templates.StructureTemplate("D02A002", node.lineno, node.orelse)
            )
        self.generic_visit(node)

    def visit_For(self, node, *args, **kwargs):
        # Found a for loop
        self.structures.append(
            templates.StructureTemplate("D02B001", node.lineno, node)
        )

        if node.orelse: # Empty or filled list
            self.structures.append(
                templates.StructureTemplate("D02B002", node.lineno, node.orelse)
            )
        self.generic_visit(node)

    # Oneline fors
    def visit_ListComp(self, node, *args, **kwargs):
        # [x for x in listing]
        self.structures.append(
            templates.StructureTemplate("D02C001", node.lineno, node)
        )
        self.generic_visit(node)

    def visit_SetComp(self, node, *args, **kwargs):
        # {x for x in listing}
        self.structures.append(
            templates.StructureTemplate("D02C002", node.lineno, node)
        )
        self.generic_visit(node)

    def visit_GeneratorExp(self, node, *args, **kwargs):
        # (x for x in listing)
        self.structures.append(
            templates.StructureTemplate("D02C003", node.lineno, node)
        )
        self.generic_visit(node)

    def visit_DictComp(self, node, *args, **kwargs):
        # {x:x for x in listing}
        self.structures.append(
            templates.StructureTemplate("D02C004", node.lineno, node)
        )
        self.generic_visit(node)

   # Conditional statement
    def visit_If(self, node, *args, **kwargs):
        self.structures.append(
            templates.StructureTemplate("D01A001", node.lineno, node)
        )

        # NOTE before the ELIF detection also elif makes IF node, when
        # elif detection is done then this detection for if's can be
        # utilised


        # try:
        #     parent = a_utils.get_parent(node, ast.If)
        #     if not parent:
        #         # Found an if statement # NOTE does not detect if's inside if's this way
        #         self.structures.append(templates.StructureTemplate("D01A001", node.lineno))

        #     # IF has orelse, orelse has something else than IF OR IF is indended more than ELSE
        # except AttributeError:
        #     pass

        # TODO ELIF detection
        # elif creates both, else and if nodes in that order
        # self.structures.append(templates.StructureTemplate("D01A002", node.lineno))

        # ELSE detection
        try:
            # This is a first nodes inside else/elif branch
            _elem = node.orelse[0]
            if _elem.col_offset > node.col_offset:
                # what if _elem do not have col_offset, then check
                # if not isinstance(_elem, ast.If)?
                # FOUND ELSE
                self.structures.append(
                    templates.StructureTemplate("D01A003", node.lineno, node.orelse)
                )
        except (IndexError, AttributeError):
            pass
        self.generic_visit(node)

    # Oneline if == ternary operator
    def visit_IfExp(self, node, *args, **kwargs):
        # Ternary operator 1 if True else 2
        self.structures.append(
            templates.StructureTemplate("D01B001", node.lineno, node)
        )
        self.generic_visit(node)

   # Functions
    def visit_FunctionDef(self, node, *args, **kwargs):
        self.structures.append(
            templates.StructureTemplate("D03A001", node.lineno, node)
        )
        self._check_arguments(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node, *args, **kwargs):
        self.structures.append(
            templates.StructureTemplate("D03A002", node.lineno, node)
        )
        self._check_arguments(node)
        self.generic_visit(node)

    # Lambda == Anonymous function
    def visit_Lambda(self, node, *args, **kwargs):
        self.structures.append(
            templates.StructureTemplate("D03A003", node.lineno, node)
        )
        self._check_arguments(node)
        self.generic_visit(node)

    # Return
    def visit_Return(self, node, *args, **kwargs):
        # return statement
        self.structures.append(
            templates.StructureTemplate("D03C001", node.lineno, node)
        )

        try:
            # Check for return <anything but None>
            if node.value.value is not None:
                self.structures.append(
                    templates.StructureTemplate("D03C005", node.lineno, node)
                )

            # Else "return None" -ast-> value=Constant(value=None, kind=None)
            else:
                self.structures.append(
                    templates.StructureTemplate("D03C004", node.lineno, node)
                )

        # return without an value leads to an AttributeError.
        # "return" -ast-> Return(value=None)
        except AttributeError:
            pass
        self.generic_visit(node)

    def visit_Yield(self, node, *args, **kwargs):
        self.structures.append(
            templates.StructureTemplate("D03C002", node.lineno, node)
        )
        self.generic_visit(node)

    def visit_YieldFrom(self, node, *args, **kwargs):
        self.structures.append(
            templates.StructureTemplate("D03C003", node.lineno, node)
        )
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
                if (parent := a_utils.get_parent(node, ast.With)) is None:
                    self.structures.append(
                        templates.StructureTemplate(
                            identifier="D05A001",
                            lineno=node.lineno,
                            astree=node
                        )
                    )
                else:
                    self.structures.append(
                        templates.StructureTemplate(
                            identifier="D05A002",
                            lineno=node.lineno,
                            astree=parent
                        )
                    )

            if _id in self._data_structures.keys():
                self.structures.append(
                    templates.StructureTemplate(
                        identifier=self._data_structures.get(_id),
                        lineno=node.lineno,
                        astree=node
                    )
                )

        self.generic_visit(node)

    # Operations and close
    def visit_Attribute(self, node, *args, **kwargs):
        try:
            # node.attr should work even for changed a.b.c.read() attributes.
            if (operation := node.attr) in self._file_operations.keys():
                self.structures.append(
                    templates.StructureTemplate(
                        identifier=self._file_operations.get(operation),
                        lineno=node.lineno,
                        astree=node
                    )
                )
        except AttributeError:
            pass
        self.generic_visit(node)

   # Data structures (Call of list(), set() etc are inside visit_Call)
    # List
    def visit_List(self, node, *args, **kwargs):
        self.structures.append(
            templates.StructureTemplate(
                identifier=self._data_structures.get("list"),
                lineno=node.lineno,
                astree=node
            )
        )
        self.generic_visit(node)

    # Dictionary
    def visit_Dict(self, node, *args, **kwargs):
        self.structures.append(
            templates.StructureTemplate(
                identifier=self._data_structures.get("dict"),
                lineno=node.lineno,
                astree=node
            )
        )
        self.generic_visit(node)

    # Tuple
    def visit_Tuple(self, node, *args, **kwargs):
        self.structures.append(
            templates.StructureTemplate(
                identifier=self._data_structures.get("tuple"),
                lineno=node.lineno,
                astree=node
            )
        )
        self.generic_visit(node)

    # Set
    def visit_Set(self, node, *args, **kwargs):
        self.structures.append(
            templates.StructureTemplate(
                identifier=self._data_structures.get("set"),
                lineno=node.lineno,
                astree=node
            )
        )
        self.generic_visit(node)

   # Class
    def visit_ClassDef(self, node, *args, **kwargs):
        self.structures.append(
            templates.StructureTemplate("D07A001", node.lineno, node)
        )
        self.generic_visit(node)

    # TODO object

   # Imports
    def visit_Import(self, node, *args, **kwargs):
        self.structures.append(
            templates.StructureTemplate("D08B001", node.lineno, node)
        )
        self.generic_visit(node)

    def visit_ImportFrom(self, node, *args, **kwargs):
        if any(x.name == "*" for x in node.names):
            self.structures.append(
                templates.StructureTemplate("D08B003", node.lineno, node)
            )
        else:
            self.structures.append(
                templates.StructureTemplate("D08B002", node.lineno, node)
            )
        self.generic_visit(node)

   # Exception handling
    # Try
    def visit_Try(self, node, *args, **kwargs):
        self.structures.append(
            templates.StructureTemplate("D09A001", node.lineno, node)
        )

        # Else
        if node.orelse: # Empty or filled list
            self.structures.append(
                templates.StructureTemplate("D09A003", node.lineno, node.orelse)
            ) # Lineno is Try's line

        # Finally
        if node.finalbody: # Empty or filled list
            self.structures.append(
                templates.StructureTemplate("D09A004", node.lineno, node.finalbody)
            ) # Lineno is Try's line

        self.generic_visit(node)

    # Except
    def visit_ExceptHandler(self, node, *args, **kwargs):
        self.structures.append(
            templates.StructureTemplate("D09A002", node.lineno, node)
        )

        # Has exception type
        if node.type: # None/ast.Name object
            self.structures.append(
                templates.StructureTemplate("D09B001", node.lineno, node.type)
            )

        self.generic_visit(node)

