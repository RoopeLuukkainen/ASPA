"""Class file. Contains ErrorHandlingAnalyser class."""
__version__ = "0.0.1"
__author__ = "RL"

import ast


import utils_lib

class ErrorHandlingAnalyser(ast.NodeVisitor):
    # Initialisation
    def __init__(self, model):
        self.model = model
   # Getters

   # Setters

   # General methods

   # Visits
    def visit_Try(self, node, *args, **kwargs):
        """Method to check if node is:
        1. Try with only one exception branch
        2. Exception branch missing a error type. Excluding the last 
            exception IF there are more than one exception branches.

        ast.Try has lists for each branchtype: handlers=[], orelse=[], finalbody=[],
        which are for excepts, else and finally, respectively
        
        Does not analyse
        1. finally branches
        2. else branches
        """
        try:
            if(not node.handlers):
                pass
            elif(len(node.handlers) < 2):
                # self.model.add_msg("PK1", lineno=node.lineno) 
                if(node.handlers[0].type == None): # TODO: THIS IS SAME check as "i.type == None" below, improve somehow
                    self.model.add_msg("PK1-1", lineno=node.handlers[0].lineno)
            else:
                for i in node.handlers[:-1]:
                    if(i.type == None):
                        self.model.add_msg("PK1-1", lineno=i.lineno)
        # except IndexError:
        #     print(f"IndexError at line: {node.lineno}, node: {node}")
        # except AttributeError:
        #     print(f"AttributeError at line: {node.lineno}, node: {node}")
        # except Exception as e:
        #     print(f"Error at line: {node.lineno}, node: {node}")
        #     print(f"message: {str(e)}")
        except Exception:
            pass

        self.generic_visit(node)


    def visit_Call(self, node, *args, **kwargs):
        """Method to check if node is:
        1. Missing try - except around file opening.
        """
        if(hasattr(node.func, "id") 
            and node.func.id == "open" 
            and hasattr(node, "parent_node")
            and utils_lib.get_parent_instance(node, ast.Try, 
                denied=(ast.FunctionDef, ast.AsyncFunctionDef)) is None):

            self.model.add_msg("PK3", lineno=node.lineno)
        self.generic_visit(node)


    def visit_Attribute(self, node, *args, **kwargs):
        """Method to check if node is:
        1. Missing try - except around file.read().
        2. Missing try - except around file.readline().
        3. Missing try - except around file.readlines().
        4. Missing try - except around file.write().
        5. Missing try - except around file.writelines().
        """
        file_operations = {"read", "readline", "readlines", "write", "writelines"}
        try:
            if(node.attr in file_operations
                    and utils_lib.get_parent_instance(node, ast.Try,
                    denied=(ast.FunctionDef, ast.AsyncFunctionDef)) is None):
                self.model.add_msg("PK4", node.value.id, node.attr, lineno=node.lineno)
        except AttributeError:
            # print("visit_Attribute, Attribute error", node, node.lineno)
            pass
        self.generic_visit(node)