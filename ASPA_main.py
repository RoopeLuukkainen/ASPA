#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The main file for ASPA - static analyser."""
__version__ = "0.2.4" # 28.09.2023
__author__ = "RL"

import src.GUI as GUI
from src.utils_lib import init_settings

def main():
    """Main function. For now no command line arguments are used."""
    settings = init_settings()
    gui = GUI.GUICLASS(settings=settings)
    gui.mainloop()


if __name__ == "__main__":
    main()
