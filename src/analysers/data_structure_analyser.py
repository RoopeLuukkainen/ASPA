"""Class file. Contains DataStructureAnalyser class."""
import ast

import src.analysers.analysis_utils as a_utils

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
        # Usaging class directly without an object
        # NOTE: identical to detection AR-7, i.e. assigning attribute to function.
        classes = self.model.get_class_dict().keys()

        try:
            for var in node.targets[:]:
                name = a_utils.get_attribute_name(var, splitted=True)
                if(isinstance(var, ast.Attribute) and name[0] in classes):
                    self.model.add_msg("TR2-1", ".".join(name), lineno=var.lineno)
        except AttributeError:
            pass

        # Object creation without parenthesis
        try:
            name = node.value.id
            parent = a_utils.get_parent_instance(node, 
                (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))

            if(name in classes or f"{parent.name}.{name}" in classes):
                self.model.add_msg("TR2-2", name, lineno=node.lineno)
        except AttributeError:
            pass

        self.generic_visit(node)

    def visit_ClassDef(self, node, *args, **kwargs):
        """Method to check
        1. Class is created in global scope
        """
        # Col offset should detect every class definition which is indended
        if(node.col_offset > 0
                or a_utils.get_parent_instance(node, 
                (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) is not None):
            self.model.add_msg("TR2-3", node.name, lineno=node.lineno)

        if(not node.name.isupper()):
            self.model.add_msg("TR2-4", node.name, lineno=node.lineno)

        self.generic_visit(node)