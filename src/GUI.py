"""GUI controller"""

try:
    import Tkinter as tk  # Python 2
except ModuleNotFoundError:
    import tkinter as tk  # Python 3, tested with this
    from tkinter import ttk
import datetime # for timestamp
import os

import src.analysers.analysis_lib as analysis # Model
import src.view_lib as view # View
import src.utils_lib as utils
import src.config.config as cnf

# Constants
TOOL_NAME = cnf.TOOL_NAME


class GUICLASS(tk.Tk):
    """Main class for GUI. Master for every used GUI element. The main
    frame and menubar are inlcuded in the here other GUI elements are
    in view. Works as a MVP model presenter/ MVC model controller.
    """

    def __init__(self, *args, settings={}, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # tk.Tk.iconbitmap(self, default="icon.ico")  # To change logo icon
        tk.Tk.title(self, TOOL_NAME)

        self.settings = settings
        self.lang = settings["language"]
        self.model = analysis.Model(self)
        self.line_count = 0

       # The main frame
        main_frame = tk.Frame(self)
        main_frame.pack(side="top", fill="both", expand=True)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Menubar
        menubar = tk.Menu(main_frame)

        # File menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(
            label=cnf.GUI[self.lang]["results"],
            command=lambda: self.show_page(view.ResultPage)
        )
        filemenu.add_command(
            label=cnf.GUI[self.lang]["exit"],
            command=quit
        )
        menubar.add_cascade(label=cnf.GUI[self.lang]["filemenu"], menu=filemenu)

        # Help menu
        helpmenu = tk.Menu(menubar, tearoff=1)
        helpmenu.add_command(
            label=cnf.GUI[self.lang]["help"],
            command=lambda: self.show_page(view.HelpPage)
        )
        menubar.add_cascade(label=cnf.GUI[self.lang]["helpmenu"], menu=helpmenu)

        # Display the menu
        tk.Tk.config(self, menu=menubar)

        self.pages = {}
        for p in (view.AnalysePage, view.ResultPage, view.HelpPage):
            page = p(main_frame, self, self.settings)
            self.pages[p] = page
            page.grid(row=0, column=0, sticky="nesw")
        self.show_page(view.AnalysePage)

    def get_lang(self):
        return self.lang

    def get_settings(self):
        # Settings are not changed when where asked so no need to send copy.
        return self.settings

    def show_page(self, cont):
        page = self.pages[cont]
        page.tkraise()

    def tkvar_2_var(self, tk_vars, to_type):
        selections = dict()
        if(isinstance(tk_vars, dict)):
            selections = dict(tk_vars)
            for key in selections.keys():
                if(to_type == "int"):
                    selections[key] = int(selections[key].get())
        return selections

    def analyse(self, selected_analysis, filepaths):
        selections = self.tkvar_2_var(selected_analysis, "int")
        if(sum(selections.values()) == 0):
            # TODO: Show message of missing analysis selections
            return None
        if(not filepaths):
            # TODO: Show message of missing files
            return None

        filelist = utils.crawl_dirs(filepaths, self.settings["only_leaf_files"])
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # # Timestamp to filename  (temporal solution!!)
        # self.settings["result_path"] = os.path.join(self.settings["root"],
        #     f"tarkistukset_{os.path.basename(filelist[0])}_{timestamp}.txt")  # Give error if file list is empty. Not yet fixed because temporal solution
        # # temporal ends

        utils.write_file(self.settings["result_path"], timestamp + "\n")

        result_page = self.pages[view.ResultPage]
        result_page.clear_result()  # Clears previous results
        result_page.show_info()  # Init new results with default info
        self.show_page(view.ResultPage)

        for filepath in filelist:
            content = utils.read_file(filepath)
            filename = os.path.basename(filepath)
            dir_path = os.path.dirname(filepath)

            # No check for tree being None etc. before analysis because
            # analyses will create violation if tree is not valid. Only
            # dump checks if tree is not True.
            tree = self.model.parse_ast(content, filename)

            # Dump tree
            if(tree and self.settings["dump_tree"]):
                self.model.dump_tree(tree)

            # Call analyser
            results = self.model.analyse(
                tree,
                content,
                dir_path,
                filename,
                selections
            )

            # Format results
            formated_results = self.model.format_results(
                filename,
                filepath,
                results
            )

            # Show results and clear results
            result_page.show_results(formated_results)
            self.model.clear_analysis_data()
            formated_results.clear()

        result_page.set_line_counter(0)
        return None