"""File to handle ASPA static analysers."""

import ast
import copy      # for deepcopy
import datetime  # for timestamp
import json      # for statistics
import os
import pathlib
import re

# Utility libraries
from ..config import config as cnf
from ..config import templates
import src.utils_lib as utils
import src.analysers.analysis_utils as a_utils

# AST analysers
import src.analysers.pre_analyser as pre_analyser
import src.analysers.data_structure_analyser as data_structure_analyser
import src.analysers.exception_handling_analyser as exception_handling_analyser
import src.analysers.basic_command_analyser as basic_command_analyser
import src.analysers.file_handling_analyser as file_handling_analyser
import src.analysers.file_structure_analyser as file_structure_analyser
import src.analysers.function_analyser as function_analyser

# BKT analyser
import src.BKT.BKT_analyser as BKT_A
import src.analysers.structure_detector as structure_detector

class Model:
    def __init__(self, controller):
        self.controller = controller
        self.settings = self.controller.get_settings()
        self.violation_occurances = {} # TEMP NOT USED?
        self.statistics = {"ALL": {}}

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
                self.checkbox_options[5]: exception_handling_analyser.ExceptionHandlingAnalyser(self)
            }
        except IndexError:
            pass
        # Pre analyser
        self.pre_analyser = pre_analyser.PreAnalyser()
        self.constant_variables = {}

        # Structure/command detector
        self.structure_detector = structure_detector.StructureDetector()
        self.structures = {}

        # Variable data structures (used by function_analyser)
        self.global_variables = {}
        self.local_variables = set()
        self.call_dict = {}
        self.same_names_dict = {}

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

        # Result list for checks from each category and list for storing
        # category_result lists
        self._category_results = []
        self.all_results = []

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
        self.all_results.clear()
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

# TODO rename this method to something better, e.g. add_result
    def add_msg(self, code, *args, lineno=-1, status=False):
        """
        Method which creates a violation object based on arguments and
        add the object to result list.

        Arguments:
        1. code is ID for detected violation (or correctly done action).
        2. *args are possible arguments for message formating.
        3. lineno is linenumber where violation was detected.
        4. status is True or False, where True means something is done
           right, i.e. no violation, while False means it is done
           incorrectly, i.e. it is a violation.

        Return: None
        """

        if not utils.ignore_check(code):
            self._category_results.append(
                templates.ViolationTemplate(code, args, lineno, status)
            )

            # Very primitive statistic calculation
            try:
                self.violation_occurances[code] += 1
            except KeyError:
                self.violation_occurances[code] = 1
        return None

    def save_category(self, title):
        self.all_results.append((title, tuple(self._category_results)))
        self._category_results.clear()

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
        current_statistics = {}
        yaml_dict = {}  # TA yaml data

        for filepath in file_list:
            results = self.execute_analysis(filepath, selections)

            # Statistics
            # FIX currently "student" only works for course project directory
            # structure
            if self.settings.get("show_statistics", False):
                current_statistics = a_utils.calculate_statistics(results)
                # TODO change to filepath.path.student when it is ready in template
                # TODO add setting for this, i.e. is it file or directory/folder

                student = f"{filepath.path.parents[1].name}/{filepath.path.parents[0].name}"
                # student = f"{filepath.path.parents[0].name}/{filepath.filename}"
                # student = filepath.path.parents[0].name
                a_utils.sum_statistics(
                    self.statistics,
                    student,
                    current_statistics
                )
                current_statistics.clear()

            # Format results
            formated_results = self.format_violations(results)

            # Count violations to violation dict
            violation_dict = a_utils.results_to_violation_dict(results)

            # TA version YAML formatting
            directory_name = filepath.path.parents[0].name
            analysed_filename = filepath.path.name
            if directory_name in yaml_dict.keys():
                yaml_dict[directory_name]["additional_comments"] += "\n{}\n{}{}".format(
                    utils.create_dash(character="=", get_dash=True),
                    analysed_filename,
                    "\n".join(map(lambda x: x[0], formated_results)) #0th value is the message
                )

                # Combine violations, changed to built-in dict so that YAML parser can handle it
                yaml_dict[directory_name]["violations"] = dict(utils.combine_integer_dicts(
                    yaml_dict[directory_name]["violations"],
                    copy.deepcopy(violation_dict)
                ))

            else:
                yaml_dict[directory_name] = {}
                # Comments in text
                yaml_dict[directory_name]["additional_comments"] = "ASPAn palaute:\n{}{}".format(
                    analysed_filename,
                    "\n".join(map(lambda x: x[0], formated_results))
                )
                # Violations, changed to built-in dict so that YAML parser can handle it
                yaml_dict[directory_name]["violations"] = dict(copy.deepcopy(violation_dict))



            # Add filename and filepath at the beginning of the result list
            formated_results.insert(
                0, (utils.create_dash(character="=", get_dash=True), cnf.GENERAL)
            )
            if (self.settings["shown_filepath_format"]
                    in cnf.OPTIONS_FOR_ALL + cnf.FILENAME_OPTIONS):
                formated_results.insert(1, (filepath.filename, cnf.GENERAL))

            if (self.settings["shown_filepath_format"]
                    in cnf.OPTIONS_FOR_ALL + cnf.FILEPATH_OPTIONS):
                formated_results.insert(1, (str(filepath.path), cnf.GENERAL))

            # Show results and clear results
            result_page.show_results(formated_results)
            self.clear_analysis_data()
            formated_results.clear()

        if self.settings.get("show_statistics", False):
            if self.settings.get("console_print", False):
                a_utils.print_statistics(self.statistics)

            if self.settings.get("file_write", False):
                content = json.dumps(self.statistics, indent=4)
                utils.write_file(
                    self.settings["statistics_path"],
                    content,
                    mode="w"
                )

            self.statistics.clear()
            self.statistics = {"ALL": {}}

        # Write TA yaml results
        utils.write_yaml_file(self.settings["yaml_result_file"], yaml_dict)

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

        # round handles also negative accuracy so no need to check that. However
        # user might get undesired results with that (in BKT case basically 0.0)
        # 0 is also allowed setting therefore using default value intead of
        # "or"-operator to give value 3 as default.
        _ACC = self.settings.get("BKT_decimal_places", 3)
        _DESIM_SEP = self.settings.get("BKT_decimal_separator") or ","
        _CELL_SEP = self.settings.get("BKT_cell_separator") or ";"


        # Create indexes for titles and sort them from A to Z (ascending order).
        # TODO add setting which allow sorting by selected value
        BKT_title_sorted = sorted(cnf.BKT_TITLES[self.language].keys())
        BKT_index = {}
        for i, title in enumerate(BKT_title_sorted):
            BKT_index[title] = i

        # --- 1. Initialise result file with title line and content lines -list ---
        BKT_result_path = self.settings.get("BKT_path")
        title_line = "{0:s}{1:s}{2:s}\n".format(
                cnf.BKT_TEXT[self.language]["student_name"],
                _CELL_SEP,
                _CELL_SEP.join(BKT_title_sorted)
            )
        utils.write_file(BKT_result_path, title_line, mode="w")

        content_lines = []
        initial_line = [0] * len(BKT_title_sorted)

        # --- 2. BKT analyse all files in given paths ---
        for student_name, filepaths in file_dict.items():
            student = BKT_A.Student(student_name)
            for filepath in filepaths:
                results_per_title = self.execute_analysis(filepath, selections)

                # --- Add results to student object to update BKTA values ---
                for title, results in results_per_title:
                    student.add_results(results, key="vid", success="status")

                self.clear_analysis_data()

            # --- Format results into writable list ---
            result_line = initial_line[:] # copy to allow separate changes
            for key, result in student.get_results().items():
                try:
                    result_line[BKT_index[key]] = round(result.Ln, _ACC)
                except (KeyError, IndexError):
                    pass

            content_lines.append(
                "{0}{1}{2}".format(  # Basically 'studentID;float;...;float' as str
                    student.student_id,
                    _CELL_SEP,
                    _CELL_SEP.join(map(str, result_line)).replace(".", _DESIM_SEP)
                )
            )

            # --- 3. Write results to BKT result file ---
            utils.write_file(
                BKT_result_path,
                "\n".join(content_lines) + "\n",
                mode="a"
            )

            # --- 4. Clear written results before next iteration ---
            result_line.clear()
            content_lines.clear()

        # At the end clear created data structures
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
            self.dump_tree(tree, self.settings.get("dump_indent", 0))

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
                self.save_category("file_error")

        # When content is not str or AST (e.g. None), usually due failed
        # file reading.
        except TypeError:
            if create_msg:
                self.add_msg("type_error")
                self.save_category("file_error")

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
            # TODO make paths Pathlib compatible such that os is not neede
            files_in_dir = os.listdir(dir_path)
            # files_in_dir = list(dir_path.iterdir())
            self.detect_structures(tree, pathlib.Path.joinpath(dir_path, filename))
            self.pre_analyse_tree(tree, files_in_dir, dir_path)
            self.analyse_tree(tree, files_in_dir, content, selections)

        except Exception as e:
            print(e)
            self.clear_analysis_data()
            self._category_results.clear()
            self.add_msg("tool_error", filename)
            self.save_category("analysis_error")

        return self.all_results

    def detect_structures(self, tree, filepath):
        """
        Execute structure detection for abstract syntax tree.
        """

        try:
            self.structure_detector.visit(tree)
        except Exception:
            pass
        else:
            self.structures[pathlib.Path(filepath)] = self.structure_detector.get_structures()
        self.structure_detector.clear_all()

    def pre_analyse_tree(self, tree, files, dir_path):
        """
        Preanalyses abstract syntax tree and all imported local
        libraries.
        """

        self.pre_analyser.visit(tree)
        self.pre_analyser.lock_constants()

        self.class_dict = self.pre_analyser.get_class_dict()
        self.function_dict = self.pre_analyser.get_function_dict()
        self.import_dict = self.pre_analyser.get_import_dict()
        self.global_variables = self.pre_analyser.get_global_dict()
         # This needs setter, getter and initialisation if used
        self.constant_variables = self.pre_analyser.get_constant_dict()
        self.call_dict = self.pre_analyser.get_call_dict()
        self.files_opened = self.pre_analyser.get_file_list()
        # This needs setter and getter
        self.same_names_dict = self.pre_analyser.get_local_global_dict()
        self.pre_analyser.clear_all()

        imported = self.import_dict.keys()
        for i in imported:
            filename = f"{i}.py"
            if(filename in files):
                self.lib_list.append(i)
                content = utils.read_file(pathlib.Path.joinpath(dir_path, filename))

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
                    analyser.check_local_global_names(self.same_names_dict)
                    analyser.check_recursive_functions(self.function_dict)
                    analyser.clear_all()

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

                self.save_category(opt)

    def format_violations(self, all_results):
        """
        Method to format results to violations. Category titles are
        included between results. Includes only results which are
        violations.

        Return: List of violation tuples.
        """

        line_list = []
        violations = []
        for title_key, results in all_results:
            violations.clear()

            # Every line after each topics is empty to make view less crowded.
            line_list.append(("", cnf.GENERAL))

            # Include only violations
            for violation in results:
                if violation.status == False:  # False means there is a violation
                    violations.append(violation)

            # Check if there are violations in this topic/title, if not go to
            # next title/analysis category.
            if len(violations) == 0:
                line_list.append(
                    utils.create_title('OK', title_key, lang=self.language)
                )
                continue

            # There is one or more violations in this topic/title so need to add
            # a note.
            line_list.append(
                utils.create_title('NOTE', title_key, lang=self.language)
            )

            for violation in violations: # TODO sort by lineno?
                line_list.append(violation.get_msg(self.language))
        violations.clear()

        return line_list

    def count_structures(self, file_dict):
        """
        Method to write detected structures into a result file.
        NOTE: This is currently pretty identical to the BKT analysis.
        """

        _CELL_SEP = self.settings.get("structure_cell_separator") or ";"
        STRUCTURES = utils.get_structures(self.language)
        ignore_formats = re.compile("|".join(cnf.IGNORE_STRUCT))

        # Create indexes for titles and sort them from A to Z (ascending order).
        structure_index = {}
        for i, key in enumerate(sorted(STRUCTURES.keys())):
            if not ignore_formats.pattern or (ignore_formats.match(key)) is None:
                structure_index[key] = i

        # --- 1. Initialise result file with title line and content lines -list ---
        result_path = self.settings.get("structure_path")
        title_line = "{cell_sep:s}{titles:s}\n".format(
                cell_sep=_CELL_SEP,
                titles=_CELL_SEP.join(
                    map(lambda x: STRUCTURES.get(x), structure_index.keys())
                )
            )
        utils.write_file(result_path, title_line, mode="w")

        content_lines = []
        initial_line = [0] * len(structure_index.keys())
        # --- 2. Count all structures ---
        for student_name, filepaths in file_dict.items():
            result_line = initial_line[:] # copy to allow separate changes
            if not filepaths:
                continue

            for filepath in filepaths:
                # In some filepaths there is no detected structures,
                # therefore default is needed to be iterable, i.e. empty
                # list instead of None.
                structs = self.structures.get(filepath.path, [])

                for s in structs:
                    try:
                        result_line[structure_index[s.identifier]] += 1
                    except KeyError:
                        # Basically ignored structures goes here
                        pass

            # --- Format results into writable list ---
            content_lines.append(
                "{student:s}{cell_sep:s}{results:s}".format(  # Basically 'name;int;...;int' as str
                    student=student_name,
                    cell_sep=_CELL_SEP,
                    results=_CELL_SEP.join(map(str, result_line))
                )
            )

            # --- 3. Write results to BKT result file ---
            content_lines.append("") # Last empty line
            utils.write_file(
                result_path,
                "\n".join(content_lines),
                mode="a"
            )

            # --- 4. Clear written results before next iteration ---
            result_line.clear()
            content_lines.clear()

        # At the end clear created data structures
        initial_line.clear()
        structure_index.clear()
        self.structures.clear()

        return None

   ####################################################################
   #  Debug functions
    def dump_tree(self, tree, indent=4):
        if indent == 0:
            indent = None
        utils.create_dash()
        print(ast.dump(tree, include_attributes=True, indent=indent))
        print()
        print(ast.dump(tree, include_attributes=False, indent=indent))
        print()
        print(ast.dump(tree, annotate_fields=False,
                       include_attributes=False, indent=indent))
        utils.create_dash()