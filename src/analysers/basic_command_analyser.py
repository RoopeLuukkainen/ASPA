"""Class file. Contains BasicsAnalyser class."""

import ast
# import keyword

import src.config.config as cnf
import src.analysers.analysis_utils as a_utils
import src.utils_lib as utils

class BasicsAnalyser(ast.NodeVisitor):
    """
    Class to do static analysis by visiting nodes of Abstract Syntax
    Tree. Uses 'ast' module and local 'utils_lib'.
    """

    def __init__(self, model):
        self.model = model
        self.searched_commands = cnf.SEARCHED_COMMANDS
        self.valid_naming = utils.get_compiled_regex("valid_naming")

    def check_valid_name(self, node, name, *args, **kwargs):
        """
        Method to validate given name, e.g. variable name or function
        name. Valid names must match following regex pattern
        ^[a-zA-Z_][a-zA-Z0-9_]*$ i.e. they can have only letters from
        a to z (both upper and lowercase), underscore or numbers, and
        may not start with a number.
        """

        try:
            self.model.add_msg(
                "PT2",
                name,
                lineno=node.lineno,
                # Must be re.match, not re.search
                status=(self.valid_naming.match(name) is not None)
            )

        # TypeError Can oocur when name is not string or bytes-like object,
        # e.g. when importing module without as-keyword (as)name will be None.
        except TypeError:
            pass

        # NOTE: using keyword actually creates syntax error to ast.parse
        # therefore this test is no in use
        # if keyword.iskeyword(name):
        #     self.model.add_msg("PT2-1", name, lineno=node.lineno)
        return None

    def iterate_arg_names(self, node, *args, **kwargs):
        """Method to collect all argument names from a given function node.
        This include posonly, 'normal', keyword and prefix arguments (*arg and
        **kwargs).
        Return list of tuples in format [(node, name), (node, name)]
        """
        # TODO move this to preanalyser?

        arg_names = list()
        # Positional and keyword arguments, i.e. all but *args and **kwargs
        try:
            for arg_type in [node.args.posonlyargs,
                             node.args.args,
                             node.args.kwonlyargs]:
                for i in arg_type:
                    arg_names.append((node, i.arg))
        except AttributeError:
            pass

        # Prefix arguments, i.e. *args and **kwargs
        try:
            for prefix_arg in [node.args.vararg, node.args.kwarg]:
                if prefix_arg:
                    arg_names.append((node, prefix_arg.arg))
        except AttributeError:
            pass
        return arg_names

    def _check_function_naming(self, node, *args, **kwargs):
        """Wrapper to check function names."""

        names = self.iterate_arg_names(node)
        try:
            names.append((node, node.name)) # add function name among parameter names
        except AttributeError:
            pass

        for i in names:
            try:
                self.check_valid_name(i[0], i[1]) # i is tuple (node, name)
            except IndexError:
                pass
        return None

    def _check_import_naming(self, node, *args, **kwargs):
        """Wrapper to check import names."""

        try:
            for i in node.names:
                self.check_valid_name(node, i.asname)
        except AttributeError:
            pass

    def _check_unreachable_code(self, node, command_name, *args, **kwargs):
        """
        Method to check if there are lines after the given command. This
        is currently used to check unreachable code after commands:
        return, break, continue, raise, sys.exit, exit, quit
        """

        try:
            self.model.add_msg(
                "PT5",
                command_name,
                lineno=node.lineno,
                status=(node.next_sibling is None)
            )
        except AttributeError:
            pass

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
            call_name = node.func.id  # Name of the called function or class
            attribute_name = None  # Library, class or object name which is referred

            # Command called check
            if (isinstance(node.func, ast.Name)
                    and call_name in self.searched_commands
            ):
                self.model.add_msg("PT1", call_name, lineno=node.lineno)

            # Unreachable code check
            if call_name == "exit":
                self._check_unreachable_code(
                    a_utils.get_parent(node, ast.Expr),
                    "exit"
                )
            elif call_name == "quit":
                self._check_unreachable_code(
                    a_utils.get_parent(node, ast.Expr),
                    "quit"
                )
        except AttributeError:
            try:
                call_name = node.func.attr  # Name of the called function or class
                attribute_name = node.func.value.id  # Library, class or object name which is referred

                # Unreachable code check
                if attribute_name == "sys" and call_name == "exit":
                    self._check_unreachable_code(
                        a_utils.get_parent(node, ast.Expr),
                        "sys.exit"
                    )

            except AttributeError:
                pass
        self.generic_visit(node)

    def visit_While(self, node, *args, **kwargs):
        try:
            # Check if there is no break in infinite loop
            status = (not a_utils.is_always_true(node.test)
                or (a_utils.get_child_instance(
                    node,
                    (ast.Break, ast.Return, ast.Raise)
                ) is not None) # TODO: Add quit(), exit(), sys.exit()
            )

            self.model.add_msg(
                "PT4-1",
                lineno=node.lineno,
                status=status
            )
        except AttributeError:
            pass
        self.generic_visit(node)

    def visit_For(self, node, *args, **kwargs):
        # iter name check
        try:
            if(isinstance(node.target, ast.Tuple)):
                for i in node.target.elts:
                    self.check_valid_name(node, i.id)
            else:
                self.check_valid_name(node, node.target.id)
        except AttributeError:
            pass
        self.generic_visit(node)

    # Assigns
    def visit_Assign(self, node, *args, **kwargs):
        try:
            # Variable name check
            for i in node.targets:
                self.check_valid_name(node, i.id)
        except AttributeError:
            pass
        self.generic_visit(node)

    # Functions
    def visit_AsyncFunctionDef(self, node, *args, **kwargs):
        # Function name check
        self._check_function_naming(node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node, *args, **kwargs):
        # Function name check
        self._check_function_naming(node)
        self.generic_visit(node)

    # Class definitions
    def visit_ClassDef(self, node, *args, **kwargs):
        try:
            # Class Name check
            self.check_valid_name(node, node.name)
        except AttributeError:
            pass
        self.generic_visit(node)

    # With statement
    def visit_With(self, node, *args, **kwargs):
        try:
            # Name check for alias variable after as-keyword
            for i in node.items:
                if(isinstance(i.optional_vars, ast.Tuple)):
                    for i in node.target.elts:
                        self.check_valid_name(node, i.optional_vars.id)
                else:
                    self.check_valid_name(node, i.optional_vars.id)
        except AttributeError:
            pass
        self.generic_visit(node)

    # Except handler
    def visit_ExceptHandler(self, node, *args, **kwargs):
        try:
            # Name check for alias variable after as-keyword
            self.check_valid_name(node, node.name)
        except AttributeError:
            pass
        self.generic_visit(node)

    # Imports
    # visit_alias would be great, but harder to get lineno
    def visit_Import(self, node, *args, **kwargs):
        # Name check for alias variable after as-keyword
        self._check_import_naming(node)
        self.generic_visit(node)

    def visit_ImportFrom(self, node, *args, **kwargs):
        # Name check for alias variable after as-keyword
        self._check_import_naming(node)
        self.generic_visit(node)

    # NOTE: Possibly checking Name node could check all the variable etc. names
    # It may give also other names, therefore not yet in use
    # At least function parameters and import aliases are not Name objects
    # def visit_Name(self, node, *args, **kwargs):
    #     try:
    #         self.check_valid_name(node.id)
    #     except AttributeError:
    #         pass
    #     self.generic_visit(node)

    def visit_Return(self, node, *args, **kwargs):
        self._check_unreachable_code(node, "return")

    def visit_Break(self, node, *args, **kwargs):
        self._check_unreachable_code(node, "break")

    def visit_Continue(self, node, *args, **kwargs):
        self._check_unreachable_code(node, "continue")

    def visit_Raise(self, node, *args, **kwargs):
        self._check_unreachable_code(node, "raise")

    # NOTE: yield or yield from can be followed by another code.
