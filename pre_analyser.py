"""Class file. Contains PreAnalyser class."""
__version__ = "0.0.1"
__author__ = "RL"

import ast

import utils_lib as utils

class PreAnalyser(ast.NodeVisitor):
    """
    TODO:
    1. Identify lib and main files
    2. Count that there are >= 2 function in lib file
    """
    def __init__(self):
        self.import_dict = dict()
        self.class_list = list()
        self.function_dict = dict()


   # Getters
    def get_import_dict(self):
        return dict(self.import_dict)

   # General methods
    def clear_all(self):
        self.import_dict.clear()
        self.function_dict.clear()
        self.class_list.clear()


    def _store_import(self, node, name, import_from=False):
        if(not name in self.import_dict.keys()):
            self.import_dict[name] = list()
        self.import_dict[name].append(utils.ImportTemplate(
            name, node.lineno, node, import_from=import_from))
        # if(lib_name in self.import_dict.keys()):
        #     if(importFrom):
        #         self.model.add_msg("MR3-1", lib_name, lineno=node.lineno)
        #     else:
        #         self.model.add_msg("MR3", lib_name, lineno=node.lineno)
        # else:
        #     self.import_dict[lib_name] = utils.ImportTemplate(lib_name, node.lineno, node, ast.ImportFrom)

   # Visits
    # Imports
    def visit_Import(self, node, *args, **kwargs):
        for i in node.names:
            self._store_import(node, i.name, import_from=False)
        self.generic_visit(node)

    def visit_ImportFrom(self, node, *args, **kwargs):
        self._store_import(node, node.module, import_from=True)
        self.generic_visit(node)

    # Functions
    def visit_FunctionDef(self, node, *args, **kwargs):
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node, *args, **kwargs):
        self.generic_visit(node)

    # Classes
    def visit_ClassDef(self, node, *args, **kwargs):
        self.generic_visit(node)
