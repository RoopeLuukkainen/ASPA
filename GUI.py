"""GUI controller"""
__version__ = "0.0.1"
__author__ = "RL"

try:
    import Tkinter as tk  # Python 2
except ModuleNotFoundError:
    import tkinter as tk  # Python 3, tested with this
    from tkinter import ttk
import datetime # for timestamp
import os

import analysis_lib as analysis # Model
import view_lib as view # View
import utils_lib as utils

# Constants
TOOL_NAME = "ASPA - Abstrakti SyntaksiPuu Analysaattori"


class GUI(tk.Tk):
    """Main class for GUI. Master for every used GUI element. The main frame and
    menubar are inlcuded in the here other GUI elements are in view.
    Works as a MVP model presenter/ MVC model controller."""
    def __init__(self, *args, settings={}, **kwargs):
        self.root = tk.Tk.__init__(self, *args, **kwargs)
        # tk.Tk.iconbitmap(self, default="icon.ico")  # To change logo icon
        tk.Tk.title(self, TOOL_NAME)

        self.settings = settings
        self.lang = settings["language"]
        self.model = analysis.Model(self)

       # The main frame
        main_frame = tk.Frame(self)
        main_frame.pack(side="top", fill="both", expand=True)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Menubar
        menubar = tk.Menu(main_frame)

        # File menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label=utils.GUI[self.lang]["results"], command=lambda: self.show_page(view.ResultPage))
        filemenu.add_command(label=utils.GUI[self.lang]["exit"], command=quit)
        menubar.add_cascade(label=utils.GUI[self.lang]["filemenu"], menu=filemenu)

        # Help menu
        helpmenu = tk.Menu(menubar, tearoff=1)
        helpmenu.add_command(label=utils.GUI[self.lang]["help"], command=lambda: self.show_page(view.HelpPage))
        menubar.add_cascade(label=utils.GUI[self.lang]["helpmenu"], menu=helpmenu)

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
        return self.settings  # Settings are not changed when where asked so no need to send copy.

    def show_page(self, cont):
        page = self.pages[cont]
        page.tkraise()

    def tkvar_2_var(self, tk_vars, to_type):
        if(isinstance(tk_vars, dict)):
            selections = dict(tk_vars)
            for key in selections.keys():
                if(to_type == "int"):
                    selections[key] = int(selections[key].get())
        return selections

    def analyse(self, selected_analysis, filepaths):
        selections = self.tkvar_2_var(selected_analysis, "int")
        filelist = utils.crawl_dirs(filepaths, self.settings["only_leaf_files"])
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # # Timestamp to filename  (temporal solution!!)
        # self.settings["result_path"] = os.path.join(self.settings["root"], 
        #     f"tarkistukset_{os.path.basename(filelist[0])}_{timestamp}.txt")  # Give error if file list is empty. Not yet fixed because temporal solution
        # # temporal ends

        utils.write_file(self.settings["result_path"], timestamp + "\n")
        self.pages[view.ResultPage].clear_result()  # Clears previous results
        self.show_page(view.ResultPage)
        self.model.analyse(filelist, selections)

    def update_result(self, result):
        self.pages[view.ResultPage].add_result(result)