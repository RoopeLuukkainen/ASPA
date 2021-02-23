"""Class file. Contains DataStructureAnalyser class."""
import ast

import src.analysers.analysis_utils as a_utils
import src.config.config as cnf
import src.config.templates as templates

class DataStructureAnalyser(ast.NodeVisitor):
   # ------------------------------------------------------------------------- #
   # Initialisations
    def __init__(self, model):
        self.model = model
        self._local_objects = {}
        self._list_addition_attributes = {"append", "extend", "insert"}


   # ------------------------------------------------------------------------- #
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
                if skip_end >= node.lineno:
                    continue
                elif isinstance(node, cnf.CLS_FUNC) and node is not tree:
                    skip_end = node.end_lineno
                    continue
            except AttributeError:
                continue

            # Object detection
            try:
                name = node.value.func.id
                if (isinstance(node, ast.Assign)
                    and ((name in classes)
                        or (f"{parent}.{name}" in classes))
                ):
                    for i in node.targets:
                        _objects.append(
                            templates.ObjectTemplate(
                                a_utils.get_attribute_name(i),
                                node.lineno,
                                i
                            )
                        )
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
        if func:
            for i in self._local_objects[func]:
                if i.name == obj_name:
                    obj = i
                    break
        else:
            for value in self._local_objects.values():
                for i in value:
                    if i.name == obj_name:
                        obj = i
                        # NOTE: using break instead of return would allow same
                        # object from different function to be returned,
                        # therefore it would not be the first object.
                        return obj
        return obj

    def _check_object_outside_loop(self, node, assing_loop):
        """
        Method to check if object creation is outside a loop and object
        (attribute) values are assigned inside the loop and then object
        is put into a list.
        """

        # Get the function where object is created, if there is no parent
        # function, func is None and all the objects are searched in later step.
        func = a_utils.get_parent(node, cnf.FUNC)

        for var in node.targets:
            try:
                # Check that value is assigned to an object (or other attribute)
                # If not, it is irrelevant var for this check and we continue.
                if not isinstance(var, ast.Attribute):
                    continue

                # Get an object and a loop where values are assigned to object's
                # attributes.
                name = a_utils.get_attribute_name(var, omit_n_last=1)
                if not (obj := self._get_object_by_name(name, func)):
                    continue
                creation_loop = a_utils.get_parent(obj.astree, cnf.LOOP)

                # TODO: This is now done everytime object attribute is assigned
                # inside a loop. Optimize this such that objects are first
                # gathered and then only one walk to check all of them.
                for elem in ast.walk(assing_loop):
                    try:
                        if ((obj.name == a_utils.get_attribute_name(elem))
                            and a_utils.is_added_to_data_structure(
                                elem,
                                ast.List,
                                "list",
                                self._list_addition_attributes
                            )
                        ):
                        # 'status' tells if creation of object is in the same
                        # loop as value is assigned to the attribute. If yes no
                        # violation.
                            self.model.add_msg(
                                "TR3-2",
                                lineno=obj.lineno,
                                status=(creation_loop == assing_loop)
                            )
                    except AttributeError:
                        continue
            except AttributeError:
                pass
        return None

    def _is_class_call(self, node, parent, classes):
        """
        Method to check if node is a call of a class.

        Arguments:
        node: node itself usually Name node which is e.g. in Assign
                nodes value.
        parent: can be name of a class, function or imported module,
                which is parent of the node.
        classes: is list dict_keys() of class names. If class has parent
                it is included into a name 'parent.class_name'.

        Three different return values:
         0: No class name and not a call, i.e. something not relevant.
         1: Class name and call, e.g. obj = CLASS()
        -1: Class name but not a call, e.g. obj = CLASS
        """

        _IRRELEVANT = 0
        _CLASS_CALL = 1
        _CALL_WITHOUT_PARENTHESIS = -1

        is_call = False
        try:
            if (temp := a_utils.get_parent(
                    node,
                    ast.Call,
                    denied=(ast.Assign,) + cnf.CLS_FUNC)):
                # There is a Call node as a parent
                is_call = True
                name = a_utils.get_class_name(temp)

            elif (temp := a_utils.get_outer_parent(
                    node,
                    ast.Attribute,
                    denied=(ast.Assign, ast.Call) + cnf.CLS_FUNC)):
                # There is one or more Attribute nodes as parents
                name = a_utils.get_attribute_name(temp)

            else:
                name = a_utils.get_attribute_name(node)

            if (name in classes) or (f"{parent.name}.{name}" in classes):
                if is_call:
                    return _CLASS_CALL
                else:
                    return _CALL_WITHOUT_PARENTHESIS

        except AttributeError:
            pass

        return _IRRELEVANT


   # ------------------------------------------------------------------------- #
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
                name = a_utils.get_attribute_name(var, splitted=True)
                # TODO change check such that when attribute is used via object
                # it is fine and when it is used via class (this now detects
                # this case) it is not fine.
                if isinstance(var, ast.Attribute) and (name[0] in classes):
                    self.model.add_msg("TR2-1", ".".join(name), lineno=var.lineno)
        except AttributeError:
            pass

        # Check if assigning value to object attribute is inside a loop,
        # if not, no other target can be inside a loop either.
        if (loop := a_utils.get_parent(node, cnf.LOOP)):
            self._check_object_outside_loop(node, loop)

        self.generic_visit(node)

    def _check_class(self, node):
        """
        Method to check
        1. Class is created in global scope
        2. Class name is written with UPPERCASE letters.
        """

        name = node.name

       # Class is at global scope check
        # Col offset should detect every class definition which is indended
        # but status is verified with parent check.
        self.model.add_msg(
            "TR2-3",
            name,
            lineno=node.lineno,
            status=(
                node.col_offset == 0
                or a_utils.get_parent(node, cnf.CLS_FUNC) is None
            )
        )

       # Class name is UPPERCASE check
        self.model.add_msg(
            "TR2-4",
            name,
            lineno=node.lineno,
            status=(name.isupper())
        )

    def visit_ClassDef(self, node, *args, **kwargs):
        """Method to call class checks of ClassDef nodes."""

        self._check_class(node)
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
        if a_utils.get_parent(node, cnf.LOOP):
            func = a_utils.get_parent(node, cnf.FUNC)
            try:
                name = a_utils.get_attribute_name(node.value)

                if (name in self._get_local_object_names(func)
                    and a_utils.is_added_to_data_structure(
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


    def visit_Name(self, node, *args, **kwargs):
        # Object creation without parenthesis, work when assigned value
        # i.e. node.id is class name.
        classes = self.model.get_class_dict().keys()

        try:
            parent = a_utils.get_parent(node, cnf.CLS_FUNC)

            if (temp := self._is_class_call(node, parent, classes)):
                self.model.add_msg(
                    "TR2-2",
                    node.id,
                    lineno=node.lineno,
                    status=(temp > 0) # -1 means class call without parenthesis
                )
        except AttributeError:
            pass
        self.generic_visit(node)