"""File to handle ASPA static analysers."""

import ast
import datetime  # for timestamp
import os

# Utility libraries
from ..config import config as cnf
from ..config import templates
import src.utils_lib as utils
import src.analysers.analysis_utils as a_utils

# AST analysers
import src.analysers.pre_analyser as pre_analyser
import src.analysers.data_structure_analyser as data_structure_analyser
import src.analysers.error_handling_analyser as error_handling_analyser
import src.analysers.basic_command_analyser as basic_command_analyser
import src.analysers.file_handling_analyser as file_handling_analyser
import src.analysers.file_structure_analyser as file_structure_analyser
import src.analysers.function_analyser as function_analyser

# BKT analyser
import src.BKT.BKT_analyser as BKT_A

class Model:
    def __init__(self, controller):
        self.controller = controller
        self.settings = self.controller.get_settings()
        self.violation_occurances = {}
        self.BKT_temp = [] # TEMP

        try:
            self.language = self.settings["language"]
        except KeyError:  # This should not be possible if defaults settings are not changed
            self.language = "FIN"
            self.controller.propagate_error_message("NO_LANGUAGE")

        try:
            self.checkbox_options = self.settings["checkbox_options"]
        except KeyError:   # This should not be possible if defaults settings are not changed
            # These could be in utils not in settings
            self.checkbox_options = [
                "basic",
                "function",
                "file_handling",
                "data_structure",
                "library",
                "exception_handling"
            ]
        # There is possibility that there are no 6 elements in checkbox options,
        # but that is modified in the code then, i.e. not by user
        try:
            self.analysers = {
                self.checkbox_options[0]: basic_command_analyser.BasicsAnalyser(self),
                self.checkbox_options[1]: function_analyser.FunctionAnalyser(self),
                self.checkbox_options[2]: file_handling_analyser.FileHandlingAnalyser(self),
                self.checkbox_options[3]: data_structure_analyser.DataStructureAnalyser(self),
                self.checkbox_options[4]: file_structure_analyser.FileStructureAnalyser(self),
                self.checkbox_options[5]: error_handling_analyser.ErrorHandlingAnalyser(self)
            }
        except IndexError:
            pass
        # Pre analyser
        self.pre_analyser = pre_analyser.PreAnalyser()
        self.constant_variables = {}

        # Variable data structures (used by function_analyser)
        self.global_variables = {}
        self.local_variables = set()
        self.call_dict = {}

        # File handling (used by file_handling_analyser)
        self.files_opened = []
        self.files_closed =  []

        # File structure list and dict used by file_structure_analyser
        # and data_structure_analyser
        self.function_dict = {}
        self.class_dict = {}

        # File structure lists used by file_structure_analyser
        self.file_list = []
        self.lib_list = []
        self.import_dict = {}

        # Messages
        self.messages = []
        self.all_messages = []

   # Datastructure getters
    def get_call_dict(self):
        return dict(self.call_dict)

    def get_global_variables(self):
        return dict(self.global_variables)

    def get_local_variables(self):
        return set(self.local_variables)

    def get_import_dict(self):
        return dict(self.import_dict)

    def get_files_opened(self):
        return list(self.files_opened)

    def get_files_closed(self):
        return list(self.files_closed)

    def get_messages(self):
        return list(self.messages)

    def get_file_list(self):
        return list(self.file_list)

    def get_lib_list(self):
        return list(self.lib_list)

    def get_function_dict(self):
        return dict(self.function_dict)

    def get_class_dict(self):
        return dict(self.class_dict)


   # List, dict and set setters
    # def set_global_variables(self, value, add=False):
    #     if(add):
    #         self.global_variables.add(value)
    #     else:
    #         self.global_variables = set(value)

    def set_call_dict(self, value, key=None):
        if(key):
            self.call_dict[key] = value
        else:
            self.call_dict = dict(value)

    def set_global_variables(self, value, key=None):
        if(key):
            self.global_variables[key] = value
        else:
            self.global_variables = dict(value)

    def set_local_variables(self, value, add=False):
        if(add):
            self.local_variables.add(value)
        else:
            self.local_variables = set(value)

    def set_files_opened(self, value, append=False):
        if(append):
            self.files_opened.append(value)
        else:
            self.files_opened = list(value)

    def set_files_closed(self, value, append=False):
        if(append):
            self.files_closed.append(value)
        else:
            self.files_closed = list(value)

    def set_file_list(self, value):
        self.file_list = list(value)

    def set_import_dict(self, value, key=None):
        if(key):
            self.import_dict[key] = value
        else:
            self.import_dict = dict(value)

    def set_function_dict(self, value, key=None):
        if(key):
            self.function_dict[key] = value
        else:
            self.function_dict = dict(value)

    def set_class_dict(self, value):
        self.class_dict = dict(value)

    def set_lib_list(self, value, append=False):
        if(append):
            self.lib_list.append(value)
        else:
            self.lib_list = list(value)

   # General methods
    def clear_analysis_data(self):
        self.all_messages.clear()
        self.global_variables.clear()
        self.local_variables.clear()
        self.files_opened.clear()
        self.files_closed.clear()
        self.function_dict.clear()
        self.class_dict.clear()
        self.file_list.clear()
        self.lib_list.clear()
        self.import_dict.clear()
        self.call_dict.clear()
        self.constant_variables.clear() # Not yet used but cleared anyway
        self.BKT_temp.clear() # TEMP

    def add_msg(self, code, *args, lineno=-1, status=False):
        if not utils.ignore_check(code):

            obj = templates.ViolationTemplate(code, args, lineno, status)
            self.BKT_temp.append(obj) # TEMP

            # TODO utilise obj in messages list, similarly as with BKT_temp
            if status == False:
                self.messages.append((lineno, code, args))

            try:
                self.violation_occurances[code] += 1
            except KeyError:
                self.violation_occurances[code] = 1
        # print("m", self.messages)

    def save_messages(self, title):
        # if(len(self.messages) == 0):
        #     self.add_msg("OK")
        self.all_messages.append((title, tuple(self.messages)))
        self.messages.clear()

    def default_analyse(self, selections, file_list, result_page, *args, **kwargs):
        """
        Method to handle default analysis steps where coding convention
        violations are detected. This includes:
        1. Initialising result file.
        2. Iterating analysed files.
        3. Formating each file's results
        4. Showing results.
        5. Clearing results.
        """

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        utils.write_file(self.settings["result_path"], timestamp + "\n")

        for filepath in file_list:
            results = self.execute_analysis(filepath, selections)

            # Format results
            formated_results = self.format_results(
                filepath.filename,
                str(filepath.path),
                results
            )

            # Show results and clear results
            result_page.show_results(formated_results)
            self.clear_analysis_data()
            formated_results.clear()
        return None

    def BKT_analyse(self, selections, file_dict, *args, **kwargs):
        """
        Method to control Bayesian Knowledge Tracing analysis steps.
        This includes:
        1. Initialising result file.
        2. Iterating analysed files.
        3. Showing results.
        4. Clearing results.
        """

        # Create indexes for titles and sort them from A to Z (ascending order).
        # TODO add setting which allow sorting by selected value
        BKT_title_sorted = sorted(cnf.BKT_TITLES[self.language].keys())
        BKT_index = {}
        for i, title in enumerate(BKT_title_sorted):
            BKT_index[title] = i

        # Initialise result file with title line
        # TODO add setting for cell separator
        BKT_result_path = self.settings["BKT_path"]
        title_line = "{0:s};{1:s}\n".format(
                cnf.BKT_TEXT[self.language]["student_name"],
                ";".join(BKT_title_sorted)
            )
        utils.write_file(BKT_result_path, title_line, mode="w")

        # Initialise content lines
        content_lines = []
        initial_line = [0] * len(BKT_title_sorted)

        # BKT analyse all files in given paths
        for student_name, filepaths in file_dict.items():
            student = BKT_A.Student(student_name)

            for filepath in filepaths:
                results = self.execute_analysis(filepath, selections)

                for i in self.BKT_temp: # FIX change BKT_temp to results
                    # print(i.lineno, i.vid, i.status)
                    student.add_result(i.vid, int(i.status))
                self.BKT_temp.clear()
                self.clear_analysis_data()


            result_line = initial_line[:] # copy
            for key, result in student.get_results().items():
                try:
                    # TODO add setting for decimal places
                    # TODO add setting for decimal separator (default is now .)
                    result_line[BKT_index[key]] = round(result.Ln, 3)
                except KeyError:
                    pass
                except IndexError:
                    pass
            # Add student results to (file) content_lines -list
            content_lines.append(
                f"{student.student_id};{';'.join(map(str, result_line))}"
            )

            # Write results to BKT result file
            utils.write_file(
                BKT_result_path,
                "\n".join(content_lines) + "\n",
                mode="a"
            )

            # Clear written results
            result_line.clear()
            content_lines.clear()

        # Clear created data structures
        initial_line.clear()
        BKT_index.clear()
        BKT_title_sorted.clear()

        return None

    def execute_analysis(self, filepath, selections):
        """
        Method to handle analysis execution steps:
        1. Reading file.
        2. Parsing AST from file.
        3. Calling AST analyser.
        4. Returning results.

        Return: List of tuples, where tuples include result messages.
        """

        content = utils.read_file(filepath.path)
        filename = filepath.filename
        dir_path = filepath.path.parent

        # No check for tree being None etc. before analysis because analyses
        # will create violation if tree is not valid. Only in dumping checks
        # if tree exist.
        tree = self.parse_ast(content, filename)

        # Dump tree
        if(tree and self.settings["dump_tree"]):
            self.dump_tree(tree)

        # Call analyser
        results = self.analyse(
            tree,
            content,
            dir_path,
            filename,
            selections
        )
        return results

    def parse_ast(self, content, filename, create_msg=True):
        """
        Creates an abstract syntax tree and adds both parent and sibling
        nodes.

        Return: Python ast typed tree or None if parse fails.
        """
        tree = None
        try:
            tree = ast.parse(content, filename)

        except SyntaxError:
            if create_msg:
                self.add_msg("syntax_error")
                self.save_messages("file_error")

        # When content is not str or AST (e.g. None), usually due failed
        # file reading.
        except TypeError:
            if create_msg:
                self.add_msg("type_error")
                self.save_messages("file_error")

        else:
            a_utils.add_parents(tree)
            a_utils.add_siblings(tree)

        finally:
            return tree

    def analyse(self, tree, content, dir_path, filename, selections):
        """
        Analysis wrapper for preanalyser and analyser which do analysis
        for abstract syntax tree and file content from the ast is
        created.

        Return: List of violation messages.
        """

        try:
            # TODO: optimise such that os.listdir is done only once per directory
            files_in_dir = os.listdir(dir_path)
            self.pre_analyse_tree(tree, files_in_dir, dir_path)
            self.analyse_tree(tree, files_in_dir, content, selections)

        except Exception:
            self.clear_analysis_data()
            self.messages.clear()
            self.add_msg("tool_error", filename)
            self.save_messages("analysis_error")

        return self.all_messages

    def pre_analyse_tree(self, tree, files, dir_path):
        """
        Preanalyses abstract syntax tree and all imported local
        libraries.
        """

        self.pre_analyser.visit(tree)
        self.class_dict = self.pre_analyser.get_class_dict()
        self.function_dict = self.pre_analyser.get_function_dict()
        self.import_dict = self.pre_analyser.get_import_dict()
        self.global_variables = self.pre_analyser.get_global_dict()
         # This need setter, getter and initialisation if used
        self.constant_variables = self.pre_analyser.get_constant_dict()
        self.call_dict = self.pre_analyser.get_call_dict()
        self.files_opened = self.pre_analyser.get_file_list()
        self.pre_analyser.clear_all()

        imported = self.import_dict.keys()
        for i in imported:
            filename = f"{i}.py"
            if(filename in files):
                self.lib_list.append(i)
                content = utils.read_file(os.path.join(dir_path, filename))

                if not (tree := self.parse_ast(content, filename, create_msg=False)):
                    continue

                # Preanalysing imported local files
                analyser = pre_analyser.PreAnalyser(library=i)
                analyser.visit(tree)
                for func, value in analyser.get_function_dict().items():
                    if(not func in self.function_dict.keys()):
                        self.function_dict[func] = value
                analyser.clear_all()

    def analyse_tree(self, tree, file_list, content, selections):
        """
        Analyses abstract syntax tree and file content from the ast is
        created. Execute only analyses marked with selections argument.

        Return: List of violation messages.
        """

        # self.file_list = file_list

        for opt in self.checkbox_options:
            if(selections[opt]):
                analyser = self.analysers[opt]
                analyser.visit(tree)

                if(opt == "file_handling"):
                    # Check left open files
                    analyser.check_left_open_files(
                        self.files_opened,
                        self.files_closed
                    )

                elif(opt == "function"):
                    analyser.check_main_function()
                    analyser.check_element_order(tree.body, cnf.ELEMENT_ORDER)
                    analyser.check_global_variables()

                elif(opt == "library"):
                    # Info comments check, i.e. author, date etc.
                    analyser.check_info_comments(content)

                    # Duplicate import check
                    analyser.check_duplicate_imports(self.import_dict)

                    # Main file check
                    if(analyser.has_main_function(tree)): # True this should be a main file
                        pass
                    else: # Else means library file.
                        pass

                self.save_messages(opt)

    def format_results(self, filename, path, all_messages):
        line_list = []
        for title_key, msgs in all_messages:
            # Every second line is empty to make view less crowded.
            line_list.append(("", cnf.GENERAL))

            if(len(msgs) == 0): # No violations in this topic/title
                line_list.append(
                    utils.create_title('OK', title_key, lang=self.language)
                )
                continue

            # There are one or more violations in this topic/title
            line_list.append(
                utils.create_title('NOTE', title_key, lang=self.language)
            )

            for lineno, code, args in msgs:
                line_list.append(
                    utils.create_msg(code, *args, lineno=lineno, lang=self.language)
                )

        # File and filepath info at the beginning of each file.
        line_list.insert(0, (utils.create_dash(character="=", get_dash=True), cnf.GENERAL))
        line_list.insert(1, (path, cnf.GENERAL))
        line_list.insert(2, (filename, cnf.GENERAL))

        return line_list

   ####################################################################
   #  Debug functions
    def dump_tree(self, tree):
        utils.create_dash()
        print(ast.dump(tree, include_attributes=True))
        print()
        print(ast.dump(tree, include_attributes=False))
        print()
        print(ast.dump(tree, annotate_fields=False, include_attributes=False))
        utils.create_dash()