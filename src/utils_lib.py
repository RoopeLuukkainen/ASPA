"""Module containing utility functions general use."""

# import ast
import json
import os       # os.walk is used for convenient directory exclusion possibility
import pathlib  # Used for all the other path operations
import re
from typing import List

import src.config.config as cnf
import src.config.templates as templates


MSG = cnf.MSG
STRUCTURE = cnf.STRUCTURE
EXAMPLES = cnf.EXAMPLES
TITLE_TO_EXAMPLES = cnf.TITLE_TO_EXAMPLES
TEXT = cnf.TEXT

IGNORE = cnf.IGNORE
GENERAL = cnf.GENERAL
ERROR = cnf.ERROR
WARNING = cnf.WARNING
NOTE = cnf.NOTE
GOOD = cnf.GOOD
DEBUG = cnf.DEBUG

########################################################################
# Regex
REGEX = {}  # This will store compiled regex patterns
PATTERN = { # This include all configurated patterns as a string
    "valid_naming": cnf.VALID_NAME_SCHEMA,
    "_global_element": cnf._GLOBAL_ELEM
}

########################################################################
# General utilities

def ignore_check(code):
    """
    Function to test if check will be ignored. Test is based on
    violation ID.

    Return:
     - True if check will be ignored.
     - False if check won't be ignored.
    """

    if code in IGNORE:
        return True
    return False


def get_all_ignored_checks():
    """
    Getter function for set which included ID's of all ignored checks.
    """

    return IGNORE


def create_msg(code, *args, lineno=-1, lang="FIN"):
    """
    Function to create violation message based on given violation code,
    message parameters (e.g. variable name), linenumber and language.

    Return:
    1. msg - violation message - string
    2. severity - severity level of message - integer number
        (numbers are predefined global constants)
    3. start - character index of violation message's start position
        - integer number
    4. end - character index of violation message's end position
        - integer number
    """

    msg = ""
    start = 0
    end = 0
    severity = MSG[lang]["default"][1]
    # if lineno < 0:
    #     pass
    if lineno >= 0 and lang:
        msg = f"{MSG[lang]['LINE'][0]} {lineno}: "
        start = len(msg)

    try:
        msg += MSG[lang][code][0]
        severity = MSG[lang][code][1]
    except KeyError:
        msg += MSG[lang]["default"][0]
    else:
        try:
            msg = msg.format(*args)
        except IndexError:
            msg = MSG[lang]["error_error"][0]
    finally:
        end = len(msg)

    return msg, severity, start, end


def get_title(title_key, lang):
    """
    Return: title of if ast analyser based on title_key (analyser ID)
    and lang (language). If there is KeyError return None.
    """

    try:
        return TEXT[lang][title_key]
    except KeyError:
        return None


def create_title(code, title_key, lang="FIN"):
    """
    Function to create title string message based on given title code,
    title_key and language.

    Arguments:
    1. code - ID of title - str
    2. title_key - ID of ast analyser - str
    3. lang - language of title, default is FIN - str

    Return:
    1. msg - title - string
    2. severity - severity level of title - integer number
        (numbers are predefined global constants)
    3. start - character index of title's start position - integer
       number
    4. end - character index of title's end position - integer number
    """

    title = get_title(title_key, lang)
    msg = ""
    start = 0
    end = 0
    severity = GENERAL
    if title:
        msg = title
        start = len(msg) + 1

    try:
        if title_key != "analysis_error":
            msg += MSG[lang][code][0]
            severity = MSG[lang][code][1]

            if code == "NOTE":
                exs = TITLE_TO_EXAMPLES[title_key]
                for i in exs:
                    if i == "EX0":
                        msg += f" {EXAMPLES[i]}"
                    else:
                        msg += f" '{EXAMPLES[i]}'"
                msg += ":"
    except KeyError:
        pass

    finally:
        end = len(msg)

    return msg, severity, start, end


def directory_crawler(
    paths,
    excluded_dirs=(),
    excluded_files=(),
    only_leaf_files=True,
    output_format="list"
):
    """
    Function to crawl all (sub)directories and return filepaths based on
    given rules.

    Arguments:
    1. paths is list of crawled filepaths. Paths should be in string
       format.
    2. excluded_dirs is iterable of (sub)directories which are excluded
       from the crawling.
    3. excluded_files is iterable of files which are excluded from the
       crawling result.
    4. only_leaf_files if True/False. If True include only files from
       directories which do not have subdirectories, after excluded_dirs
       are excluded.
    5. output_format defines format in which filepaths are returned.
       Supported formats are currently dictionary and list. List is
       default.

    Return: Filepaths in format speficied in output_format argument.
    """

    def remove_excluded(dirs, excluded):
        for e in excluded:
            try:
                dirs.remove(e)
            except ValueError:
                pass

    def add_file(file_struct, filepath):
        # TODO add settings which allow user to define corresponding numberings
        # and how many there are and in which order.
        student = 0
        exercise = 1
        week = 2 # exam
        # course = 3

        student_str = filepath.parents[student].name
        week_str = filepath.parents[week].name
        exercise_str = filepath.parents[exercise].name

        file_struct.setdefault(student_str, []).append(
            templates.FilepathTemplate(
                path=filepath,
                student=student_str,
                week=week_str,
                exercise=exercise_str
            )
        )


    # List which will include every filepath as pathlib.Path object
    file_list = []

    for path_str in paths:
        path_obj = pathlib.Path(path_str).resolve()

        if path_obj.is_dir():
            # for sub in path_obj.glob("**/*.py"): # NOTE glob itself does not
            # allow selecting only leaf files, therefore os.path.walk is used.
            for current_dir, dirs, all_files in os.walk(path_obj, topdown=True):
                remove_excluded(dirs, excluded_dirs)

                if not all_files or (only_leaf_files and dirs):
                    continue

                for f in all_files:
                    if f.endswith(".py") and not f in excluded_files:
                        file_list.append(pathlib.Path(current_dir).joinpath(f))

        elif (path_obj.is_file()
                and path_obj.suffix == ".py"
                and not path_str in excluded_files):
            file_list.append(path_obj)

    # Transform file_list into requested file structure.
    if output_format == "list":
        file_structure = []

        for path_obj in file_list:
            file_structure.append(templates.FilepathTemplate(path=path_obj))

    elif output_format == "dict":
        file_structure = {}

        for path_obj in file_list:
            add_file(file_structure, path_obj)

    # Else there is invalid output_format then empty list is returned.
    else:
        file_structure = []

    file_list.clear()

    return file_structure


def read_file(filepath, encoding="UTF-8", settings_file=False):
    """
    Function to read given filepath. If encoding is given use it
    otherwise expect UTF-8 encoding.

    Return: Read content as string.
    """

    content = None
    try:
        with open(filepath, "r", encoding=encoding) as f_handle:
            content = f_handle.read() # Add pass / fail metadata extraction
    except OSError:
        if not settings_file:
            print("OSError while reading a file", filepath)
    except Exception:
        pass
    return content


def write_file(filepath, content, mode="w", encoding="UTF-8", repeat=True):
    """
    Function to write given content to given filepath. If filepath has
    subdirectories which do not exists, these subdirectories are created
    and single recursive call is created to try again.

    Return: None
    """

    try:
        try:
            with open(filepath, mode=mode, encoding=encoding) as f_handle:
                f_handle.write(content)

        except FileNotFoundError: # When subdirectory is not found
                path = pathlib.Path(filepath)
                path.parent.absolute().mkdir(parents=True, exist_ok=True)
                if repeat:
                    # This call is first level recursion
                    write_file(
                        filepath,
                        content,
                        mode=mode,
                        encoding=encoding,
                        repeat=False # To prevent infinite repeat loop
                    )

    except OSError:
        print("OSError while writing a file", filepath)
    except Exception:
        print("Other error than OSError with file", filepath)
    return None


def print_title(title):
    print(f"--- {title} ---")


def create_dash(character="-", dash_count=80, get_dash=False):
    """
    Creates a "line" which is given character repeated dash_count times.

    Return: If get_dash is True, return created "line of dashes"
            else prints it and return None.
    """

    if get_dash:
        return character * dash_count
    else:
        print(character * dash_count)


########################################################################
# Getter functions for static values

def get_structures(lang="FIN"):
    return STRUCTURE.get(lang, {})


def get_compiled_regex(key):
    """
    Function to get compiled regex pattern. On the first call pattern
    will be compiled in concecutive calls same compiled pattern will be
    returned.
    """

    # NOTE this will raise a KeyError if key is not found from the
    # PATTERN but that should be possible only in development phase when
    # patterns are added to config file and to the PATTERN dictionary.
    # PATTERN is not configurable by an end user.
    return REGEX.setdefault(key, re.compile(PATTERN[key]))


########################################################################
# Init functions

def add_fixed_settings(settings):
    """
    Function to add fixed settings which are not modifieable by user and
    derived settings e.g. result paths which are concatenated result
    directory path and filename.

    Return: None
    """

    # Checkbox options
    settings["checkbox_options"] = cnf.CHECKBOX_OPTIONS

    # Result file paths
    result_dir = pathlib.Path(settings["result_dir"])
    settings["result_path"] = result_dir.joinpath(settings["result_file"])
    settings["BKT_path"] = result_dir.joinpath(settings["BKT_file"])
    settings["structure_path"] = result_dir.joinpath(settings["structure_file"])

    # Combine BKT_ignored_staff and excluded_directories which are basically
    # doing the same thing (in current directory structure).
    settings["excluded_directories"].extend(settings["excluded_staff"])
    return None


def init_settings() -> dict:
    """
    Function to initialise settings dictionary. Settings are based on
    default settings which are then updated by values from settings.json
    file. If there is no settings file, new settings.json file is
    created.

    Return: settings dictionary.
    """

    settings = cnf.DEFAULT_SETTINGS # Currently reference not copy
    settings_file = settings.get("settings_file", "settings.json")

    content = read_file(settings_file, settings_file=True)
    if content:
        for key, value in json.loads(content).items():
            settings[key] = value
    else:
        content = json.dumps(settings, indent=4)
        write_file(settings_file, content, mode="w")
    add_fixed_settings(settings)
    return settings


def detect_settings_conflicts(settings: dict) -> List[str]:
    """
    Function to check throught predefined set of possible conflict cases
    in settings.

    Arguments:
    1. settings - Settings dictionary, key is setting name and value is
       setting value - dict

    Return: conflicts - list of conflict message IDs (str) - List[str]
    """

    # Initialise
    conflicts = []

    # Check defined conflict cases
    if settings.get("BKT_decimal_separator") == settings.get("BKT_cell_separator"):
        conflicts.append("C0001")

    return conflicts


def solve_settings_conflicts(conflicts: List[str], settings: dict) -> None:
    """
    Function to solve detected settings conflicts.

    Arguments:
    1. conflicts - List of conflict message keys as string - List[str]
    2. settings - Settings dictionary, key is setting name and value is
       setting value - dict

    Return: None
    """

    for key in conflicts:
        if key == "C0001":
            settings["BKT_decimal_separator"] = ","
            settings["BKT_cell_separator"] = ";"

    return None
