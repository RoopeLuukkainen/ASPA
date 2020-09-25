#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The main file for ASPA - static analyser."""
__version__ = "0.1.1"
__author__ = "RL"

import json
import pathlib

import GUI
from utils_lib import read_file, write_file

DEFAULT_SETTINGS = {
    "root": str(pathlib.Path(__file__).parent.absolute()),
    "language": "FIN",
    "dump_tree": False,
    "console_print": False,
    "file_write": True,
    "GUI_print": True,
    "result_path": str(pathlib.Path(__file__).parent.absolute().joinpath("tarkistukset.txt")),
    "only_leaf_files": True,
    "show_statistics": False
}

def add_fixed_settings(settings):
    settings["checkbox_options"] = ["basic", "function", "file_handling", "data_structure", "library", "exception_handling"]


def init_settings():
    settings_file = "settings.json"
    settings = DEFAULT_SETTINGS

    content = read_file(settings_file, settings_file=True)
    if(content):
        for key, value in json.loads(content).items():
            settings[key] = value
    else:
        content = json.dumps(settings, indent=4)
        write_file(settings_file, content, mode="w")
    add_fixed_settings(settings)

    return settings


def main():
    settings = init_settings()
    gui = GUI.GUICLASS(settings=settings)
    gui.mainloop()


if(__name__ == "__main__"):
    main()