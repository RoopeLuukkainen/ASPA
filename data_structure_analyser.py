"""Class file. Contains DataStructureAnalyser class."""
__version__ = "0.1.1"
__author__ = "RL"

import ast


import utils_lib as utils

class DataStructureAnalyser(ast.NodeVisitor):
   # Initialisations
    def __init__(self, model):
        self.model = model

   # Visits
    def visit_Assign(self, node, *args, **kwargs):
        """Method to find:
        1. Direct usage of CLASS variables via class itself.
        2. Assiging CLASS to variable, i.e. object = CLASS <without parenthesis>
        """
        classes = self.model.get_class_dict().keys()
        # Class as global variable detection
        for var in node.targets[:]:
            if(isinstance(var, ast.Attribute)
                    and hasattr(var.value, "id")
                    and var.value.id in classes):
                self.model.add_msg("TR2-1", var.value.id, var.attr, lineno=var.lineno)

        # Object creating without parenthesis
        try:
            name = node.value.id
            parent = utils.get_parent_instance(node, 
                (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))

            if(name in classes or f"{parent.name}.{name}" in classes):
                self.model.add_msg("TR2-2", name, lineno=node.lineno)
        except AttributeError:
            pass

        self.generic_visit(node)

    def visit_ClassDef(self, node, *args, **kwargs):
        """Method to check if 
        1. Class is created in global scope
        """
        if(node.col_offset > 0):
            self.model.add_msg("TR2-3", node.name, lineno=node.lineno)
        
        # if(utils.get_parent_instance(node, 
        #       (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) is not None):
        #     print(node.lineno)
        self.generic_visit(node)