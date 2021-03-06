#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The main file for ASPA - static analyser."""
__version__ = "0.1.2"
__author__ = "RL"

import src.GUI as GUI
from src.utils_lib import init_settings

def main():
    settings = init_settings()
    gui = GUI.GUICLASS(settings=settings)
    gui.mainloop()


if(__name__ == "__main__"):
    main()