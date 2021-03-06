"""Class file. Contains PreAnalyser class."""
import ast

import src.analysers.analysis_utils as a_utils
import src.config.templates as templates

class PreAnalyser(ast.NodeVisitor):
    """
    TODO:
    1. Identify lib and main files
    2. Count that there are >= 2 function in lib file
    """
    def __init__(self, library=None):
        self.import_dict = dict()
        self.class_dict = dict()
        self.function_dict = dict()
        self.global_dict = dict()
        self.constant_dict = dict()
        self.call_dict = dict()
        self.library = library


   # Getters
    def get_import_dict(self):
        return dict(self.import_dict)

    def get_function_dict(self):
        return dict(self.function_dict)

    def get_class_dict(self):
        return dict(self.class_dict)

    def get_global_dict(self):
        return dict(self.global_dict)

    def get_constant_dict(self):
        return dict(self.constant_dict)

    def get_call_dict(self):
        return dict(self.call_dict)

   # General methods
    def clear_all(self):
        self.import_dict.clear()
        self.function_dict.clear()
        self.class_dict.clear()
        self.global_dict.clear()
        self.constant_dict.clear()
        self.call_dict.clear()
        # del self.library

    # TODO: General store node function?
    def _store_import(self, node, name, import_from=False):
        if(self.library):
            name = f"{self.library}.{name}"
        if(not name in self.import_dict.keys()):
            self.import_dict[name] = list()
        self.import_dict[name].append(templates.ImportTemplate(
            name, node.lineno, node, import_from=import_from))

    def _store_assign(self, node):
        def get_names(var, name):
            name.clear()
            try:
                if(isinstance(var, ast.Attribute)):
                    pass

                elif(isinstance(var, ast.Tuple)):
                    for i in var.elts:
                        name.append(i.id)

                else:
                    name.append(var.id)

            except AttributeError:
                pass
            return name

        # Global variable detection
        names = list()
        for var in node.targets[:]:
            for name in get_names(var, names): # name must be str or int
                if(name in self.global_dict.keys()):
                    continue

                elif(name in self.constant_dict.keys()):
                    self.global_dict[name] = self.constant_dict.pop(name, None)

                elif(var.col_offset == 0 
                        or a_utils.get_parent_instance(node,
                        (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) is None):

                    # TODO: imporove this to detect tuples created with 
                    # tuple(), which is Call not Tuple
                    if(isinstance(node.value, (ast.Constant, ast.Tuple))):
                        self.constant_dict[name] = templates.GlobalTemplate(
                                                        name,
                                                        var.lineno,
                                                        var
                                                    )
                    else:
                        self.global_dict[name] = templates.GlobalTemplate(
                                                    name,
                                                    var.lineno,
                                                    var
                                                )

    def _store_class(self, node):
        key = node.name
        parent = a_utils.get_parent_instance(node, 
            (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        if(parent):
            key = f"{parent.name}.{key}"
        if(self.library):
            key = f"{self.library}.{key}"
        self.class_dict[key] = templates.ClassTemplate(
            node.name, node.lineno, node)

    def _store_function(self, node):
        key = node.name
        pos_args = [i.arg for i in node.args.args]
        kw_args = [i.arg for i in node.args.kwonlyargs]

        parent = a_utils.get_parent_instance(node, 
            (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        if(parent):
            key = f"{parent.name}.{key}"
        if(self.library):
            key = f"{self.library}.{key}"
        #  TODO: If key exist then there are two identically named functions 
        # in same scope
        # Could use similar list solution as with imports
        self.function_dict[key] = templates.FunctionTemplate(
            node.name, node.lineno, node, pos_args, kw_args)

    def _store_call(self, node):
        try:
            if(node.col_offset == 0 
                    or a_utils.get_parent_instance(node,
                    (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) is None):
                self.call_dict[node.func.id] = templates.CallTemplate(
                                                    node.func.id,
                                                    node.lineno,
                                                    node
                                                )
        except AttributeError:
            pass

   # Visits
    # Imports
    def visit_Import(self, node, *args, **kwargs):
        for i in node.names:
            self._store_import(node, i.name, import_from=False)
        self.generic_visit(node)

    def visit_ImportFrom(self, node, *args, **kwargs):
        self._store_import(node, node.module, import_from=True)
        self.generic_visit(node)

    # Assigns
    def visit_Assign(self, node, *args, **kwargs):
        self._store_assign(node)
        self.generic_visit(node)

    # Classes
    def visit_ClassDef(self, node, *args, **kwargs):
        self._store_class(node)
        self.generic_visit(node)

    # Functions
    def visit_FunctionDef(self, node, *args, **kwargs):
        self._store_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node, *args, **kwargs):
        self._store_function(node)
        self.generic_visit(node)

    # Calls
    def visit_Call(self, node, *args, **kwargs):
        self._store_call(node)
        self.generic_visit(node)
