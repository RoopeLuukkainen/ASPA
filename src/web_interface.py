"""web controller"""

import src.analysers.analysis_lib as analysis  # Model
import src.config.config as cnf
import src.utils_lib as utils

import tempfile
import os

# Constants
TOOL_NAME = cnf.TOOL_NAME
USER_FILES_PATH = "./user_files"

class WEB_INTERFACE_CLASS():
    """Main class for web interface.
    """

    def __init__(self, *args, settings={}, **kwargs):
        self.settings = settings
        self.LANG = settings.setdefault("language", "FIN")

        # Detect and solve possible settings conflicts
        conflicts = utils.detect_settings_conflicts(settings)
        if conflicts:
            utils.solve_settings_conflicts(conflicts, settings)
            for c in conflicts:
                self.propagate_error_message(c, error_type="conflict")

        self.model = analysis.Model(self)

    def get_settings(self):
        # Settings are not changed when where asked so no need to send copy.
        return self.settings
    
    #def propagate_error_message(self, error_code, *args, error_type="error"):
    #    self.cli.print_error(error_code, *args, error_type=error_type)

    def analyse_wrapper(self, selected_analysis, content, analysis_type):
        """
        Method to call when starting analysis. Calls correct functions
        to execute selected analysis type.
        """

        results = []
        
        temp_dir = USER_FILES_PATH

        temp_file_fd, temp_file_path = tempfile.mkstemp(suffix='.py', dir=temp_dir)

        with open(temp_file_path, 'w') as temp_file:
            temp_file.write(content)

        os.close(temp_file_fd)

        my_filepaths = {temp_file_path}

        #selections = {'basic': 1, 'function': 1, 'file_handling': 1, 'data_structure': 1, 'library': 1, 'exception_handling': 1}
        selections = selected_analysis
        
        #if not self.check_selection_validity(selected_analysis, filepaths):
        #    return None

        if analysis_type == "BKTA":
            output_format = "dict"
        else:  # default
            output_format = "list"

        file_structure = utils.directory_crawler(
            my_filepaths,
            only_leaf_files=self.settings["only_leaf_files"],
            excluded_dirs=self.settings["excluded_directories"],
            excluded_files=self.settings["excluded_files"],
            output_format=output_format
        )

        if analysis_type == "BKTA":
            self.model.BKT_analyse(
                selections,
                file_structure
            )

            self.model.count_structures(file_structure)
        else:
            results = self.model.default_analyse_web(
                selections,
                file_structure
            )

        # Remove the temporary user uploaded file
        os.unlink(temp_file_path)

        return results