"""Class file. Contains FileStructureAnalyser class."""
import ast

import src.analysers.analysis_utils as a_utils
import src.config.config as cnf

class FileStructureAnalyser(ast.NodeVisitor):
    """
    TODO:
    1. Identify lib and main files
    2. Count that there are >= 2 function in lib file
    """

   # ------------------------------------------------------------------------- #
   # Initialisations
    def __init__(self, model):
        self.model = model

   # ------------------------------------------------------------------------- #
   # General methods
    def check_info_comments(self, content, n=10):
        """
        Function to check the info comments at the beginning of the
        file. Beginning is n fist lines, default 10. Checked infos are:
        1. Author            ('Tekijä')
        2. Student number    ('Opiskelijanumero')
        3. Date              ('Päivämäärä')
        4. Co-operation      ('Yhteistyö')

        Currently does NOT check that they are in comments or docstring.
        """

        # file.__doc__ could be used to check docstring.
        # Could use regex to match 10 lines and find words from there.
        author = student_num = date = coop = all_found = False
        for line in content.split("\n", n)[:n]:
            # Could add error for each of missing words (then use regex)
            line = line.strip()
            if "Tekijä" in line:
                author = True
            elif "Opiskelijanumero" in line:
                student_num = True
            elif "Päivämäärä" in line:
                date = True
            elif "Yhteistyö" in line:
                coop = True

            if author and student_num and date and coop:
                all_found = True
                break

        self.model.add_msg("MR5", n, lineno=1, status=all_found)
        return None

    def has_main_function(self, tree):
        """
        TODO: change this to check of main level function calls
        """

        call_count = 0
        # TODO: Parse nested function names, which are in format parent.functionName
        fun_list = self.model.get_function_dict().keys()
        for node in tree.body:
            if hasattr(node, "value") and isinstance(node.value, ast.Call):
                call_count += 1
                try:
                    name = a_utils.get_attribute_name(node.value.func)
                    # TODO Call count could be replaced by model's call_dict()
                    # if call_dict would contain every call not just every
                    # unique call name.
                    if name in fun_list:
                        self.model.add_msg(
                            "MR2-3",
                            name,
                            call_count,
                            lineno=node.lineno,
                            status=(call_count <= 1)
                        )
                except AttributeError:
                    pass

                try:
                    # TODO: Check that node is not class which has the main
                    # function in it.
                    func = node.value.func
                    imported_library_call = False

                    try:
                        attr_name = a_utils.get_attribute_name(func, splitted=True)
                        if (attr_name[0] in cnf.ALLOWED_LIBRARIES_FOR_CONST
                                and attr_name[0] in self.model.get_import_dict()):
                            imported_library_call = True # E.g. random.random()
                    except AttributeError:
                        pass

                    self.model.add_msg(
                        "MR2-4",
                        a_utils.get_attribute_name(func),
                        lineno=node.lineno,
                        status=(
                            imported_library_call
                            or not isinstance(func, ast.Attribute)
                        )
                    )
                except AttributeError:
                    pass

    def check_duplicate_imports(self, import_dict):
        for value in import_dict.values():
            if len(value) <= 1: # Correctly done only 1 import per module
                self.model.add_msg(
                    "MR3-1" if value[0].import_from else "MR3",
                    value[0].name,
                    lineno=value[0].lineno,
                    status=True
                )
            else: # Too many imports i.e. incorrectly done (in course's context)
                for i in sorted(value, key=lambda elem: elem.lineno)[1:]:
                    ID = "MR3-1" if i.import_from else "MR3"
                    self.model.add_msg(
                        ID,
                        i.name,
                        lineno=i.lineno,
                        status=False
                    )
        return None

    def _check_import(self, node, lib_name, importFrom=False):
        """Method to check if import is not at global namespace."""

        self.model.add_msg(
            "MR4",
            lib_name,
            lineno=node.lineno,
            status=(a_utils.get_parent(node, cnf.CLS_FUNC) is None)
        )

   # ------------------------------------------------------------------------- #
   # Visits
    def visit_Import(self, node, *args, **kwargs):
        for i in node.names:
            self._check_import(node, i.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node, *args, **kwargs):
        self._check_import(node, node.module, importFrom=True)
        self.generic_visit(node)