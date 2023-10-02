"""Class file. Contains ExceptionHandlingAnalyser class."""

import ast

import src.analysers.analysis_utils as a_utils
import src.config.config as cnf

class ExceptionHandlingAnalyser(ast.NodeVisitor):
   # ------------------------------------------------------------------------- #
   # Initialisation
    def __init__(self, model):
        self.model = model
        self.file_operations = {
            "read", "readline", "readlines", "write", "writelines",
        }
        self.allowed_exception_types = cnf.ALLOWED_EXCEPTION_TYPES

   # Getters

   # ------------------------------------------------------------------------- #
   # Setters

   # ------------------------------------------------------------------------- #
   # General methods
    def _has_exception_handling(self, node, denied=cnf.FUNC):
        """Check to determine if node is inside exception handling."""

        if a_utils.get_parent(node, ast.Try, denied=denied) is None:
            return False
        return True

    def _check_exception_handling(self, node):
        """
        Method to check if node has:
        1. Missing try - except around file opening.
        """

        try:
            if node.func.id == "open":
                self.model.add_msg(
                    "PK3",
                    lineno=node.lineno,
                    status=self._has_exception_handling(node)
                )
        except AttributeError:
            pass

    def _check_exception_handlers(self, node):
        """
        Method to check if node is:
        1. Try with no exception branches
        2. Exception branch missing an error type. Excluding the last
            exception IF there are more than one exception branches.

        ast.Try has lists for each branchtype: handlers=[], orelse=[],
        finalbody=[], which are for excepts, else and finally,
        respectively

        Does not analyse
        1. finally branches
        2. else branches
        """

        try:
            self.model.add_msg(
                code="PK1",
                status=(len(node.handlers) >= 1),
                lineno=node.lineno
            )

            for handler in node.handlers:  # handler is ast.ExceptHandler object
                self.model.add_msg(
                    code="PK1-1",
                    status=(handler.type != None),
                    lineno=handler.lineno
                )

        except AttributeError:
            # print(f"Error at line: {node.lineno}, node: {node}, e: {e}") # Debug
            pass

    def _check_exception_type(self, node):
        """
        Method to check if used exception type is Exception.
        """

        try:
            temp = []
            for handler in node.handlers:
                if isinstance(handler.type, ast.Tuple):
                    for i in handler.type.elts:
                        temp.append(i)
                else:
                    temp.append(handler.type)

            for i in temp:
                self.model.add_msg(
                    code="PK1-2",
                    status=(a_utils.get_attribute_name(i) in self.allowed_exception_types),
                    lineno=i.lineno
                )
            temp.clear()

        except AttributeError:
            pass
        return None

   # ------------------------------------------------------------------------- #
   # Visits
    def visit_Try(self, node, *args, **kwargs):
        """Method to visit Try nodes."""

        self._check_exception_handlers(node)
        self._check_exception_type(node)
        self.generic_visit(node)

    def visit_Call(self, node, *args, **kwargs):
        """Method to visit (function) Call nodes."""

        self._check_exception_handling(node)
        self.generic_visit(node)

    def visit_Attribute(self, node, *args, **kwargs):
        """
        Method to check if node is:
        1. Missing try - except around file.read().
        2. Missing try - except around file.readline().
        3. Missing try - except around file.readlines().
        4. Missing try - except around file.write().
        5. Missing try - except around file.writelines().
        6. Missing try - except around file.close().
        """

        try:
            if node.attr in self.file_operations:
                self.model.add_msg(
                    "PK4",
                    a_utils.get_attribute_name(node),
                    lineno=node.lineno,
                    status=self._has_exception_handling(node)
                )
            elif node.attr == "close":
                self.model.add_msg(
                    "PK5",
                    a_utils.get_attribute_name(node),
                    lineno=node.lineno,
                    status=self._has_exception_handling(node)
                )

        except AttributeError:
            pass
        self.generic_visit(node)

    def visit_For(self, node, *args, **kwargs):
        """
        Method to check if node is:
        1. For loop reading a file AND missing exception handling.
        """

        try:
            names = [i.filehandle for i in self.model.get_files_opened()]
            # TODO: add check that file is opened in same function

            iter_name = ""
            if isinstance(node.iter, (ast.Name, ast.Attribute)):
                iter_name = a_utils.get_attribute_name(node.iter)

            # Special case for 'for ... in enumerate(filehandle)'
            # Only works if there is one call, not call inside calls
            elif isinstance(node.iter, ast.Call) and node.iter.func.id == "enumerate":
                iter_name = a_utils.get_attribute_name(node.iter.args[0])

            if iter_name in names:
                try:
                    msg_arg = f"for {node.target.id} in {iter_name}"
                except AttributeError:
                    msg_arg = f"for ... in ..."
                finally:
                    self.model.add_msg(
                        "PK4-1",
                        msg_arg,
                        lineno=node.lineno,
                        status=self._has_exception_handling(node)
                    )

        except (AttributeError, TypeError):
            pass
        self.generic_visit(node)
