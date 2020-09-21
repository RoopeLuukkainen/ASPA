"""Class file. Contains FileStructureAnalyser class."""
__version__ = "0.1.2"
__author__ = "RL"

import ast


import utils_lib

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

    def _check_import(self, node, lib_name, importFrom=False):
        # Check if same module is imported already
        if(lib_name in self.model.get_imported()):
            if(importFrom):
                self.model.add_msg("MR3-1", lib_name, lineno=node.lineno)
            else:
                self.model.add_msg("MR3", lib_name, lineno=node.lineno)
        else:
            self.model.set_imported(lib_name, add=True)
            # Check if current directory has imported file, i.e. it's local library file.
            if((lib_name + ".py") in self.model.get_file_list()):
                # self.model.lib_list.append(lib_name + ".py")
                self.model.set_lib_list(lib_name, append=True)

        # Check if import is not at global namespace
        if(utils_lib.get_parent_instance(node, 
                (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) is not None):
            self.model.add_msg("MR4", lib_name, lineno=node.lineno)

    def has_main_function(self, tree):
        """
        TODO:
        1. If current file has not imports to libfiles but has function
        call at the main level then it is possible main file.
        2. Also could check if this file is imported by others. If not
        Then it is probably main file."""
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

        if(call_count >= 1): # FIXME: NOW this gives main file if class is used globally obj = CLASS()
            return True
        return False

   # Visits
    def visit_Import(self, node, *args, **kwargs):
        self._check_import(node, str(node.names[0].name))
        self.generic_visit(node)

    def visit_ImportFrom(self, node, *args, **kwargs):
        self._check_import(node, str(node.module), importFrom=True)
        self.generic_visit(node)