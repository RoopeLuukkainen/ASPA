"""Class file. Contains FunctionAnalyser class."""
__version__ = "0.2.0"
__author__ = "RL"

import ast

import utils_lib as utils

class FunctionAnalyser(ast.NodeVisitor):
    # Initialisation
    def __init__(self, model):
        self.model = model

    # General methods
    def _check_nested_function(self, node, *args, **kwargs):
        """Method to check if function definition is not at a global scope."""
        if(utils.get_parent_instance(node, 
                (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) is not None):
            self.model.add_msg("AR2-1", node.name, lineno=node.lineno)

    def check_main_function(self, *args, **kwargs):
        # CHECK IF there is any global scope calls and also if there there is
        # import to local lib it should be main file.
        if(not utils.MAIN_FUNC_NAME in self.model.get_function_dict().keys()):
            self.model.add_msg("AR1")

        # if(not utils.MAIN_FUNC_NAME in self.model.get_call_dict().keys()):
        #     pass # No paaohjelma called

    def check_element_order(self, body, element_order, *args, **kwargs):
        """Method to check if ast.nodes in 'body' are in desired order.
        Order is defined in element_order with following format:
        ((ast nodes), (must have names/id), (not allowed names/id), "msg ID")
        """
        def check_name(tree, required, denied):
            valid = True
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
                if(isinstance(item, elem[0]) and check_name(item, elem[1], elem[2])):
                    cur = temp
                    break
                temp += 1
            else:
                self.model.add_msg("MR1", lineno=item.lineno)

    def _check_recursion(self, node, func, *args, **kwargs):
        # Recursive function calls.
        try:
            if(func == utils.get_parent_instance(node,
                    (ast.FunctionDef, ast.AsyncFunctionDef)).name):
                self.model.add_msg("AR4", lineno=node.lineno)
        except AttributeError:  # AttributeError occus e.g. when function name is searched from global scope
            pass

    def _check_paramenters(self, node, func, *args, **kwargs):
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
            functionnames = funs.keys()
            if(func in functionnames):
                count_args(func, funs)
        except (AttributeError, KeyError, UnboundLocalError):
            # print(f"Error at {node.lineno}, with {node}") # Debug
            pass
        except:
            pass

   # Visits
    def visit_Assign(self, node, *args, **kwargs):
        """Method to find:
        1. Global variables by checking col_offset i.e. indention
        and checking does assign have FuncDef as parent.

        TODO Does not match:
        1. globals which are not classes and are indended.
            However utils.global_test find those.
        2. Expr objects like file_handle.close()
        """
        # Global variable detection
        for var in node.targets[:]:
            if(node.col_offset == 0
                    or utils.get_parent_instance(node,
                    (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) is None):
                if(isinstance(var, ast.Attribute)):
                    self.model.add_msg("AR3-2", var.value.id, var.attr, lineno=var.lineno)
                    global_var = var.value.id
                else:
                    self.model.add_msg("AR3", var.id, lineno=var.lineno)
                    global_var = var.id

                self.model.set_global_variables(global_var, add=True)

            else:
                # This currently (doesn't?) match globals which are not classes and are indended
                # however utils.global_test find those.
                # Should check if there is no class or function as parent
                pass
                # self.model.local_variables.add(var.id)
        self.generic_visit(node)

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
            4. function call, recursive call is detected in visit_Call method

        TODO Does not find:
        1. If there are multiple returns
        2. If return is unreachable
        3. If there are lines after the return TODO: Same thing with break and continue
            e.g. by going one level up to parent and check if there are nodes which are after the return.
        """
        if(not isinstance(node.parent_node, (ast.FunctionDef, ast.AsyncFunctionDef))):
            self.model.add_msg("AR6-2", lineno=node.lineno)

        return_value = node.value
        if(return_value is None):  # i.e. Match return <without anything>, but not return None
            self.model.add_msg("AR6-3", lineno=node.lineno)

        # This match keyword constants None, True, False etc.
        elif((isinstance(return_value, ast.NameConstant)
                or isinstance(return_value, ast.Name))
                and hasattr(return_value, "value")):
            pass

        # This match variables, sets, tuples, lists, dictionaries.
        elif(isinstance(return_value, (ast.Name, ast.List, ast.Tuple, ast.Dict, ast.Set))):
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
            pass
            #TODO: Remove test print when not needed anymore
            # print("<TEST: Palautetaan jotain mitä ei tunnistettu!>", return_value.lineno) # Debug
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
        # has_return = False
        # for elem in node.body:
        #     if(isinstance(elem, ast.Return)):
        #         has_return = True

        # else:  # this match if 1 layer of function body has no return, 
                 # doesn't work if return is indented more
        #     if(not has_return):
        #         self.model.add_msg("AR6", node.name, lineno=node.lineno)

        if(not isinstance(node.body[-1], ast.Return)):
        #         and node.body[-1] is not ast.Yield
        #         and node.body[-1] is not ast.YieldFrom): # Doesn't work because yield (from) are inside expr node
            self.model.add_msg("AR6", node.name, lineno=node.lineno)

        self._check_nested_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node, *args, **kwargs):
        """Method to check usage of async functions. Currently checks:
        1. If function declaration is nested.
        """
        self._check_nested_function(node)
        self.generic_visit(node)


    def visit_Yield(self, node, *args, **kwargs):
        """Method to detect usage of yield."""
        self.model.add_msg("AR6-1",
            "yield",
            utils.get_parent_instance(node, (ast.FunctionDef, ast.AsyncFunctionDef)).name,
            lineno=node.lineno)
        self.generic_visit(node)

    def visit_YieldFrom(self, node, *args, **kwargs):
        """Method to detect usage of yield from."""
        self.model.add_msg("AR6-1",
            "yield from",
            utils.get_parent_instance(node, (ast.FunctionDef, ast.AsyncFunctionDef)).name,
            lineno=node.lineno)
        self.generic_visit(node)