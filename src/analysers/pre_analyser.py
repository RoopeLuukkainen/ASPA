"""Class file. Contains PreAnalyser class."""

import ast

import src.analysers.analysis_utils as a_utils
import src.config.config as cnf
import src.config.templates as templates

class PreAnalyser(ast.NodeVisitor):
    """
    TODO:
    1. Identify lib and main files
    2. Count that there are >= 2 function in lib file
    3. Add General store node function wrapper, maybe??
    """

   # ------------------------------------------------------------------------- #
   # Initialisation
    def __init__(self, library=None):
        self.import_dict = {}
        self.class_dict = {}
        self.function_dict = {}
        self.global_dict = {}
        self.constant_dict = {}
        self.call_dict = {}     # Global scope calls
        self.file_list = []     # Opened filehandles
        self.local_global_dict = {} # Local variables with same name as global
        self.library = library

        self._possible_constant_dict = {}
        self._list_mod_attrs = a_utils.LIST_MODIFICATION_ATTRIBUTES
        self._dict_mod_attrs = a_utils.DICT_MODIFICATION_ATTRIBUTES
   # ------------------------------------------------------------------------- #
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

    def get_file_list(self):
        return list(self.file_list)

    def get_local_global_dict(self):
        return dict(self.local_global_dict)

   # ------------------------------------------------------------------------- #
   # General methods
    def clear_all(self):
        self.import_dict.clear()
        self.function_dict.clear()
        self.class_dict.clear()
        self.global_dict.clear()
        self.constant_dict.clear()
        self._possible_constant_dict.clear()
        self.call_dict.clear()
        self.file_list.clear()
        self.local_global_dict.clear()
        # del self.library

    def lock_constants(self):
        """Method to store remaining possible constants as
        real constants to constant_dict.
        """
        self.constant_dict.update(self._possible_constant_dict)

    def _get_names(self, var, name):
        name.clear()
        try:
            if isinstance(var, (ast.Attribute, ast.Subscript)): # TODO Use Match case here
                name.append(var.value.id)
            elif isinstance(var, ast.Tuple):
            # NOTE this might be unused due to the Tuple check in _store_assing
                for i in var.elts:
                    if isinstance(i, ast.Subscript):
                        name.append(i.value.id)
                    else:
                        name.append(i.id)
            else:
                name.append(var.id)

        except AttributeError:
            pass
        return name

    def _store_import(self, node, name, import_from=False):
        if self.library:
            name = f"{self.library}.{name}"
        if not name in self.import_dict.keys():
            self.import_dict[name] = []
        self.import_dict[name].append(templates.ImportTemplate(
            name,
            node.lineno,
            node,
            import_from=import_from
        ))

    def _store_assign(self, node):
        """
        Method to store assignments to global variable and constant
        variable dictionaries.

        TODO: Extend modification checks to dictionaries and sets
              now list is only data structure detected.
        """

        def _helper(var):
            names = []
            for name in self._get_names(var, names): # name must be str or int
                if name in self.global_dict.keys():
                    continue

                elif (var.col_offset == 0
                        or a_utils.get_parent(node, cnf.CLS_FUNC) is None):

                    if name in self._possible_constant_dict:
                        self.global_dict[name] = self._possible_constant_dict.pop(name, None)

                    # elif (isinstance(node.value, (ast.Constant, ast.Tuple))
                    #     or (isinstance(node.value, ast.Call)
                    #         and node.value.func.id == "tuple")):
                    #     # Also Constants e.g. int, str, float are marked as
                    #     # constant because they cannot be used within function
                    #     # without global or nonlocal keyword which are detected
                    #     # separately.
                    #     self._possible_constant_dict[name] = templates.GlobalTemplate(
                    #         name,
                    #         var.lineno,
                    #         var
                    #     )

                    else:
                        self._possible_constant_dict[name] = templates.GlobalTemplate(
                            name,
                            var.lineno,
                            var
                        )

                elif (isinstance(var, (ast.Subscript, ast.Attribute))
                        and name in self._possible_constant_dict):
                    self.global_dict[name] = self._possible_constant_dict.pop(name, None)

                elif (name in self._possible_constant_dict
                        and a_utils.get_parent(var, cnf.CLS_FUNC) is not None):
                    self.local_global_dict[name] = templates.NodeTemplate(
                        name,
                        var.lineno,
                        var
                    )

        # Actual function i.e. possible constant detection
        for var in node.targets[:]:
            # TODO make all assignment detection start with Tuple check and
            # then handle every elts like there would be only one assign
            if isinstance(var, ast.Tuple):
                for e in var.elts:
                    _helper(e)
            else:
                _helper(var)

    def _store_aug_assign(self, node):
        """
        Method to check if AugAssign node is in global scope and it uses
        existing variable (X) then the X is a global variable.
        """

        if (isinstance(node.target, ast.Attribute)
                and (name := node.target.value.id) in self._possible_constant_dict):
            self.global_dict[name] = self._possible_constant_dict.pop(name, None)
        elif ((node.col_offset == 0
             or a_utils.get_parent(node, cnf.CLS_FUNC) is None)
                and (name := node.target.id) in self._possible_constant_dict):
            # If we get here and variable used in AugAssign does not exist it
            # would be NameError when analysed code is executed.
            self.global_dict[name] = self._possible_constant_dict.pop(name, None)

    def _store_class(self, node):
        imported = False
        key = node.name
        parent = a_utils.get_parent(node, cnf.CLS_FUNC)
        if(parent):
            key = f"{parent.name}.{key}"
        if(self.library):
            key = f"{self.library}.{key}"
            imported = True
        self.class_dict[key] = templates.ClassTemplate(
            node.name,
            node.lineno,
            node,
            imported=imported
        )

    def _store_function(self, node):
        imported = False
        key = node.name
        pos_args = [i.arg for i in node.args.args]
        kw_args = [i.arg for i in node.args.kwonlyargs]

        parent = a_utils.get_parent(node, cnf.CLS_FUNC)
        if parent:
            key = f"{parent.name}.{key}"
        if self.library:
            key = f"{self.library}.{key}"
            imported = True
        #  TODO: If key exist then there are two identically named functions
        # in same scope
        # Could use similar list solution as with imports
        self.function_dict[key] = templates.FunctionTemplate(
            node.name,
            node.lineno,
            node,
            pos_args,
            kw_args,
            imported=imported
        )

    def _store_call(self, node):
        try:
            if (node.col_offset == 0
                    or a_utils.get_parent(node, cnf.CLS_FUNC) is None):
                self.call_dict[node.func.id] = templates.CallTemplate(
                    node.func.id,
                    node.lineno,
                    node
                )
        except AttributeError:
            pass

        # Detect modifications to (global) list(s) and dict(s), however because
        # type of variable is not checked sets (or anything calling methods
        # with same name) are be detected too.
        try:
            if ((name := node.func.value.id) in self._possible_constant_dict
                and (node.func.attr in self._list_mod_attrs
                    or node.func.attr in self._dict_mod_attrs)):
                self.global_dict[name] = self._possible_constant_dict.pop(name, None)
        except AttributeError:
            pass

        try:
            if node.func.id == "open" and isinstance(node.parent_node, ast.Assign):
                # If Call is open call e.g. filehandle = open("filename")
                for opened_file in node.parent_node.targets:
                    self.file_list.append(templates.FilehandleTemplate(
                        name=a_utils.get_attribute_name(opened_file),
                        lineno=opened_file.lineno,
                        astree=node # or node.parent_node?
                    ))
        except AttributeError:
            pass


   # ------------------------------------------------------------------------- #
   # Visits
    # Imports
    def visit_Import(self, node):
        for i in node.names:
            self._store_import(node, i.name, import_from=False)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self._store_import(node, node.module, import_from=True)
        self.generic_visit(node)

    # Assigns
    def visit_Assign(self, node):
        self._store_assign(node)
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        self._store_aug_assign(node)
        self.generic_visit(node)

    # Classes
    def visit_ClassDef(self, node):
        self._store_class(node)
        self.generic_visit(node)

    # Functions
    def visit_FunctionDef(self, node):
        self._store_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self._store_function(node)
        self.generic_visit(node)

    # Calls
    def visit_Call(self, node):
        self._store_call(node)
        self.generic_visit(node)
