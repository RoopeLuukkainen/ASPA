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
BG_COLOR = cnf.BG_COLOR # None #"#bababa" #None # "#383838"
FRAME_COLOR = cnf.FRAME_COLOR # None #"#ffcfcf"
PAD = cnf.PAD # 5
LARGE_FONT = cnf.LARGE_FONT # "None 12 bold"
NORMAL_FONT = cnf.NORMAL_FONT # "None 10"
SMALL_FONT = cnf.SMALL_FONT # "None 8"
FONT_COLOR = cnf.FONT_COLOR # "black"
BD_STYLE = cnf.BD_STYLE # tk.RIDGE # Border style
BD = cnf.BD # 2              # Border width
HIGHLIGHT = cnf.HIGHLIGHT


class CheckboxPanel(tk.Frame):
    """Class to view checkbox panel. Usage clarification:
    in __init__ the self (i.e. inherited tk.Frame) 
    is a master to all elements in this frame.
    """
    def __init__(self, parent, checkbox_options):
        tk.Frame.__init__(self, parent, bd=BD, relief=BD_STYLE)
        tk.Label(self, text=cnf.GUI[parent.LANG]["select_analysis_title"], bg=BG_COLOR, fg=FONT_COLOR, font=LARGE_FONT).grid(row=0, column=0, columnspan=2, padx=PAD, pady=PAD)
    #    tk.Label(self, text=utils.GUI[parent.LANG]["preset_title"], bg=BG_COLOR, fg=FONT_COLOR, font=LARGE_FONT).grid(row=0, column=3, padx=PAD, pady=PAD)

        self.selected_analysis = dict()
        count = 0
        for i in checkbox_options:
            count += 1
            self.selected_analysis[i] = tk.IntVar()
            self.selected_analysis[i].set(1)
            try:
                option = cnf.TEXT[parent.LANG][i]#ENG_TEXT[i]#FIN_TEXT[i]
            except KeyError:
                option = i
            cb = tk.Checkbutton(master=self, text=option, width=20, anchor=tk.W, 
                                variable=self.selected_analysis[i])
            cb.grid(row=count, column=1, sticky=tk.W)

        # tk.Label(self, text="try-except rakenteet", bg=BG_COLOR, fg=FONT_COLOR, font=SMALL_FONT).grid(row=count+1, column=1, padx=PAD, sticky="w")#, pady=PAD)


    #    # Predefined options buttons
    #     buttons = list()

    #     b_clear = ttk.Button(self, text=utils.GUI[parent.LANG]["clear"],
    #         command=lambda: self.check(self.selected_analysis.keys(), 0))
    #     b_clear.grid(row=1, column=3, padx=PAD, pady=PAD, sticky=tk.W + tk.E)
    #     buttons.append(b_clear)

    #     for i in range(1, len(checkbox_options)):
    #         b = ttk.Button(self, text=f"{utils.GUI[parent.LANG]['exam_level']} {i}",  # Here could be also week number range
    #             command=lambda i=i: self.check(checkbox_options[0:i]))
    #         b.grid(row=i+1, column=3, padx=PAD, pady=PAD, sticky=tk.W + tk.E)
    #         buttons.append(b)

    #     # Hotfix to make last one being all
    #     buttons[-1].config(text=f"{utils.GUI[parent.LANG]['exam_level']} {len(checkbox_options)-1} / {utils.GUI[parent.LANG]['course_project_short']}", 
    #                        command=lambda: self.check(self.selected_analysis.keys()))

    def check(self, keys, value=1):
        """Method to set given value for given checkboxes."""
        for key in self.selected_analysis.keys():
            self.selected_analysis[key].set(0)
        if(value != 0):
            try:
                for key in keys:
                    self.selected_analysis[key].set(1)
            except KeyError:
                pass
        return None

    def get_selections(self):
        return self.selected_analysis


class FiledialogPanel(tk.Frame):
    def __init__(self, parent, root):
        tk.Frame.__init__(self, parent, bd=BD, relief=BD_STYLE)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.root = root
        self.parent = parent

        # Title label
        tk.Label(self, text=cnf.GUI[parent.LANG]["filepaths"], bg=BG_COLOR, fg=FONT_COLOR, font=LARGE_FONT).grid(row=0, column=0, sticky=tk.W, padx=PAD, pady=PAD)

        # File dialog buttons
        ttk.Button(self, text=cnf.GUI[parent.LANG]["select_file"], command=self.get_filedialog).grid(row=0, column=1, padx=PAD, pady=PAD, sticky=tk.E)
        ttk.Button(self, text=cnf.GUI[parent.LANG]["select_folder"], command=lambda: self.get_filedialog(dir=True)).grid(row=0, column=2, padx=PAD, pady=PAD, sticky=tk.E)
        ttk.Button(self, text=cnf.GUI[parent.LANG]["clear"], command=self.clear_files).grid(row=0, column=3, padx=PAD, pady=PAD, sticky=tk.E)


        # Create output text box
        self.filebox = tk.Text(self, width=50, height=10, bg=BG_COLOR, fg=FONT_COLOR, font=NORMAL_FONT)#font=SMALL_FONT)
        self.filebox.grid(row=1, column=0, columnspan=4, sticky="nesw", padx=PAD, pady=PAD)
        
        # self.filebox.insert(0.0, "E:/GitLab/ast-analyser/test_files/example2.py\nE:/GitLab/ast-analyser/test_files/lib_example.py\n") # TODO: remove this line
        #self.filebox.insert(0.0, "E:/GitLab/ast-analyser/test_files/analysis_examples.py") # TODO: remove this line

    def get_filedialog(self, dir=False):
        initdir = self.root
        # File dialog
        if(dir):
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

        if(isinstance(path, tuple)):
            for p in path:
                self.add_file(p)
        elif(path):
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
            if(path != ""):
                pathset.add(path)
        if(clear):
            pass # TODO: remove this line
            # self.clear_files()
        return pathset

    def get_filepath_list(self, clear=False):
        # TODO: This should not be used at the end but only during the testing phase
        # This should be replaced by call to model where list is stored
        return self.parse_filepaths(clear)

class ControlPanel(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, bd=BD, relief=BD_STYLE)
        button_group = tk.Frame(master=self, bg=FRAME_COLOR)
        button_group.pack(side=tk.TOP)

        run_button = ttk.Button(button_group, text=cnf.GUI[parent.LANG]["execute_analysis"], command=parent.analyse)
        run_button.grid(row=0, column=0, padx=PAD, pady=PAD, sticky=tk.E)

        # exit_button = ttk.Button(button_group, text="Sulje ohjelma", command=quit) #command=parent.close_window)
        # exit_button.grid(row=0, column=1, padx=PAD, pady=PAD, sticky=tk.W)



class AnalysePage(tk.Frame):
    """Class to view analyse page. Usage clarification:
    in __init__ the self (i.e. inherited tk.Frame) 
    is a master to all elements in this frame.
    """
    def __init__(self, parent, controller, settings):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.LANG = self.controller.get_lang()
        # self.model = model

        self.ctrl_panel = ControlPanel(self)
        self.check_panel = CheckboxPanel(self, settings["checkbox_options"])
        self.file_panel = FiledialogPanel(self, settings["root"])

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.check_panel.grid(row=0, column=0, sticky="nesw")
        self.file_panel.grid(row=0, column=1, sticky="nesw")
        self.ctrl_panel.grid(row=1, columnspan=2, sticky="ew")

        # ctrl_panel.pack(side="bottom", fill="x", expand=True)
        # check_panel.pack(side="left", fill="both", expand=True)
        # file_panel.pack(side="right", fill="both", expand=True)

        # button_all = ttk.Button(self, text="All", 
        #                     command=lambda: controller.show_page(ResultPage))
        # button_all.pack()

    def analyse(self):
        self.controller.analyse(
            self.check_panel.get_selections(),
            self.file_panel.get_filepath_list(clear=True)
        )


class ResultPage(tk.Frame):
    """Class to view result page. Usage clarification:
    in __init__ the self (i.e. tk.Frame typed class) 
    is a master to all elements in this frame.
    """
    def __init__(self, parent, controller, settings):
        tk.Frame.__init__(self, parent)
        self.LANG = controller.get_lang()

        # Title label
        label = tk.Label(self, text=cnf.GUI[self.LANG]["analysis_result"], bg=BG_COLOR, fg=FONT_COLOR, font=LARGE_FONT)
        label.pack(padx=PAD, pady=PAD)

        # Result textbox frame
        result_frame = tk.Frame(self, bg=FRAME_COLOR)
        result_frame.pack(fill="both", expand=True, padx=PAD, pady=PAD)
        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)

        self.result_textbox = tk.Text(result_frame, state="disabled", height=15)
        self.result_textbox.grid(column=0, row=0, pady=PAD, sticky="nsew")
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_textbox.yview)
        scrollbar.grid(column=1, row=0, sticky="ns", pady=PAD)
        self.result_textbox.configure(yscrollcommand=scrollbar.set)

        # Control buttons
        button_group = tk.Frame(master=self, bg=FRAME_COLOR)
        button_group.pack(side=tk.BOTTOM)

        back_button = ttk.Button(button_group, text=cnf.GUI[self.LANG]["back"],
                                command=lambda: controller.show_page(AnalysePage))
        back_button.grid(row=0, column=0, padx=PAD, pady=PAD, sticky=tk.E)
        # exit_button = ttk.Button(button_group, text="Sulje ohjelma", command=quit)
        # exit_button.grid(row=0, column=1, padx=PAD, pady=PAD, sticky=tk.W)

    def show_info(self, counter=0):
        infos = [
            utils.create_msg("NOTE_INFO"),
            utils.create_msg("WARNING_INFO"),
            utils.create_msg("ERROR_INFO")
        ]
        c = self.add_result(infos, counter=counter)
        infos.clear()
        return c

    def add_result(self, messages, counter=0):

        self.result_textbox.config(state="normal")
        line_counter = counter
        for msg in messages:
            line_counter += 1 # Text box lines start from 1 therefore add at the beginning
            self.result_textbox.insert(tk.END, f"{msg[0]}\n")
            if(len(msg) >= 4):
                s = f"{line_counter}.0 + {msg[2]}c"
                e = f"{line_counter}.0 + {msg[3]}c"
                self.colour_text(msg[1], start=s, end=e)

        self.result_textbox.config(state="disabled")
        return line_counter

    def colour_text(self, tag, start="1.0", end=tk.END):
        textbox = self.result_textbox
        try:
            color = HIGHLIGHT[tag]
        except KeyError:
            color = FONT_COLOR

        textbox.tag_configure(tag,
                              font=font.Font(textbox, textbox.cget("font")),
                              foreground=color)
        textbox.tag_add(tag, start, end)

    def clear_result(self):
        self.result_textbox.config(state="normal")
        self.result_textbox.delete(1.0, tk.END)
        self.result_textbox.config(state="disabled")


class HelpPage(tk.Frame):
    """Class to view help page. Usage clarification:
    in __init__ the self (i.e. tk.Frame typed class) 
    is a master to all elements in this frame.
    """
    def __init__(self, parent, controller, settings):
        tk.Frame.__init__(self, parent)
        self.LANG = controller.get_lang()

        label = tk.Label(self, text=cnf.GUI[self.LANG]["help"], bg=BG_COLOR, fg=FONT_COLOR, font=LARGE_FONT)
        label.pack()

        help_label = tk.Label(self, text=cnf.GUI[self.LANG]["not_ready_note"])
        help_label.pack()

        # Control buttons (identical to result page buttons)
        button_group = tk.Frame(master=self, bg=FRAME_COLOR)
        button_group.pack(side=tk.BOTTOM)

        back_button = ttk.Button(button_group, text=cnf.GUI[self.LANG]["back"],
                                command=lambda: controller.show_page(AnalysePage))
        back_button.grid(row=0, column=0, padx=PAD, pady=PAD, sticky=tk.E)
        # exit_button = ttk.Button(button_group, text="Sulje ohjelma", command=quit)
        # exit_button.grid(row=0, column=1, padx=PAD, pady=PAD, sticky=tk.W)


class SettingsPage(tk.Frame):
    """Class to view settings page. Usage clarification:
    in __init__ the self (i.e. tk.Frame typed class) 
    is a master to all elements in this frame.
    """
    def __init__(self, parent, controller, settings):
        tk.Frame.__init__(self, parent)
        self.LANG = controller.get_lang()

        label = tk.Label(self, text=cnf.GUI[self.LANG]["settings"], bg=BG_COLOR, fg=FONT_COLOR, font=LARGE_FONT)
        label.pack()

        help_label = tk.Label(self, text=cnf.GUI[self.LANG]["not_ready_note"])
        help_label.pack()

        # Control buttons (identical to result page buttons)
        button_group = tk.Frame(master=self, bg=FRAME_COLOR)
        button_group.pack(side=tk.BOTTOM)

        back_button = ttk.Button(button_group, text=cnf.GUI[self.LANG]["back"],
                                command=lambda: controller.show_page(AnalysePage))
        back_button.grid(row=0, column=0, padx=PAD, pady=PAD, sticky=tk.E)
        # exit_button = ttk.Button(button_group, text="Sulje ohjelma", command=quit)
        # exit_button.grid(row=0, column=1, padx=PAD, pady=PAD, sticky=tk.W)