"""Class file. Contains FileHandlingAnalyser class."""
import ast

import src.analysers.analysis_utils as a_utils

class FileHandlingAnalyser(ast.NodeVisitor):
    # Initally opened and closed were SETs of names, that was super easy and efficient but not complete solution
    def __init__(self, model):
        self.model = model
        self.file_operations = {"read", "readline", "readlines", "write", "writelines"}

   # General methods
    def check_left_open_files(self, opened_files, closed_files):
        """Method to detect left open filehandles."""
        temp = None
        left_open = list(opened_files)
        for closed in closed_files:
            for opened in opened_files:
                if(closed.id == opened.id
                        and closed.lineno >= opened.lineno
                        and a_utils.get_parent_instance(opened, (ast.FunctionDef, ast.AsyncFunctionDef))
                        is a_utils.get_parent_instance(closed, (ast.FunctionDef, ast.AsyncFunctionDef))):
                    temp = opened
            if(temp):  # After for loop to find last file handle
                try:
                    left_open.remove(temp)
                    temp = None
                except ValueError:
                    pass  # In this case same file is closed again

        for file in left_open:
            self.model.add_msg("TK1", file.id, lineno=file.lineno)
        return None

    def check_same_parent(self, node, attr, parent=tuple()):
        try:
            func = a_utils.get_parent_instance(node, parent)
            name = node.value.id
            line = node.lineno
            has_close = False
            has_open = False
            if(not (func and name)):
                return None

            for i in ast.walk(func):
                if(isinstance(i, ast.With)
                        and i.lineno <= line):
                    has_close = has_open = True
                    break
                elif(isinstance(i, ast.Attribute)
                        and i.value.id == name
                        and i.attr == "close"):
                        # and i.lineno >= line):
                    has_close = True
                elif(isinstance(i, ast.Assign)
                        and i.targets[0].id == name
                        and i.value.func.id == "open"):
                        # and i.lineno <= line):
                    has_open = True

            if(not (has_close and has_open)):
                self.model.add_msg("TK2", name, attr, lineno=node.lineno)
        except AttributeError:
            pass
        return None

   # Visits
    def visit_Attribute(self, node, *args, **kwargs):
        """Method to check if node is:
        1. Closing a file.
        2. Closing a file in except branch.
        """
        try:
            if(node.attr == "close"):
                if(a_utils.get_parent_instance(node, ast.ExceptHandler) is not None):
                    self.model.add_msg("TK1-2", node.value.id, lineno=node.lineno)
                if(a_utils.get_parent_instance(node, ast.Call) is None):
                    self.model.add_msg("TK1-3", node.value.id, "close", lineno=node.lineno)
                if(hasattr(node, "value") and isinstance(node.value, ast.Name)):
                    self.model.set_files_closed(node.value, append=True)

            elif(node.attr in self.file_operations):
                self.check_same_parent(node, node.attr, (ast.FunctionDef, ast.AsyncFunctionDef))
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

    def visit_With(self, node, *args, **kwargs):
        try:
            for i in node.items:
                if(i.context_expr.func.id == "open"):
                    self.model.add_msg("TK1-1", "with open", lineno=node.lineno)
        except AttributeError:
            pass
        self.generic_visit(node)