"""Class file. Contains FunctionAnalyser class."""
import ast

import src.analysers.analysis_utils as au
import src.config.config as cnf

class FunctionAnalyser(ast.NodeVisitor):
    # Initialisation
    def __init__(self, model):
        self.model = model
        self.MAIN_FUNC_NAME = cnf.MAIN_FUNC_NAME
        self.ALLOWED_FUNC = cnf.ALLOWED_FUNCTIONS
        self.DENIED_FUNC = cnf.DENIED_FUNCTIONS
        self.MISSING_RETURN_ALLOWED = cnf.MISSING_RETURN_ALLOWED

    # General methods
    def _check_return(self, node, *args, **kwargs):
        last = node.body[-1]
        try:
            if(not (isinstance(last, ast.Return)
                        or (isinstance(last, ast.Expr)
                        and isinstance(last.value, cnf.YIELD)))
                    and not "*" in self.MISSING_RETURN_ALLOWED
                    and not node.name in self.MISSING_RETURN_ALLOWED):
                self.model.add_msg("AR6", node.name, lineno=node.lineno)
        except AttributeError:
            pass

    def _check_nested_function(self, node, *args, **kwargs):
        """Method to check
        1. function definition is not at a global scope.
        """
        try:
            name = node.name
        except AttributeError:
            return None
        # Col offset should detect every function definition which is indended
        if(node.col_offset > 0
                or au.get_parent(node, cnf.CLS_FUNC) is not None):

            # This if check if there are allowed names for methods given.
            if(((not "*" in self.ALLOWED_FUNC and not name in self.ALLOWED_FUNC)
                 and (name in self.DENIED_FUNC or "*" in self.DENIED_FUNC))
                    or (au.get_parent(node, ast.ClassDef) is None)):
                # If function name is not in denied and not in allowed
                # AND there is class as parent, then no error.
                self.model.add_msg("AR2-1", name, lineno=node.lineno)
        return None


    def check_main_function(self, *args, **kwargs):
        if(len(self.model.get_call_dict().keys()) > 0
                and not self.MAIN_FUNC_NAME in self.model.get_function_dict().keys()):
            self.model.add_msg("AR1")

        # if(not self.MAIN_FUNC_NAME in self.model.get_call_dict().keys()):
        #     pass # No paaohjelma called
        return None

    def check_element_order(self, body, element_order, *args, **kwargs):
        """Method to check if ast.nodes in 'body' are in desired order.
        Order is defined in element_order with following format:
        ((ast nodes), (must have names/id), (not allowed names/id), "msg ID")
        """
        def check_name(tree, required, denied):
            valid = True
            name = ""
            if(required or denied):
                for node in ast.walk(tree):
                    n = getattr(node, "name", None)
                    i = getattr(node, "id", None)
                    if(n):
                        name = n
                        break
                    elif(i):
                        name = i
                        break
                if(required and not name in required):
                    valid = False
                elif(denied and name in denied):
                    valid = False
            return valid

        cur = 0
        for item in body:  # Check items from top to bottom
            temp = cur
            for elem in element_order[cur:]:
                if(isinstance(item, elem[0])):
                    try:
                        if(check_name(item, elem[1], elem[2])):
                            cur = temp
                            break
                        elif("Docstring" in elem[1]
                                and isinstance(item.value, ast.Constant)
                                and isinstance(item.value.value, str)):
                            # Only one docstring is allowed therefore moves to
                            # next element
                            cur = temp = temp + 1
                            break
                    except AttributeError:
                        pass
                temp += 1
            else:
                self.model.add_msg("MR1", lineno=item.lineno)

    def _check_recursion(self, node, func, *args, **kwargs):
        # Recursive function calls.
        try:
            if(func == au.get_parent(node, cnf.FUNC).name):
                self.model.add_msg("AR4", lineno=node.lineno)
        except AttributeError:  # AttributeError occus e.g. when function name is searched from global scope
            pass

    def _check_paramenters(self, node, func, *args, **kwargs):
        # FIXME: check case where function is called with keyword like
        # def func(a, b): pass
        # func(a, b=1)
        #
        # FIXME doesn't detect directly imported functions, i.e. from import ...
        # with function name or with *
        #
        # FIXME: doesn't test functions from libraries which are named with as-
        # keyword, i.e. import library as lib

        def count_args(func, funs, *args, **kwargs):
            has_args = True if(funs[func].astree.args.vararg) else False
            has_kwargs = True if(funs[func].astree.args.kwarg) else False
            default_count = len(funs[func].astree.args.defaults)
            args_count = len(funs[func].pos_args)  # This is directly from FunctionTemplate class
            # kw_default_count = len(funs[fun].astree.args.kw_defaults) # Currently not used
            # kw_only_count = len(funs[fun].kw_args) # Currently not used # This is directly from
                                                    # FunctionTemplate class

            call_arg_count = len(node.args)
            # call_kw_count = len(node.keywords) # Currently not used

            if(call_arg_count < (args_count - default_count)):
                self.model.add_msg("AR5-1", func, args_count, call_arg_count, lineno=node.lineno)
            elif(not has_args and (call_arg_count > args_count)):
                self.model.add_msg("AR5-2", func, args_count, call_arg_count, lineno=node.lineno)

            if(not has_kwargs):
                for i in node.keywords:
                    if(i.arg not in funs[func].kw_args):
                        self.model.add_msg("AR5-3", func, i.arg, lineno=node.lineno)
            return None

        # Parameter and argument check tested with Python 3.8.5
        try:
            funs = self.model.get_function_dict()
            function_names = funs.keys()
            if(func in function_names):
                count_args(func, funs)
        except (AttributeError, KeyError):
            # print(f"Error at {node.lineno}, with {node}") # Debug
            pass
        except:
            pass

    def _check_global_variables(self):
        for i in sorted(self.model.get_global_variables().values(),
                        key=lambda elem: elem.lineno):
            self.model.add_msg("AR3", i.name, lineno=i.lineno)


   # Visits
    def visit_Assign(self, node, *args, **kwargs):
        # Adding attribute to function detection
        # NOTE: quite identical to detection TR2-1, i.e. CLASS is used directly without an object.
        functions = self.model.get_function_dict().keys()

        try:
            for var in node.targets[:]:
                name = au.get_attribute_name(var, splitted=True)
                if(isinstance(var, ast.Attribute) and name[0] in functions):
                    self.model.add_msg("AR7", ".".join(name), lineno=var.lineno)
        except AttributeError:
            pass
    # def visit_Assign(self, node, *args, **kwargs):
    #     """Method to find:
    #     1. Global variables by checking col_offset i.e. indention
    #     and checking does assign have FuncDef as parent.

    #     TODO Does not match:
    #     1. Expr objects like file_handle.close()
    #     """
    #     # Global variable detection
    #     for var in node.targets[:]:
    #         if(node.col_offset == 0
    #                 or au.get_parent(node,
    #                 (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) is None):
    #             if(isinstance(var, ast.Attribute)):
    #                 self.model.add_msg("AR3-2", var.value.id, var.attr, lineno=var.lineno)
    #                 global_var = var.value.id
    #             elif(isinstance(var, ast.Tuple)):
    #                 global_var = "TEMP"
    #             else:
    #                 self.model.add_msg("AR3", var.id, lineno=var.lineno)
    #                 global_var = var.id

    #             self.model.set_local_variables(global_var, add=True) # temporal

    #         else:
    #             pass
    #             # self.model.local_variables.add(var.id)
    #     self.generic_visit(node)

    def visit_Global(self, node, *args, **kwargs):
        """
        Method to detect usage of global keyword.
        """
        try:
            for var in node.names:
                self.model.add_msg("AR3", var, lineno=node.lineno)
        except AttributeError:
            pass
        self.generic_visit(node)

    def visit_Return(self, node, *args, **kwargs):
        """Method to check if node is:
        1. return-statement at the middle of the function.
        2. Missing return
        3. Return with missing return value
        4. Returning a constant such as 1 or "abc"
        5. Also detect (but pass) if return value is
            1. constant keyword None, True, False etc.
            2. variable, set, tuple, list, dictionary.
            3. object or other value with attributes
            4. function call, recursive call is detected in visit_Call
               method

        TODO Does not find:
        1. If there are multiple returns
        2. If return is unreachable due to the logical condition,
           trivial cases are check with basic command check for
           unreachable code.
        3. Functions with yield should not give return errors, e.g. AR6
           missing return at the end of the function. This partially
           works e.g. when yield is the last command AR6 is ignored.
           However, yield is rarely the last command of function body.
        """

        # NOTE Deprecated since version 3.8:
        # Methods visit_Num(), visit_Str(), visit_Bytes(), visit_NameConstant()
        # and visit_Ellipsis() are deprecated now and will not be called in
        # future Python versions. Add the visit_Constant() method to handle all
        # constant nodes.

        if(not isinstance(node.parent_node, cnf.FUNC)):
            self.model.add_msg("AR6-2", lineno=node.lineno)

        return_value = node.value
        if(return_value is None):  # i.e. Match return <without anything>, but not return None
            self.model.add_msg("AR6-3", lineno=node.lineno)

        # This match keyword constants None, True, False etc.
        elif((isinstance(return_value, ast.NameConstant)
                or isinstance(return_value, ast.Name))
                and hasattr(return_value, "value")):
            pass

        # This match tuples include also multiple retun values case.
        elif(isinstance(return_value, ast.Tuple)):
            self.model.add_msg("AR6-5", lineno=node.lineno)
            pass

        # This match variables, sets, lists, dictionaries.
        elif(isinstance(return_value, (ast.Name, ast.List, ast.Dict, ast.Set))):
            pass

        # This match objects and other values with attributes.
        elif(isinstance(return_value, ast.Attribute)
                or (hasattr(return_value, "func")
                and isinstance(return_value.func, ast.Attribute))):
            pass

        # This match constant strings and numbers.
        elif(isinstance(return_value, (ast.Num, ast.Str))):
            self.model.add_msg("AR6-4", lineno=node.lineno)

        # This match function calls.
        elif(isinstance(return_value, ast.Call)):
            pass

        # This match e.g. aritmetic operations and boolean operations such as
        # return 1 + 2
        # return a or b
        else:
            self.model.add_msg("AR6-6", lineno=node.lineno)
        self.generic_visit(node)

    def visit_Call(self, node, *args, **kwargs):
        """Method to check if node is:
        1. Recursive function call.
        2. Check that arguments and parameters match
        """
        try:
            if(hasattr(node.func, "id")):
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
        self.model.add_msg(
            "AR6-1",
            "yield",
            au.get_parent(node, cnf.FUNC).name,
            lineno=node.lineno
        )
        self.generic_visit(node)

    def visit_YieldFrom(self, node, *args, **kwargs):
        """Method to detect usage of yield from."""
        self.model.add_msg(
            "AR6-1",
            "yield from",
            au.get_parent(node, cnf.FUNC).name,
            lineno=node.lineno
        )
        self.generic_visit(node)