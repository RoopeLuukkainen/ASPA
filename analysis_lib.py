"""File to handle ASPA static analysers."""
__version__ = "0.1.1"
__author__ = "RL"

import ast
import os

# AST analysers
import pre_analyser
import data_structure_analyser
import error_handling_analyser
import basic_command_analyser
import file_handling_analyser
import file_structure_analyser
import function_analyser

# Utility libraries
import utils_lib as utils

class Model:
    def __init__(self, controller):
        self.controller = controller
        self.settings = self.controller.get_settings()
        self.violation_occurances = dict()

        try:
            self.language = self.settings["language"]
        except KeyError:  # This should not be possible if defaults settings are not changed
            print("Language is not defined in settings.")
            self.language = "FIN"

        try:
            self.checkbox_options = self.settings["checkbox_options"]
        except KeyError:   # This should not be possible if defaults settings are not changed
            # These could be in utils not in settings
            self.checkbox_options = ["basic", "function", "file_handling", "data_structure", "library", "exception_handling"]
        # There is possibility that there are no 6 elements in checkbox options,
        # but that is modified in the code then, i.e. not by user
        try:
            self.analysers = {
                self.checkbox_options[0]: basic_command_analyser.ExamAnalyser(self),
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

        # Variable lists (used by function_analyser)
        self.global_variables = set()
        self.local_variables = set()

        # File handling (used by file_handling_analyser)
        self.files_opened = list()
        self.files_closed =  list()

        # File structure list and dict used by file_structure_analyser and data_structure_analyser
        self.function_dict = dict()
        self.class_list = list()
        # File structure lists used by file_structure_analyser
        self.file_list = list()
        self.lib_list = list()
        self.imported = list()

        # Messages
        self.messages = list()
        self.all_messages = list()

   # List getters
    def get_global_variables(self):
        return set(self.global_variables)

    def get_local_variables(self):
        return set(self.local_variables)

    def get_imported(self):
        return list(self.imported)

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

    def get_class_list(self):
        return list(self.class_list)


   # List and set setters
    def set_global_variables(self, value, add=False):
        if(add):
            self.global_variables.add(value)
        else:
            self.global_variables = set(value)

    def set_local_variables(self, value):
        self.local_variables = set(value)

    def set_imported(self, value, append=False):
        if(append):
            self.imported.append(value)
        else:
            self.imported = list(value)

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

    def set_function_dict(self, value, key=None):
        if(key):
            self.function_dict[key] = value
        else:
            self.function_dict = dict(value)

    def set_class_list(self, value):
        self.class_list = list(value)

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
        self.class_list.clear()
        self.file_list.clear()
        self.lib_list.clear()
        self.imported.clear()

    def add_msg(self, code, *args, lineno=-1):
        if(not utils.ignore_check(code)):
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

    # TODO: MOVE TO -> controller -> view
    def show_all_messages(self, filename, path):
        content = ""
        for title_key, msgs in self.all_messages:
            title = utils.get_title(title_key, self.language)
            if(len(msgs) == 0):
                content += f"\n{title}: {utils.create_msg('OK', lang=self.language)}\n"
                continue

            content += f"\n{title}, {utils.create_msg('NOTE', lang=self.language)}:\n"
            for lineno, code, args in msgs:
                content += utils.create_msg(code, *args, lineno=lineno, lang=self.language) + "\n"

        if(self.settings["console_print"]):
            print(content)

        if(self.settings["file_write"]):
            write_content = f"{utils.create_dash(get_dash=True)}\n{path}\n{filename}\n{content}"
            utils.write_file(self.settings["result_path"], write_content, mode="a")

        if(self.settings["GUI_print"]):
            GUI_content = f"{utils.create_dash(get_dash=True)}\n{path}\n{filename}\n{content}"
            self.controller.update_result(GUI_content)

        if(self.settings["show_statistics"]):
            # Currently only cumulative count to console.
            # TODO: TEMPRORAL: Add to file and GUI too, OR make this own function
            for key, value in self.violation_occurances.items():
                print(f"{key}: {value}")
            print()

    # def find_defs(self, tree, library=None):
    #     class_list = list()
    #     function_dict = dict()
    #     import_set = set()

    #     for node in ast.walk(tree):
    #         if(isinstance(node, ast.ClassDef)):
    #             if(library):
    #                 class_list.append(f"{library}.{node.name}")
    #             else:
    #                 class_list.append(node.name)

    #         elif(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))):
    #             key = node.name
    #             pos_args = [i.arg for i in node.args.args]
    #             kw_args = [i.arg for i in node.args.kwonlyargs]

    #             parent = utils.get_parent_instance(node, 
    #                 (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    #             if(parent):
    #                 key = f"{parent.name}.{key}"
    #             if(library):
    #                 key = f"{library}.{key}"
    #             #  TODO: If key exist then there are two identically named functions in same scope

    #             function_dict[key] = utils.FunctionTemplate(
    #                 node.name, node, pos_args, kw_args)

    #         elif(isinstance(node, ast.Import)):
    #             try:
    #                 for i in node.names:
    #                     import_set.add(i.name)
    #             except AttributeError:
    #                 pass

    #         elif(isinstance(node, ast.ImportFrom)):
    #             try:
    #                 import_set.add(node.module)
    #             except AttributeError:
    #                 pass
    #         return class_list, function_dict, import_set

    def analyse(self, pathlist, selections):
        for path in pathlist:
            content = utils.read_file(path)
            filename = os.path.basename(path)

            if(self.settings["console_print"]):
                utils.create_dash()
                print(str(path))
                print(f"Analysing file: {filename}\n")
            # print(f"Analysoidaan tiedostoa: {filename, path}\n")

            # Create a abstract syntax tree and add parent nodes
            try:
                tree = ast.parse(content, filename)
            except SyntaxError:
                self.add_msg("syntax_error")
                self.save_messages("file_error")

            # When content is not str or AST (e.g. None), usually due failed
            # file reading.
            except TypeError:
                self.add_msg("type_error")
                self.save_messages("file_error")

            else:
                utils.add_parents(tree)
                self.pre_analyse_tree(tree)
                self.class_list, self.function_dict, self.imported = utils.find_defs(tree)
                # print(self.class_list, self.function_dict, self.imported)
                files_in_dir = os.listdir(os.path.dirname(path))
                # TODO: HERE add read and parse for each imported file and then somehow add those functions to function dict
                # HERE HERE
                
                # TODO: optimise such that os.listdir is done only once per directory
                self.analyse_tree(tree, files_in_dir, content, selections)

            self.show_all_messages(filename, path)
            self.clear_analysis_data()

    def pre_analyse_tree(self, tree):
        self.pre_analyser.visit(tree)
        imported = self.pre_analyser.get_import_dict().keys()


    def analyse_tree(self, tree, file_list, content, selections):
        """Function to conduct selected static analyses."""
        self.file_list = file_list

        # DUMP tree
        if(self.settings["dump_tree"]):
            utils.create_dash()
            print(ast.dump(tree, include_attributes=True))
            print()
            print(ast.dump(tree, include_attributes=False))
            utils.create_dash()

        for opt in self.checkbox_options:
            if(selections[opt]):
                analyser = self.analysers[opt]
                analyser.visit(tree)

                if(opt == "file_handling"):
                #    Check left open files
                    for file in analyser.check_left_open_files():
                        self.add_msg("TK1", file.id, lineno=file.lineno)

                elif(opt == "function"):
                    analyser.check_main_function()

                elif(opt == "library"):
                    # Info comments check, i.e. author, date etc.
                    analyser.check_info_comments(content)

                    # Duplicate import check
                    analyser.check_duplicate_imports(
                        self.pre_analyser.get_import_dict())

                    # Main file check
                    if(analyser.has_main_function(tree)): # True this should be a main file
                        pass
                    else: # Else means library file.
                        pass

                self.save_messages(opt)