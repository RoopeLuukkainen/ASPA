"""Class file. Contains FileHandlingAnalyser class."""
__version__ = "0.0.1"
__author__ = "RL"

import ast


import utils_lib as utils

class FileHandlingAnalyser(ast.NodeVisitor):
    # Initally opened and closed were SETs of names, that was super easy and efficient but not complete solution
    def __init__(self, model):
        self.model = model

   # General methods
    def check_left_open_files(self):
        """Method to detect left open filehandles."""
        temp = None
        left_open = list(self.model.get_files_opened())
        for closed in self.model.get_files_closed():
            for opened in self.model.get_files_opened():
                if(closed.id == opened.id
                        and closed.lineno >= opened.lineno
                        and utils.get_parent_instance(opened, (ast.FunctionDef, ast.AsyncFunctionDef))
                        is utils.get_parent_instance(closed, (ast.FunctionDef, ast.AsyncFunctionDef))):
                    temp = opened
            if(temp):  # After for loop to find last file handle
                try:
                    left_open.remove(temp)
                    temp = None
                except ValueError:
                    pass  # In this case same file is closed again
        return left_open

   # Visits
    def visit_Attribute(self, node, *args, **kwargs):
        """Method to check if node is:
        1. Closing a file.
        2. Closing a file in except branch.
        """
        try:
            if(node.attr == "close"):
                if(utils.get_parent_instance(node, ast.ExceptHandler) is not None):
                    self.model.add_msg("TK1-2", node.value.id, lineno=node.lineno)
                if(utils.get_parent_instance(node, ast.Call) is None):
                    self.model.add_msg("TK1-3", node.value.id, "close", lineno=node.lineno)
                if(hasattr(node, "value") and isinstance(node.value, ast.Name)):
                    self.model.set_files_closed(node.value, append=True)
        except AttributeError:
            pass
        self.generic_visit(node)


    def visit_Call(self, node, *args, **kwargs):
        """Method to check if node is:
        1. Opening a file.
        """
        if(hasattr(node.func, "id") and node.func.id == "open"
                and hasattr(node, "parent_node")):
            parent = node.parent_node

            if(isinstance(parent, ast.Assign)):
                for name_obj in parent.targets:
                    self.model.set_files_opened(name_obj, append=True)

        self.generic_visit(node)