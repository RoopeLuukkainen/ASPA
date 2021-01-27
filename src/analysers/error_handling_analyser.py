"""Class file. Contains ErrorHandlingAnalyser class."""
import ast

import src.analysers.analysis_utils as a_utils
import src.analysers.ast_checks as ac

class ErrorHandlingAnalyser(ast.NodeVisitor):
    # Initialisation
    def __init__(self, model):
        self.model = model
        self.BKTA = model.settings["BKT_analysis"]
        self.file_operations = {"read", "readline", "readlines", "write", "writelines"}
   # Getters

   # Setters

   # General methods

   # Visits
    def visit_Try(self, node, *args, **kwargs):
        """Method to check if node is:
        1. Try with only one exception branch
        2. Exception branch missing an error type. Excluding the last
            exception IF there are more than one exception branches.

        ast.Try has lists for each branchtype: handlers=[], orelse=[], finalbody=[],
        which are for excepts, else and finally, respectively

        Does not analyse
        1. finally branches
        2. else branches
        """
        try:
            if(not node.handlers):
                pass
            elif(len(node.handlers) < 2):
                self.model.add_msg("PK1", lineno=node.lineno)
                # TODO: THIS IS SAME check as "i.type == None" below, improve somehow
                if(node.handlers[0].type == None):
                    self.model.add_msg("PK1-1", lineno=node.handlers[0].lineno)
            else:
                for i in node.handlers[:-1]:
                    if(i.type == None):
                        self.model.add_msg("PK1-1", lineno=i.lineno)
        except Exception:
        #     print(f"Error at line: {node.lineno}, node: {node}") # Debug
            pass

        self.generic_visit(node)

    def visit_Call(self, node, *args, **kwargs):
        """Method to check if node is:
        1. Missing try - except around file opening.
        """
        try:
            if node.func.id == "open":
                if not ac.has_exception_handling(node):
                    self.model.add_msg("PK3", lineno=node.lineno)
                elif self.BKTA:
                    pass
                    # File opening has correct exception handling
        except AttributeError:
            pass

        self.generic_visit(node)

    def visit_Attribute(self, node, *args, **kwargs):
        """Method to check if node is:
        1. Missing try - except around file.read().
        2. Missing try - except around file.readline().
        3. Missing try - except around file.readlines().
        4. Missing try - except around file.write().
        5. Missing try - except around file.writelines().
        """

        try:
            if(node.attr in self.file_operations
                    and a_utils.get_parent(node, ast.Try,
                    denied=(ast.FunctionDef, ast.AsyncFunctionDef)) is None):
                self.model.add_msg(
                    "PK4",
                    a_utils.get_attribute_name(node),
                    lineno=node.lineno
                )
        except AttributeError:
            pass
        self.generic_visit(node)

    def visit_For(self, node, *args, **kwargs):
        try:
            names = [a_utils.get_attribute_name(i) for i in self.model.get_files_opened()]
            # TODO: add check that file is opened in same function

            iter_name = ""
            if(isinstance(node.iter, (ast.Name, ast.Attribute))):
                iter_name = a_utils.get_attribute_name(node.iter)

            # Special case for 'for ... in enumerate(filehandle)'
            # Only works if there is one call, not call inside calls
            elif(isinstance(node.iter, ast.Call) and node.iter.func.id == "enumerate"):
                iter_name = a_utils.get_attribute_name(node.iter.args[0])

            if(iter_name in names
                    and a_utils.get_parent(node, ast.Try,
                    denied=(ast.FunctionDef, ast.AsyncFunctionDef)) is None):
                try:
                    self.model.add_msg("PK4", f"for {node.target.id} in {iter_name}", lineno=node.lineno)
                except AttributeError:
                    self.model.add_msg("PK4", f"for ... in ...", lineno=node.lineno)

        except (AttributeError, TypeError):
            pass
        self.generic_visit(node)
