"""Class file. Contains DataStructureAnalyser class."""
import ast

import src.analysers.analysis_utils as au
import src.config.config as cnf
import src.config.templates as templates

class DataStructureAnalyser(ast.NodeVisitor):
   # Initialisations
    def __init__(self, model):
        self.model = model
        self._local_objects = {}
        self._list_addition_attributes = {"append", "extend", "insert"}

   # General methods
    def _detect_objects(self, tree):
        _objects = []

        classes = self.model.get_class_dict().keys()
        parent = tree.name

        # Linenumber are positive therefore this inactivate skip
        skip_end = -1
        for node in ast.walk(tree):

            # Used to skip nested functions and classes
            try:
                if(skip_end >= node.lineno):
                    continue
                elif(isinstance(node, cnf.CLS_FUNC) and node is not tree):
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
                        # _objects.append(au.get_attribute_name(i))
                        # print(1)
                        # print(ast.dump(i, include_attributes=True), node.lineno)
                        _objects.append(
                            templates.ObjectTemplate(
                                au.get_attribute_name(i),
                                node.lineno,
                                i
                            )
                        )
                        # print()
            except AttributeError:
                pass

        self._local_objects[tree] = _objects
        return None

    def _get_local_object_names(self, func=None):
        """
        Method to return names of the objects within given function. If
        no func-argument is given search objects from every function.

        Names are returned as a list of strings.
        """
        names = []
        if(func):
            for i in self._local_objects[func]:
                names.append(i.name)
        else:
            for value in self._local_objects.values():
                for i in value:
                    names.append(i.name)
        return names

    def _get_object_by_name(self, obj_name, func=None):
        """
        Method to return the first object with given name obj_name. If
        func-argument is given search objects only from that function.
        """
        obj = None
        if(func):
            for i in self._local_objects[func]:
                if(i.name == obj_name):
                    obj = i
                    break
        else:
            for value in self._local_objects.values():
                for i in value:
                    if(i.name == obj_name):
                        obj = i
                        break
        return obj

   # Visits
    def visit_Assign(self, node, *args, **kwargs):
        """Method to find:
        1. Direct usage of CLASS variables via class itself.
        2. Assiging CLASS to variable, i.e. object = CLASS <without parenthesis>
        3. Object creation outside a loop and object (attribute) values
           are assigned inside the loop and then object is put into a
           list.
        """
        classes = self.model.get_class_dict().keys()

        # Using class directly without an object
        # NOTE: identical to detection AR-7, i.e. assigning attribute to function.
        try:
            for var in node.targets[:]:
                name = au.get_attribute_name(var, splitted=True)
                if(isinstance(var, ast.Attribute) and name[0] in classes):
                    self.model.add_msg("TR2-1", ".".join(name), lineno=var.lineno)
        except AttributeError:
            pass

        # Object creation without parenthesis, work when assigned value
        # i.e. node.value is class name.
        try:
            name = au.get_attribute_name(node.value)
            parent = au.get_parent(node, cnf.CLS_FUNC)

            if(name in classes or f"{parent.name}.{name}" in classes):
                self.model.add_msg("TR2-2", name, lineno=node.lineno)
        except AttributeError:
            pass

        # Object creation outside a loop and object (attribute) values
        # are assigned inside the loop and then object is put into a
        # list.
        for i in node.targets:
            try:
                # Check if value is assigned to an object (or other attribute)
                if(not isinstance(i, ast.Attribute)):
                    continue

                loop = au.get_parent(node, cnf.LOOP)

                # Check if assign is inside a loop, if not no other
                # target can be inside a loop either.
                if(not loop):
                    break

                func = au.get_parent(node, cnf.FUNC)
                name_list = au.get_attribute_name(i, splitted=True)
                obj = self._get_object_by_name(".".join(name_list[:-1]), func)
                loop2 = au.get_parent(obj.astree, cnf.LOOP)

                # Check if the object is created in same function as
                # value is assigned to its attribute but creation is not
                # in the same loop.
                if(not obj or (loop2 == loop)):
                    continue

                # TODO: This is now done everytime object attribute is
                # assigned inside loop. Optimize this such that objects
                # are first gathered and then only one walk to check all
                # of them.
                for elem in ast.walk(loop):
                    try:
                        if((obj.name == au.get_attribute_name(elem))
                            and au.is_added_to_data_structure(
                                elem,
                                ast.List,
                                "list",
                                self._list_addition_attributes
                            )
                        ):
                            self.model.add_msg("TR3-2", lineno=obj.lineno)
                    except AttributeError:
                        pass
            except AttributeError:
                pass

        self.generic_visit(node)

    def visit_ClassDef(self, node, *args, **kwargs):
        """Method to check
        1. Class is created in global scope
        """
        # Col offset should detect every class definition which is indended
        if(node.col_offset > 0
                or au.get_parent(node, cnf.CLS_FUNC) is not None):
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
        """Method to check
        1. Object attributes are added into a list inside a loop.
        """

        # The check of adding object's attribute to the list is only done when
        # it is done inside a loop
        if(au.get_parent(node, cnf.LOOP)):
            func = au.get_parent(node, cnf.FUNC)
            try:
                name = au.get_attribute_name(node.value)

                if(name in self._get_local_object_names(func)
                    and au.is_added_to_data_structure(
                        node,
                        ast.List,
                        "list",
                        self._list_addition_attributes
                    )
                ):
                    self.model.add_msg("TR3-1", lineno=node.lineno)
            except (AttributeError, KeyError):
                pass

        self.generic_visit(node)
