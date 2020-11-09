"""Class file. Contains FileStructureAnalyser class."""
__version__ = "0.1.2"
__author__ = "RL"

import ast

import src.analysers.analysis_utils as a_utils

class FileStructureAnalyser(ast.NodeVisitor):
    """
    TODO:
    1. Identify lib and main files
    2. Count that there are >= 2 function in lib file
    """
   # Initialisations
    def __init__(self, model):
        self.model = model

   # General methods
    def check_info_comments(self, content, n=10, print_doc=False):
        """Function to check the info comments at the beginning of the
        file. Beginning is n fist lines, default 10. Checked infos are:
        1. Author            ('Tekijä')
        2. Student number    ('Opiskelijanumero')
        3. Date              ('Päivämäärä')
        4. Co-operation      ('Yhteistyö')

        Currently does NOT check that they are in comments or docstring.
        """
        # file.__doc__ could be used to check docstring.
        # Could use regex to match 10 lines and find words from there.

        author = student_no = date = coop = False
        for line in content.split("\n", n)[:n]:
            # Could add error for each of missing words (then use regex)
            line = line.strip()
            if("Tekijä" in line):
                author = True
            elif("Opiskelijanumero" in line):
                student_no = True
            elif("Päivämäärä" in line):
                date = True
            elif("Yhteistyö" in line):
                coop = True

            if(author and student_no and date and coop):
                break
        else:
            self.model.add_msg("MR5", n, lineno=1)

    def has_main_function(self, tree):  # TODO: change this to check of main level function calls
        """
        """
        call_count = 0
        # TODO: Parse nested function names, which are in format parent.functionName
        fun_list = self.model.get_function_dict().keys() 
        for node in tree.body:
            if(hasattr(node, "value") and isinstance(node.value, ast.Call)):
                call_count += 1
                try:
                    if(node.value.func.id in fun_list and call_count > 1):
                        self.model.add_msg("MR2-3", node.value.func.id, call_count, lineno=node.lineno)
                except AttributeError:
                    pass

                try:  # TODO: Check that node is not class which has the main function in it
                    if(isinstance(node.value.func, ast.Attribute)):
                        self.model.add_msg("MR2-4", node.value.func.value.id, node.value.func.attr, lineno=node.lineno)
                except AttributeError:
                    pass

    def check_duplicate_imports(self, import_dict):
        for value in import_dict.values():
            if(len(value) > 1):
                for i in sorted(value, key=lambda elem: elem.lineno)[1:]:
                    ID = "MR3-1" if(i.import_from) else "MR3"
                    self.model.add_msg(ID, i.name, lineno=i.lineno)

    def _check_import(self, node, lib_name, importFrom=False):
        # Check if import is not at global namespace
        if(a_utils.get_parent_instance(node, 
                (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) is not None):
            self.model.add_msg("MR4", lib_name, lineno=node.lineno)

   # Visits
    def visit_Import(self, node, *args, **kwargs):
        for i in node.names:
            self._check_import(node, i.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node, *args, **kwargs):
        self._check_import(node, node.module, importFrom=True)
        self.generic_visit(node)