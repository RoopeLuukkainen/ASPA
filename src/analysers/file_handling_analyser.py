"""Class file. Contains FileHandlingAnalyser class."""
import ast

import src.analysers.analysis_utils as a_utils
import src.config.config as cnf
import src.config.templates as templates

class FileHandlingAnalyser(ast.NodeVisitor):
   # ------------------------------------------------------------------------- #
   # Initialisation
    def __init__(self, model):
        self.model = model
        self.file_operations = {
            "read", "readline", "readlines", "write", "writelines",
        }

   # ------------------------------------------------------------------------- #
   # General methods
    def check_left_open_files(self, opened_files, closed_files):
        """Method to detect left open filehandles."""

        for closed in closed_files:
            try:
                closed_name = a_utils.get_attribute_name(closed)
            except AttributeError:
                continue

            temp = None
            for opened_obj in opened_files:
                if (closed_name == opened_obj.filehandle
                        and closed.lineno >= opened_obj.lineno
                        and a_utils.get_parent(opened_obj.astree, cnf.FUNC)
                        is a_utils.get_parent(closed, cnf.FUNC)):
                    # Lineno check is used to detect correct order when multiple
                    # filehandles have same name in same function. However, this
                    # can fail if opening and closing are e.g. in different
                    # conditional statement branches (and closing branch is
                    # before in line numbers), but then students structure is
                    # already questionable.
                    temp = opened_obj

            # After loop to find the last opened pair for closed filehandle.
            if temp:
                temp.set_closed(closed.lineno)

        for file_obj in opened_files:
            self.model.add_msg(
                "TK1",
                file_obj.name,
                lineno=file_obj.lineno,
                status=(file_obj.closed != 0)
            )

        return None

    def _has_open_and_close(self, node, func_handle, parent=cnf.FUNC):
        """Method to detect both, open() and close(), inside function
        and used for same filehandle as defined in "func_handle".

        Check has three return points:
        1. True if parent is with.
        2. True if same function contains open() and close() for same
           file handle as the "func_handle" parameter.
        3. False otherwise.
        """
        try:
            # Check usage of "with" keyword
            if a_utils.get_parent(node, ast.With) is not None:
                return True

            # Otherwise check function body
            func_node = a_utils.get_parent(node, parent)
            has_close = has_open = False

            # while (not has_open or not has_close) and (subnode := ast.walk(func_node)):
            for subnode in ast.walk(func_node):
                try:
                    if (not has_close
                        and isinstance(subnode, ast.Attribute)
                        and (subnode.attr == "close")
                        and (a_utils.get_attribute_name(
                                subnode,
                                omit_n_last=1
                            ) == func_handle)):
                        # When attribute is close and functionhandles have same name
                        # e.g. file_h.close()
                        has_close = True

                    elif (not has_open
                        and isinstance(subnode, ast.Assign)
                        and (subnode.value.func.id == "open")
                        and (a_utils.get_attribute_name(
                                subnode.targets[0]
                            ) == func_handle)):
                        # When filehandle is assigned for open()-call value.
                        has_open = True

                except AttributeError:
                    continue

                else:
                    if has_open and has_close:
                        return True

        except AttributeError:
            pass
        return False

    def _check_same_parent(self, node, attr, parent):
        """
        Method to detect that if filehandle is read/write inside
        function it is also opened and closed in same function.
        """

        func_handle = a_utils.get_attribute_name(node.value)
        self.model.add_msg(
            "TK2",
            func_handle,
            attr,
            lineno=node.lineno,
            status=self._has_open_and_close(node, func_handle, parent)
        )

    def _check_file_closing(self, node):
        self.model.set_files_closed(node.value, append=True)
        attr_name = a_utils.get_attribute_name(node.value)

        # TK1-2 closing file in except branch.
        self.model.add_msg(
            "TK1-2",
            attr_name,
            lineno=node.lineno,
            status=(a_utils.get_parent(node, ast.ExceptHandler) is None)
        )

        # TK1-3 close has not parenthesis i.e. close not close().
        self.model.add_msg(
            "TK1-3",
            attr_name,
            "close",
            lineno=node.lineno,
            status=(a_utils.get_parent(
                node,
                ast.Call,
                denied=(ast.Expr,)) is not None
            )
        )
        return None


   # ------------------------------------------------------------------------- #
   # Visits
    def visit_Attribute(self, node, *args, **kwargs):
        """Method to check if node is:
        1. Closing a file.
        2. Closing a file in except branch.
        """

        try:
            if node.attr == "close":
                self._check_file_closing(node)
        except AttributeError:
            pass

        try:
            # node.attr should work even for changed a.b.c.read() attributes.
            if node.attr in self.file_operations:
                self._check_same_parent(node, node.attr, cnf.FUNC)
        except AttributeError:
            pass

        self.generic_visit(node)


    def visit_With(self, node, *args, **kwargs):
        # TODO Make BKT compatible by changing check in the normal open.
        try:
            for i in node.items:
                if i.context_expr.func.id == "open":
                    self.model.add_msg("TK1-1", "with open", lineno=node.lineno)
        except AttributeError:
            pass
        self.generic_visit(node)