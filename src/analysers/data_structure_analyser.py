"""Class file. Contains DataStructureAnalyser class."""
import ast
import copy

import src.analysers.analysis_utils as a_utils

class DataStructureAnalyser(ast.NodeVisitor):
   # Initialisations
    def __init__(self, model):
        self.model = model
        self._local_objects = dict()
        self._list_addition_attributes = {"append", "extend", "insert"}

   # General methods
    def _detect_objects(self, tree):
        _objects = list()

        classes = self.model.get_class_dict().keys()
        parent = tree.name

        # temp_tree = copy.deepcopy(tree)

        # Linenumber are positive therefore this inactivate skip
        skip_end = -1
        for node in ast.walk(tree):

            # Used to skip nested functions and classes
            try:
                if(skip_end >= node.lineno):
                    continue
                elif(isinstance(node,
                        (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
                        and node is not tree):
                    skip_end = node.end_lineno
                    continue
            except AttributeError:
                continue

            # Object detection
            try:
                name = node.value.func.id
                if(isinstance(node, ast.Assign)
                    and ((name in classes)
                        or (f"{parent}.{name}" in classes))):

                    for i in node.targets:
                        _objects.append(a_utils.get_attribute_name(i))
            except AttributeError:
                pass

        self._local_objects[tree] = _objects
        return None

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

    def visit_FunctionDef(self, node, *args, **kwargs):
        """Method to call detect objects for current namespace."""
        self._detect_objects(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node, *args, **kwargs):
        """Method to call detect objects for current namespace."""
        self._detect_objects(node)
        self.generic_visit(node)

    def visit_Attribute(self, node, *args, **kwargs):
        """
        """

        # The check of adding object's attribute to the list is only done when
        # it is done inside a loop
        if(a_utils.get_parent_instance(node, (ast.While, ast.For))):
            func = a_utils.get_parent_instance(node,
                    (ast.FunctionDef, ast.AsyncFunctionDef))
            try:
                name = a_utils.get_attribute_name(node.value)
                if(name in self._local_objects[func]):
                    parent = a_utils.get_parent_instance(node, (ast.List, ast.Call))

                    # This detect list_name += [...] and list_name = list_name + [...]
                    # and cases with extend where list_name.extend([...])
                    if(isinstance(parent, ast.List)):
                        self.model.add_msg("TR3-1", lineno=node.lineno)

                    # This detect list_name.append() and list_name.insert()
                    # and in some cases list_name.extend()
                    elif(isinstance(parent, ast.Call)
                            and isinstance(parent.func, (ast.Attribute))
                            and parent.func.attr in self._list_addition_attributes):
                        self.model.add_msg("TR3-1", lineno=node.lineno)

                    #  This detect all cases inside list(...)-call
                    elif(isinstance(parent, ast.Call) and parent.func.id == "list"):
                        self.model.add_msg("TR3-1", lineno=node.lineno)

            except (AttributeError, KeyError):
                pass

        self.generic_visit(node)
