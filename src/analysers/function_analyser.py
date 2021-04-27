"""Class file. Contains FunctionAnalyser class."""
import ast

import src.config.config as cnf
import src.analysers.analysis_utils as a_utils
import src.utils_lib as utils

class FunctionAnalyser(ast.NodeVisitor):
    # Initialisation
    def __init__(self, model):
        self.model = model
        self.MAIN_FUNC_NAME = cnf.MAIN_FUNC_NAME
        self.ALLOWED_FUNC = cnf.ALLOWED_FUNCTIONS
        self.DENIED_FUNC = cnf.DENIED_FUNCTIONS
        self.MISSING_RETURN_ALLOWED = cnf.MISSING_RETURN_ALLOWED
        self.ALLOWED_CONSTANTS = cnf.ALLOWED_CONSTANTS

        self.recursive_calls = {}

    def clear_all(self):
        self.recursive_calls.clear()
        return None

    # General methods
    def _check_return(self, node):
        """Method to check
        1. if function is missing a return

        NOTE 1:
        Functions with yield should not give return errors, e.g. AR6
        missing return at the end of the function. This partially
        works e.g. when yield is the last command AR6 is ignored.
        However, yield is rarely the last command of function body.
        """
        # TODO change such that checks if there is at least one return or yield
        # in the function.

        try:
            last = node.body[-1]
            # if(not (isinstance(last, ast.Return)
            #             or (isinstance(last, ast.Expr)
            #             and isinstance(last.value, cnf.YIELD)))
            #         and not "*" in self.MISSING_RETURN_ALLOWED
            #         and not node.name in self.MISSING_RETURN_ALLOWED):
            status = (
                isinstance(last, ast.Return)
                or (isinstance(last, ast.Expr) and isinstance(last.value, cnf.YIELD))
                or "*" in self.MISSING_RETURN_ALLOWED
                or node.name in self.MISSING_RETURN_ALLOWED
            )
        except AttributeError:
            status=False

        finally:
            self.model.add_msg(
                "AR6",
                node.name,
                lineno=node.lineno,
                status=status
            )

    def _check_return_location(self, node):
        """Method to check if node is:
        1. return-statement at the middle of the function.
        """

        self.model.add_msg(
            "AR6-2",
            lineno=node.lineno,
            status=(isinstance(node.parent_node, cnf.FUNC))
        )

    def _check_return_value(self, node, *args, **kwargs):
        """Method to check if node is:
        1. Return with missing return value
        2. Returning a constant such as 1 or "abc"
        3. Also detect if return value is
            1. name constant i.e. keyword None, True, False
            2. variable, set, tuple, list, dictionary.
            3. object or other value with attributes
            4. function call, recursive call is detected in visit_Call
               method

        TODO Does not find:
        1. If there are multiple returns
        2. If return is unreachable due to the logical condition,
           trivial cases are check with basic command check for
           unreachable code.
        """

        # NOTE Deprecated since version 3.8:
        # Methods visit_Num(), visit_Str(), visit_Bytes(), visit_NameConstant()
        # and visit_Ellipsis() are deprecated now and will not be called in
        # future Python versions. Add the visit_Constant() method to handle all
        # constant nodes.
        # Above this section:
        # https://docs.python.org/3.8/library/ast.html#abstract-grammar

        return_value = node.value
        valid_return = False
        # Match return <without anything>, not return None
        if return_value is None:
            self.model.add_msg("AR6-3", lineno=node.lineno)

        # This match name constants None, True, False
        elif isinstance(return_value, ast.NameConstant):
            # NOTE: since Python 3.8 NameConstants create Constant node but this
            # check seem to work anyway.
            valid_return = True

        # This match variables
        elif isinstance(return_value, ast.Name):
            valid_return = True

        # This match function calls.
        elif isinstance(return_value, ast.Call):
            valid_return = True

        # This match objects and other values with attributes.
        elif (isinstance(return_value, ast.Attribute)
                or (hasattr(return_value, "func")
                and isinstance(return_value.func, ast.Attribute))
        ):
            valid_return = True
        # This match sets, lists, dictionaries.
        elif isinstance(return_value, (ast.List, ast.Dict, ast.Set)):
            valid_return = True

        # This match tuples include also multiple return values case.
        elif isinstance(return_value, ast.Tuple):
            # NOTE: Idea of this check is to detect if student returns e.g.
            # 'return a, b'  which creates a Tuple node, unfortunately then
            # 'return (a, b)' creates an error too. Idea is that in the first
            # one student is not aware what (s)he is doing.
            #
            # if-statement makes 'return (a,)' allowed, however never seen a
            # student doing like that. 'return (a)' will assumet it's an
            # aritmetic operation and will not create a Tuple node.
            if len(return_value.elts) > 1:
                self.model.add_msg("AR6-5", lineno=node.lineno)
            else:
                valid_return = True

        # This match constant strings and numbers.
        elif (isinstance(return_value, (ast.Num, ast.Str, ast.Constant))
                and return_value.value not in self.ALLOWED_CONSTANTS
        ):
            # NOTE: since Python 3.8 ast.Num and ast.Str create ast.Constant
            # node but this check seem to work anyway.
            self.model.add_msg("AR6-4", lineno=node.lineno)

        # This match e.g. aritmetic operations and boolean operations such as
        # return 1 + 2
        # return a or b
        else:
            self.model.add_msg("AR6-6", lineno=node.lineno)

        return valid_return

    def _check_nested_function(self, node, *args, **kwargs):
        """Method to check
        1. function definition is not at a global scope.
        """
        try:
            name = node.name
        except AttributeError:
            return None

        status = True
        # Col offset should detect every function definition which is indended
        if (node.col_offset > 0
            or a_utils.get_parent(node, cnf.CLS_FUNC) is not None
        ):

            # This if check if there are allowed names for methods given.
            if (((not "*" in self.ALLOWED_FUNC and not name in self.ALLOWED_FUNC)
                    and (name in self.DENIED_FUNC or "*" in self.DENIED_FUNC))
                or (a_utils.get_parent(node, ast.ClassDef) is None)
            ):
                # If function name is not in denied and not in allowed
                # AND there is class as parent, then no error.
                status = False

        self.model.add_msg(
            "AR2-1",
            name,
            lineno=node.lineno,
            status=status
        )
        return None

    def _check_function_attributes(self, node, *args, **kwargs):
        """Check if attribute is added directly to function.
        NOTE: quite identical to detection TR2-1, i.e. CLASS is used
        directly without an object.
        """

        functions = self.model.get_function_dict().keys()

        try:
            for var in node.targets[:]:
                name = a_utils.get_attribute_name(var, splitted=True)
                if isinstance(var, ast.Attribute) and name[0] in functions:
                    self.model.add_msg("AR7", ".".join(name), lineno=var.lineno)
        except AttributeError:
            pass

    def _check_recursion(self, node, func, *args, **kwargs):
        """
        Private method to detect if function call is directly recursive,
        i.e. if function call inside a function is calling the function
        itself, e.g.:

        def func():
            ...
            func()
            ...

        If recursion is found, adds function to recursive_calls
        dictonary and adds the function call node to FunctionTemplate
        object in that dictionary.
        """

        try:
            # Recursive function calls
            if func == a_utils.get_parent(node, cnf.FUNC).name:
                self.recursive_calls.setdefault(
                    func,
                    self.model.get_function_dict().get(func)
                ).add_recursive_call(node)
        except AttributeError:
            # AttributeError occurs e.g. when function name is searched from
            # the global scope OR when get_parent no match and returns value
            # None, which does not has a attribute name.
            pass

    def _check_paramenters(self, node, function_name, *args, **kwargs):
        # FIXME doesn't detect directly imported functions, i.e. from import ...
        # with function name or with *
        #
        # FIXME: doesn't test functions from libraries which are named with as-
        # keyword, i.e. import library as lib

        def count_args(func_name, funcs, *args, **kwargs):
            func = funcs[func_name] # Shorthand variable for current function.

            has_args = True if func.astree.args.vararg else False
            has_kwargs = True if func.astree.args.kwarg else False
            default_count = len(func.astree.args.defaults)
            args_count = len(func.pos_args)  # This is directly from FunctionTemplate class
            # kw_default_count = len(func.astree.args.kw_defaults) # Currently not used
            # kw_only_count = len(func.kw_args) # Currently not used # This is directly from FunctionTemplate class

            call_arg_count = len(node.args)
            # call_kw_count = len(node.keywords) # Currently not used

            # call_pos_args_with_value is used to count how many positional
            # arguments have value given in function call, e.g.
            # 'def addition(a, b):'
            # is called like
            # 'addition(a=10, b=10)'
            call_pos_args_with_value = 0
            for i in node.keywords:
                if i.arg in func.pos_args:
                    call_pos_args_with_value += 1

            # Checking if there are TOO FEW parameters given
            self.model.add_msg(
                "AR5-1",
                func_name,
                args_count - default_count,
                call_arg_count,
                lineno=node.lineno,
                status=(
                    (call_arg_count + call_pos_args_with_value) >= (args_count - default_count)
                )
            )

            # Checking if there are TOO MANY parameters given
            self.model.add_msg(
                "AR5-2",
                func_name,
                args_count,
                call_arg_count,
                lineno=node.lineno,
                status=(has_args or (call_arg_count <= args_count))
            )

            if not has_kwargs:
                # NOTE Same loop as above, check if possible to combine
                # (note that this is inside if)
                for i in node.keywords:
                    self.model.add_msg(
                        "AR5-3",
                        func_name,
                        i.arg,
                        lineno=node.lineno,
                        status=(i.arg in func.kw_args or i.arg in func.pos_args)
                    )
            return None

        # Parameter and argument check tested with Python 3.8.5
        try:
            funs = self.model.get_function_dict()
            function_names = funs.keys()
            if function_name in function_names:
                count_args(function_name, funs)
        except (AttributeError, KeyError):
            # print(f"Error at {node.lineno}, with {node}") # Debug
            pass
        except:
            pass

    def _found_yield(self, node, yield_type="yield"):
        self.model.add_msg(
            "AR6-1",
            yield_type,
            a_utils.get_parent(node, cnf.FUNC).name,
            lineno=node.lineno
        )

    def _found_global(self, node):
        try:
            for var in node.names:
                self.model.add_msg("AR3", var, lineno=node.lineno)
        except AttributeError:
            pass

    def check_main_function(self, *args, **kwargs):
        if len(self.model.get_call_dict().keys()) > 0:
            self.model.add_msg(
                "AR1",
                status=(
                    self.MAIN_FUNC_NAME in self.model.get_function_dict().keys()
                )
            )
        return None

    def check_element_order(self, body, element_order, *args, **kwargs):
        """Method to check if ast.nodes in 'body' are in desired order.
        Order is defined in element_order with following format:
        ((ast nodes), (must have names/id), (not allowed names/id), "msg ID")

        BKTA get correctly done ONLY when not a single item is wrong,
        but each incorrect one gives one wrong.
        TODO: BKTA could be done true or false per file.
        """
        def check_name(tree, required, denied):
            valid = True
            name = ""
            if required or denied:
                for node in ast.walk(tree):
                    n = getattr(node, "name", None)
                    i = getattr(node, "id", None)
                    if n:
                        name = n
                        break
                    elif i:
                        name = i
                        break
                if required and not name in required:
                    valid = False
                elif denied and name in denied:
                    valid = False
            return valid

        cur = 0
        all_correct = True
        for item in body:  # Check items from top to bottom
            temp = cur
            for elem in element_order[cur:]:
                if isinstance(item, elem[0]):
                    try:
                        if check_name(item, elem[1], elem[2]):
                            cur = temp
                            break
                        elif ("Docstring" in elem[1]
                                and isinstance(item.value, ast.Constant)
                                and isinstance(item.value.value, str)
                        ):
                            # Only one docstring is allowed therefore moves to
                            # next element
                            cur = temp = temp + 1
                            break
                    except AttributeError:
                        pass
                temp += 1
            else:
                self.model.add_msg("MR1", lineno=item.lineno)
                all_correct = False

        if all_correct:
            self.model.add_msg("MR1", status=True)
        return None

    def check_global_variables(self):
        for i in sorted(self.model.get_global_variables().values(),
                        key=lambda elem: elem.lineno):
            self.model.add_msg("AR3", i.name, lineno=i.lineno)

    def _exclude_imported_functions(self, fun_dict_full):
        """
        Private method to exclude all the functions which are imported.
        """

        func_dict_local = dict(
            filter(
                lambda elem: not elem[1].imported,
                fun_dict_full.items()
            )
        )
        return func_dict_local

    def check_recursive_functions(self, func_dict):
        """
        Method to detected which functions are done without a single
        recursive call and which ones have one or more recursive call.

        NOTE EACH recursive CALL creates a violation, but each FUNCTION
        without a recursion creates ONE correctly done function.

        Attributes:
        1. func_dict - Dict[FunctionTemplate] - Dictionary containing
           function template objects (defined in templates.py file).
           Keys are str of function name in addition the format
           "parent.name" is also accepted and they are used to get
           values from recursive_calls dictionary.

        Return: None
        """

        try:
            local_functions = self._exclude_imported_functions(func_dict)
            for func_name, func_obj in local_functions.items():
                if (temp := self.recursive_calls.get(func_name)):
                    for node in temp.get_recursive_calls():
                        self.model.add_msg(
                            "AR4",
                            lineno=node.lineno,
                            status=False
                        )
                else:
                    self.model.add_msg(
                        "AR4",
                        lineno=func_obj.lineno,
                        status=True
                    )
        except AttributeError:
            pass

   # Visits
    def visit_Assign(self, node, *args, **kwargs):
        self._check_function_attributes(node)
        self.generic_visit(node)

    def visit_Global(self, node, *args, **kwargs):
        """Method to detect usage of global keyword."""

        self._found_global(node)
        self.generic_visit(node)

    def visit_Return(self, node, *args, **kwargs):
        """Method to detect usage of 'return'."""

        self._check_return_location(node)
        is_valid_return = self._check_return_value(node)

        # TODO BKTA
        # self.model.add_msg(
        #     "AR6-00",
        #     lineno=node.lineno,
        #     status=is_valid_return
        # )
        self.generic_visit(node)

    def visit_Call(self, node, *args, **kwargs):
        """Method to check if node is:
        1. Recursive function call.
        2. Check that arguments and parameters match
        """

        try:
            if hasattr(node.func, "id"):
                fun = node.func.id
            else:
                fun = f"{node.func.value.id}.{node.func.attr}"
        except (AttributeError, Exception): # AttributeError occur e.g. with attribute/method calls.
            pass
        else:
            self._check_recursion(node, fun)
            self._check_paramenters(node, fun)

        self.generic_visit(node)

    def visit_FunctionDef(self, node, *args, **kwargs):
        """Method to find:
        1. Usage of return at the END of the function

        TODO Does not find:
        1. If there are multiple returns
        """

        self._check_return(node)
        self._check_nested_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node, *args, **kwargs):
        """Method to check usage of async functions. Currently checks:
        1. If function declaration is nested.
        """
        self._check_return(node)
        self._check_nested_function(node)
        self.generic_visit(node)

    def visit_Yield(self, node, *args, **kwargs):
        """Method to detect usage of yield."""
        self._found_yield(node, yield_type="yield")
        self.generic_visit(node)

    def visit_YieldFrom(self, node, *args, **kwargs):
        """Method to detect usage of yield from."""
        self._found_yield(node, yield_type="yield from")
        self.generic_visit(node)