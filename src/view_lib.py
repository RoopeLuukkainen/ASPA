"""Module for TKinter GUI frames."""

try:
    import Tkinter as tk  # Python 2
    from Tkinter import ttk         # Not tested
    from Tkinter import filedialog  # Not tested
except ModuleNotFoundError:
    import tkinter as tk  # Python 3, tested with this
    from tkinter import ttk
    from tkinter import filedialog
    from tkinter import font

import pathlib

import src.utils_lib as utils
import src.config.config as cnf

# Constants
def set_style_constants(settings):
    # TODO change this function more practical solution

    def parse_font(font_style, value):
        if value:
            parts = font_style.split(" ")
            parts[1] = str(value)
            font_style = " ".join(parts)
        return font_style

    global BG_COLOR, FRAME_COLOR, PAD, LARGE_FONT, NORMAL_FONT, SMALL_FONT
    global FONT_COLOR, BD_STYLE, BD, HIGHLIGHT

    BG_COLOR = cnf.BG_COLOR # None #"#bababa" #None # "#383838"
    FRAME_COLOR = cnf.FRAME_COLOR # None #"#ffcfcf"
    PAD = cnf.PAD # 5
    LARGE_FONT = parse_font(cnf.LARGE_FONT, settings.get("title_font_size")) # "None 12 bold"
    NORMAL_FONT = parse_font(cnf.NORMAL_FONT, settings.get("normal_font_size")) # "None 10"
    SMALL_FONT = parse_font(cnf.SMALL_FONT, settings.get("small_font_size")) # "None 8"
    FONT_COLOR = cnf.FONT_COLOR # "black"
    BD_STYLE = cnf.BD_STYLE # tk.RIDGE # Border style
    BD = cnf.BD # 2              # Border width
    HIGHLIGHT = cnf.HIGHLIGHT

    # Ttk buttons
    ttk.Style().configure("TButton", font=NORMAL_FONT)
    return None

################################################################################
class MainFrame(tk.Frame):
    def __init__(self, parent, lang):
       # -------------------------------------------------------------------- #
       # Variable and grid initialisations
        controller = parent
        tk.Frame.__init__(self, controller)

        self.LANG = lang
        self.pack(side="top", fill="both", expand=True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        settings = controller.get_settings()
        set_style_constants(settings)

       # --------------------------------------------------------------------- #
       # Content pages
        self.pages = {}

         # CLASS names are keys.
        for page_class in (AnalysePage, ResultPage, HelpPage):
            page = page_class(self, controller, settings)
            self.pages[page_class] = page
            page.grid(row=0, column=0, sticky=tk.NSEW)
        self.show_page(AnalysePage)

       # --------------------------------------------------------------------- #
       # Menubar
        menubar = tk.Menu(self)

        ## Create file menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(
            label=cnf.GUI[self.LANG]["results"],
            font=NORMAL_FONT,
            command=lambda: self.show_page(ResultPage)
        )
        # Add BKT analysis option
        filemenu.add_command(
            label=cnf.GUI[self.LANG]["BKTA"],
            font=NORMAL_FONT,
            command=lambda: self.pages[AnalysePage].analyse(
                controller.analyse_wrapper,
                analysis_type="BKTA"
            )
        )
        # Add guit option
        filemenu.add_command(
            label=cnf.GUI[self.LANG]["exit"],
            font=NORMAL_FONT,
            command=quit
        )
        menubar.add_cascade(label=cnf.GUI[self.LANG]["filemenu"], menu=filemenu)

        ## Create help menu
        helpmenu = tk.Menu(menubar, tearoff=1)
        helpmenu.add_command(
            label=cnf.GUI[self.LANG]["help"],
            font=NORMAL_FONT,
            command=lambda: self.show_page(HelpPage)
        )
        menubar.add_cascade(label=cnf.GUI[self.LANG]["helpmenu"], menu=helpmenu)

        self._menu = menubar

    @property
    def menu(self):
        return self._menu

    def get_page(self, page_class):
        """Method to return object of asked page class."""
        return self.pages[page_class]

    def show_page(self, page_class):
        """Method to show asked page based on given page_class."""
        # TODO: Hide pages on background if possible
        page = self.pages[page_class]
        page.tkraise()


################################################################################
class CheckboxPanel(tk.Frame):
    """Class to view checkbox panel. Usage clarification:
    in __init__ the self (i.e. inherited tk.Frame)
    is a master to all elements in this frame.
    """

    def __init__(self, parent, checkbox_options):
        tk.Frame.__init__(self, parent, bd=BD, relief=BD_STYLE)
        tk.Label(
            self,
            text=cnf.GUI[parent.LANG]["select_analysis_title"],
            bg=BG_COLOR,
            fg=FONT_COLOR,
            font=LARGE_FONT
        ).grid(row=0, column=0, columnspan=2, padx=PAD, pady=PAD)

        self.selected_analysis = {}
        count = 0
        for i in checkbox_options:
            count += 1
            self.selected_analysis[i] = tk.IntVar()
            self.selected_analysis[i].set(1)
            try:
                option = cnf.TEXT[parent.LANG][i]
            except KeyError:
                option = i

            cb = tk.Checkbutton(
                master=self,
                text=option,
                font=NORMAL_FONT,
                width=20,
                anchor=tk.W,
                variable=self.selected_analysis[i]
            )
            cb.grid(row=count, column=1, sticky=tk.W)

    def check(self, keys, value=1):
        """Method to set given value for given checkboxes."""
        for key in self.selected_analysis.keys():
            self.selected_analysis[key].set(0)
        if value != 0:
            try:
                for key in keys:
                    self.selected_analysis[key].set(1)
            except KeyError:
                pass
        return None

    def get_selections(self):
        return self.selected_analysis


################################################################################
class FiledialogPanel(tk.Frame):
    def __init__(self, parent, root, default_files):
        tk.Frame.__init__(self, parent, bd=BD, relief=BD_STYLE)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.root = root
        self.parent = parent

        # Title label
        tk.Label(
            self,
            text=cnf.GUI[parent.LANG]["filepaths"],
            bg=BG_COLOR,
            fg=FONT_COLOR,
            font=LARGE_FONT
        ).grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)

        # File dialog buttons
        ttk.Button(
            self,
            text=cnf.GUI[parent.LANG]["select_file"],
            command=self.get_filedialog
        ).grid(row=0, column=1, padx=PAD, pady=PAD, sticky=tk.E)

        ttk.Button(
            self,
            text=cnf.GUI[parent.LANG]["select_folder"],
            command=lambda: self.get_filedialog(directory=True)
        ).grid(row=0, column=2, padx=PAD, pady=PAD, sticky=tk.E)

        ttk.Button(
            self,
            text=cnf.GUI[parent.LANG]["clear"],
            command=self.clear_files
        ).grid(row=0, column=3, padx=PAD, pady=PAD, sticky=tk.E)


        # Create output text box
        self.filebox = tk.Text(
            self,
            width=50,
            height=10,
            bg=BG_COLOR,
            fg=FONT_COLOR,
            font=NORMAL_FONT, #font=SMALL_FONT
        )
        self.filebox.grid(
            row=1,
            column=0,
            columnspan=4,
            sticky=tk.NSEW,
            padx=PAD,
            pady=PAD
        )

        for filepath in default_files:
            self.add_file(filepath)

    def get_filedialog(self, directory=False):
        initdir = self.root
        # File dialog
        if directory:
            path = filedialog.askdirectory(
                initialdir=initdir,
                title=cnf.GUI[self.parent.LANG]["select_folder"]
            )
        else:
            path = filedialog.askopenfilename(
                initialdir=initdir,
                title=cnf.GUI[self.parent.LANG]["select_file"],
                filetypes=(
                    ("Python", "*.py"),
                    (cnf.GUI[self.parent.LANG]["all_files"], "*")
                ),
                multiple=True
            )

        if isinstance(path, tuple):
            for p in path:
                self.add_file(p)
        elif path:
            self.add_file(path)
        return None

    def add_file(self, path):
        self.filebox.config(state="normal")
        self.filebox.insert(tk.END, path + "\n")
        self.filebox.config(state="disabled")

    def clear_files(self):
        self.filebox.config(state="normal")
        self.filebox.delete(1.0, tk.END)
        self.filebox.config(state="disabled")

    def parse_filepaths(self, clear=False):
        pathset = set()
        for path in self.filebox.get(0.0, tk.END).split("\n"):
            path = path.strip()
            if path != "":
                pathset.add(path)
        if clear:
            self.clear_files()
        return pathset

    def get_filepath_list(self, clear=False):
        # TEMP: This should not be used at the end. This should be
        # replaced by call to model where list would be stored.
        return self.parse_filepaths(clear)

class ControlPanel(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bd=BD, relief=BD_STYLE)
        button_group = tk.Frame(master=self, bg=FRAME_COLOR)
        button_group.pack(side=tk.TOP)

        run_button = ttk.Button(
            button_group,
            text=cnf.GUI[parent.LANG]["execute_analysis"],
            command=lambda: parent.analyse(
                controller.analyse_wrapper,
                analysis_type="default"
            )
        )
        run_button.grid(row=0, column=0, padx=PAD, pady=PAD, sticky=tk.E)

        # exit_button = ttk.Button(button_group, text="Sulje ohjelma", command=quit) #command=parent.close_window)
        # exit_button.grid(row=0, column=1, padx=PAD, pady=PAD, sticky=tk.W)


################################################################################
class AnalysePage(tk.Frame):
    """Class to view analyse page. Usage clarification:
    in __init__ the self (i.e. inherited tk.Frame)
    is a master to all elements in this frame.
    """

    def __init__(self, parent, controller, settings):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.LANG = self.controller.get_lang()
        self.CLEAR_FILEPATHS = settings.get("clear_filepaths", False)
        # self.model = model

        self.ctrl_panel = ControlPanel(self, controller)
        self.check_panel = CheckboxPanel(self, settings["checkbox_options"])
        self.file_panel = FiledialogPanel(
            self,
            settings["root"],
            settings.get("default_paths", [])
        )

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.check_panel.grid(row=0, column=0, sticky=tk.NSEW)
        self.file_panel.grid(row=0, column=1, sticky=tk.NSEW)
        self.ctrl_panel.grid(row=1, columnspan=2, sticky=tk.EW)

        # ctrl_panel.pack(side="bottom", fill="x", expand=True)
        # check_panel.pack(side="left", fill="both", expand=True)
        # file_panel.pack(side="right", fill="both", expand=True)

        # button_all = ttk.Button(self, text="All",
        #                     command=lambda: controller.show_page(ResultPage))
        # button_all.pack()

    def analyse(self, analysis_func, analysis_type="default"):
        """
        Analysis wrapper function to redirect analysis call from GUI
        element to controller (and model) for actual analysis.
        """

        # NOTE this could be changed such that analysis_func (or analysis_wrapper)
        # would be decorator or similar wrapper but currently it is still
        # normal class method.
        analysis_func(
            self.check_panel.get_selections(),
            self.file_panel.get_filepath_list(clear=self.CLEAR_FILEPATHS),
            analysis_type
        )


################################################################################
class ResultPage(tk.Frame):
    """Class to view result page. Usage clarification:
    in __init__ the self (i.e. tk.Frame typed class)
    is a master to all elements in this frame.
    """

    def __init__(self, parent, controller, settings):
        tk.Frame.__init__(self, parent)
        self.LANG = controller.get_lang()
        self.settings = controller.get_settings()# settings
        self.line_counter = 0

        # Title label
        label = tk.Label(
            self,
            text=cnf.GUI[self.LANG]["analysis_result"],
            bg=BG_COLOR,
            fg=FONT_COLOR,
            font=LARGE_FONT
        )
        label.pack(padx=PAD, pady=PAD)

        # Result textbox frame
        result_frame = tk.Frame(self, bg=FRAME_COLOR)
        result_frame.pack(fill="both", expand=True, padx=PAD, pady=PAD)
        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)

        self.result_textbox = tk.Text(
            result_frame,
            font=NORMAL_FONT,
            state="disabled",
            height=15
        )
        self.result_textbox.grid(column=0, row=0, pady=PAD, sticky=tk.NSEW)
        scrollbar = ttk.Scrollbar(
            result_frame,
            orient=tk.VERTICAL,
            command=self.result_textbox.yview
        )
        scrollbar.grid(column=1, row=0, sticky=tk.NS, pady=PAD)
        self.result_textbox.configure(yscrollcommand=scrollbar.set)

        # Control buttons
        button_group = tk.Frame(master=self, bg=FRAME_COLOR)
        button_group.pack(side=tk.BOTTOM)

        back_button = ttk.Button(
            button_group,
            text=cnf.GUI[self.LANG]["back"],
            command=lambda: parent.show_page(AnalysePage)
        )
        back_button.grid(row=0, column=0, padx=PAD, pady=PAD, sticky=tk.E)
        # exit_button = ttk.Button(button_group, text="Sulje ohjelma", command=quit)
        # exit_button.grid(row=0, column=1, padx=PAD, pady=PAD, sticky=tk.W)

    def set_line_counter(self, counter, update=False):
        if update:
            self.line_counter += counter
        else:
            self.line_counter = counter

    def show_info(self):
        infos = [
            utils.create_msg("NOTE_INFO", lang=self.LANG),
            utils.create_msg("WARNING_INFO", lang=self.LANG),
            utils.create_msg("ERROR_INFO", lang=self.LANG)
        ]
        self.display_result(infos)
        infos.clear()

    def display_result(self, messages, counter=0):
        if not counter:
            counter = self.line_counter
        line_counter = counter

        self.result_textbox.config(state="normal")
        for msg in messages:
            # Text box lines start from 1 therefore add at the beginning
            line_counter += 1
            self.result_textbox.insert(tk.END, f"{msg[0]}\n")
            if len(msg) >= 4:
                s = f"{line_counter}.0 + {msg[2]}c"
                e = f"{line_counter}.0 + {msg[3]}c"
                self.colour_text(msg[1], start=s, end=e)

        self.result_textbox.config(state="disabled")
        self.line_counter = line_counter

    def colour_text(self, tag, start="1.0", end=tk.END):
        textbox = self.result_textbox
        try:
            color = HIGHLIGHT[tag]
        except KeyError:
            color = FONT_COLOR

        textbox.tag_configure(
            tag,
            font=font.Font(textbox, textbox.cget("font")),
            foreground=color
        )
        textbox.tag_add(tag, start, end)

    def clear_result(self):
        """Method to clear results textbox."""

        self.result_textbox.config(state="normal")
        self.result_textbox.delete(1.0, tk.END)
        self.result_textbox.config(state="disabled")

    def show_results(self, line_list):
        """Method to show analysis results in selected output channels."""

        # Last \n is added because of file.write() command doesn't add it.
        content = "\n".join((map(lambda elem: elem[0], line_list))) + "\n"
        if self.settings["console_print"]:
            print(content, end="")

        if self.settings["file_write"]:
            utils.write_file(self.settings["result_path"], content, mode="a")

        if self.settings["GUI_print"]:
            self.display_result(line_list)

    def print_statistics(self, statistics):
        """Method to print basic statistics of found violations.
        Currently contains only counts of each violation type.
        """

        utils.create_dash()
        for key, value in statistics.items():
            print(f"{key}: {value}")
        print()


################################################################################
class HelpPage(tk.Frame):
    """Class to view help page. Usage clarification:
    in __init__ the self (i.e. tk.Frame typed class)
    is a master to all elements in this frame.
    """

    def __init__(self, parent, controller, settings):
        tk.Frame.__init__(self, parent)
        self.LANG = controller.get_lang()

        label = tk.Label(
            self,
            text=cnf.GUI[self.LANG]["help"],
            bg=BG_COLOR,
            fg=FONT_COLOR,
            font=LARGE_FONT
        )
        label.pack()

        help_label = tk.Label(self, text=cnf.GUI[self.LANG]["not_ready_note"])
        help_label.pack()

        # Control buttons (identical to result page buttons)
        button_group = tk.Frame(master=self, bg=FRAME_COLOR)
        button_group.pack(side=tk.BOTTOM)

        back_button = ttk.Button(
            button_group,
            text=cnf.GUI[self.LANG]["back"],
            command=lambda: parent.show_page(AnalysePage)
        )
        back_button.grid(row=0, column=0, padx=PAD, pady=PAD, sticky=tk.E)
        # exit_button = ttk.Button(button_group, text="Sulje ohjelma", command=quit)
        # exit_button.grid(row=0, column=1, padx=PAD, pady=PAD, sticky=tk.W)


################################################################################
class SettingsPage(tk.Frame):
    """Class to view settings page. Usage clarification:
    in __init__ the self (i.e. tk.Frame typed class)
    is a master to all elements in this frame.
    """

    def __init__(self, parent, controller, settings):
        tk.Frame.__init__(self, parent)
        self.LANG = controller.get_lang()

        label = tk.Label(
            self,
            text=cnf.GUI[self.LANG]["settings"],
            bg=BG_COLOR,
            fg=FONT_COLOR,
            font=LARGE_FONT
        )
        label.pack()

        help_label = tk.Label(self, text=cnf.GUI[self.LANG]["not_ready_note"])
        help_label.pack()

        # Control buttons (identical to result page buttons)
        button_group = tk.Frame(master=self, bg=FRAME_COLOR)
        button_group.pack(side=tk.BOTTOM)

        back_button = ttk.Button(
            button_group,
            text=cnf.GUI[self.LANG]["back"],
            command=lambda: parent.show_page(AnalysePage)
        )
        back_button.grid(row=0, column=0, padx=PAD, pady=PAD, sticky=tk.E)
        # exit_button = ttk.Button(button_group, text="Sulje ohjelma", command=quit)
        # exit_button.grid(row=0, column=1, padx=PAD, pady=PAD, sticky=tk.W)


################################################################################
class CLI():
    """
    Upcoming class for command line views.
    """

    def __init__(self, lang):
        self.LANG = lang

    def print_error(self, error_code, *args, error_type="error"):
        if error_type == "error":
            print(cnf.CLI_ERROR[self.LANG][error_code])

        elif error_type == "conflict":
            print(cnf.SETTINGS_CONFLICTS[self.LANG][error_code])