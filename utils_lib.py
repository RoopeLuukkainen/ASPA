"""Library containing utility functions for static analysers."""
__version__ = "0.1.4"
__author__ = "RL"

import ast
import os

class FunctionTemplate:
    def __init__(self, name, astree, pos_args, kw_args):
        self.name = name
        self.pos_args = pos_args # Positional arguments before *args
        self.kw_args = kw_args # Keyword arguments before **kwargs
        self.astree = astree # AST of the function

# TODO: Take this from the configuration file
IGNORE = {"PT1", "PK1"} # Add keys of ignored error messages

# ** Means warning
# ++ Means note
# <...> means not currently used
MSG = {
    "ENG": {
        "default": "Error occured!\n",
        "error_error": "\nError while printing an error message. :(\nProbably too few *args.\n", # Debug
        "syntax_error": "File has a syntax error.",
        "type_error": "Abstract Syntax Tree parameter has wrong type, e.g. None.", # Debug
        "OK": "No violations detected.",
        "NOTE": "detected",
        "PT1": "++Command '{}' is used.",
        "AR2-1": "Definition of the function '{}' is not at the global scope.",
        "AR3": "Global variable '{}'.",
        "AR3-2": "Variable or object is used in global scope '{}.{}'.", # Works only with objects
        "AR4": "**Recursive function call.",
        "AR5-1": "Function '{}' requires at least {} parameters, but {} given.",
        "AR5-2": "Function '{}' requires at most {} parameters, but {} given.",
        "AR5-3": "In call of function '{}', '{}' is invalid keyword argument.",
        "AR6": "Missing return at the end of the function '{}'.",
        "AR6-1": "**Usage of '{}' in function '{}'.",
        "AR6-2": "Return statement at the middle of the function.",
        "AR6-3": "Missing value from the return-statement.",
        "AR6-4": "**Return value is a constant.",
        "AR6-5": "<Lines after the return-statement.>",
        "MR2-3": "Function call '{}()' is {} function call at global scope. There\n"
                + "should be only one (1) function call, calling the main function.",
        "MR2-4": "Function call '{}.{}()' does not call the main function.",
        "MR3": "Library '{}' is imported again.",
        "MR3-1": "From library '{}' function(s) are imported again.",
        "MR4": "Import of the library '{}' is not at the global scope.",
        "MR4-1": "<Import of the library '{}' is not at the beginning of the file.>",
        "MR5": "Missing some or all header comments at {} first lines of the file.",
        "PK1": "**Error handling has only one (1) except.",
        "PK1-1": "Missing exception type.",
        "PK3": "Missing exception handling from the file opening.",
        "PK4": "Missing exception handling from the file operation '{}.{}'.",
        "TK1": "File handle '{}' is left open.",
        "TK1-2": "**File handle '{}' is closed in except-branch.",
        "TR2-1": "Class is being used as a global variable '{}.{}'.",
        "TR2-2": "Missing parenthesis from object creation. Should be '{}()'.",
        "TR2-3": "Class '{}' is not defined in global scope.",
        "WELCOME": "Program does static analysis for defined file(s).\n"
                + "In prints **-marking stands for warning, and ++ for note,\n"
                + "all others are errors."
    },
    "FIN": {
        "default": "Tapahtui virhe!\n",
        "error_error": "\nVirhe tulostettaessa virhettä.\n"
                      + "Luultavasti liian vähän argumentteja (*args).\n", # Debug
        "type_error": "Syntaksipuun (AST) parametri on väärää tyyppiä, esim. None.",  # Debug
        "syntax_error": "Tiedostossa on syntaksi virhe.",
        "OK": "Ei tunnistettu tyylirikkomuksia.",
        "NOTE": "huomioita",
        "PT1": "++Komentoa '{}' on käytetty.",
        "AR2-1": "Aliohjelman '{}' määrittely ei ole päätasolla.",
        "AR3": "Globaalimuuttuja '{}'.",
        "AR3-2": "Muuttujan tai olion globaali käyttö '{}.{}'.",
        "AR4": "**Rekursiivinen aliohjelmakutsu.",
        "AR5-1": "Aliohjelma '{}' vaatii vähintään {} parametria, mutta vain {} lähetetty.",
        "AR5-2": "Aliohjelma '{}' vaatii enintään {} parametria, mutta {} lähetetty.",
        "AR5-3": "Aliohjelmakutsussa '{}', '{}' on virheellinen muuttujan nimi.",
        "AR6": "Aliohjelman '{}' lopusta puuttuu return-komento.",
        "AR6-1": "**Käytetään generaattoria '{}' aliohjelmassa '{}'.",
        "AR6-2": "Keskellä aliohjelmaa on return.",
        "AR6-3": "return-kommenosta puuttuu paluuarvo.",
        "AR6-4": "**Paluuarvo on vakio.",
        "AR6-5": "<Koodirivejä return-komennon jälkeen.>",
        "MR2-3": "Aliohjelmakutsu '{}()' on {}. aliohjelmakutsu. Pitäisi olla vain\n"
                + "yksi (1) aliohjelmakutsu joka kutsuu paaohjelmaa.",
        "MR2-4": "Päätason aliohjelmakutsu '{}.{}()' ei viittaa tiedoston pääohjelmaan.",
        "MR3": "Kirjasto '{}' sisällytetään (eng. import) uudelleen.",
        "MR3-1": "Kirjastosta '{}' sisällytetään (eng. import) aliohjelmia uudelleen.",
        "MR4": "Kirjaston '{}' sisällytys (eng. import) ei ole päätasolla.",
        "MR4-1": "<Kirjaston '{}' sisällytys (eng. import) ei ole tiedoston alussa.>",
        "MR5": "Tiedostossa ei ole kaikkia alkukommentteja tiedoston {} ensimmäisellä rivillä.",
        "PK1": "**Virheenkäsittelyssä vain yksi (1) except.",
        "PK1-1": "Exceptistä puuttuu virhetyyppi.",
        "PK3": "Tiedoston avaamisesta puuttuu virheenkäsittely.",
        "PK4": "Tiedosto-operaatiosta '{}.{}' puuttuu virheenkäsittely.",
        "TK1": "Tiedostokahva '{}' on sulkematta.",
        "TK1-2": "**Tiedostokahva '{}' suljetaan except-haarassa.",
        "TR2-1": "Luokan käyttö globaalina muuttujana '{}.{}'.",
        "TR2-2": "Olion luonnista puuttuvat sulkeet. Pitäisi olla '{}()'.",
        "TR2-3": "Luokkaa '{}' ei ole määritelty päätasolla.",
        "WELCOME": "Ohjelma suorittaa staattisen analyysin annetulle tiedostolle.\n"
                + "Tulosteissa **-merkintä tarkoittaa varoitusta ja ++-merkintä ilmoitusta,\n"
                + "muut ovat virheitä."
    }
}

TEXT = {
    "FIN": {
        "basic": "Perustoiminnot",
        "function": "Aliohjelmat",
        "file_handling": "Tiedostonkäsittely",
        "data_structure": "Tietorakenteet",
        "library": "Kirjaston käyttö",
        "exception_handling": "Poikkeustenkäsittely",
        "file_error": "Tiedostovirhe" # File error e.g. SyntaxError
    },
    "ENG": {
        "basic": "Basic commands",
        "function": "Functions",
        "file_handling": "File handling",
        "data_structure": "Data structures",
        "library": "Library usage",
        "exception_handling": "Exception handling",
        "file_error": "File Error" # File error e.g. SyntaxError
    }
}

GUI = {
    "FIN": {
        "results": "Tulokset",
        "exit": "Sulje",
        "filemenu": "Toiminnot",
        "help": "Käyttöohje",
        "helpmenu": "Ohjeet",
        "select_analysis_title": "Valitse tarkistukset",
        "preset_title": "Esivalinnat",
        "clear": "Tyhjennä",
        "exam_level": "Tentti taso",
        "course_project_short": "HT",
        "filepaths": "Tiedostopolut",
        "select_file": "Valitse tiedosto",
        "select_folder": "Valitse kansio",
        "all_files": "Kaikki tiedostot",
        "execute_analysis": "Suorita analyysi",
        "analysis_result": "Analyysin tulokset",
        "back": "Takaisin",
        "settings": "Asetukset",
        "not_ready_note": "Työn alla"
    },
    "ENG": {
        "results": "Results",
        "exit": "Exit",
        "filemenu": "File",
        "help": "User guide",
        "helpmenu": "Help",
        "select_analysis_title": "Select analyses",
        "preset_title": "Presets",
        "clear": "Clear",
        "exam_level": " Exam level",
        "course_project_short": "CP",
        "filepaths": " Filepaths",
        "select_file": "Select file",
        "select_folder": "Select folder",
        "all_files": "All files",
        "execute_analysis": "Execute analysis",
        "analysis_result": "Analysis results",
        "back": "Back",
        "settings": "Settings",
        "not_ready_note": "Under construction"
    }
}

def add_parents(tree):
    for node in ast.walk(tree):
        for child_node in ast.iter_child_nodes(node):
            child_node.parent_node = node


def get_parent_instance(node, allowed, denied=tuple()):
    temp = node
    parent = None
    while(hasattr(temp, "parent_node") and not isinstance(temp, denied)):
        temp = temp.parent_node
        if(isinstance(temp, allowed)):
            parent = temp
            break
    return parent


def ignore_check(code):
    if(code in IGNORE):
        return True
    else:
        return False


def create_msg(code, *args, lineno=-1, lang="FIN"):
    msg = ""
    if(lineno < 0):
        pass
    elif(lang == "ENG"):
        msg = f"Line {lineno}: "
    elif(lang == "FIN"):
        msg = f"Rivillä {lineno}: "

    try:
        msg += MSG[lang][code]
    except KeyError:
        msg += MSG["default"]

    try:
        return msg.format(*args)
    except IndexError:
        return MSG[lang]["error_error"]


def crawl_dirs(paths, only_leaf_files=False):
    filelist = list()
    for path in paths:
        if(os.path.isdir(path)):
            for current_dir, dirs, all_files in os.walk(path):
                if(not all_files or (only_leaf_files and dirs)):
                    continue
                files = [f for f in all_files if(f.endswith(".py"))]

                for f in files:
                    filelist.append(os.path.join(current_dir, f))
        elif(os.path.isfile(path) and path.endswith(".py")):
            filelist.append(path)
        # else # file is a special file e.g. socket, FIFO or device file OR not .py file.

    return filelist


def read_file(filepath, encoding="UTF-8", settings_file=False):
    content = None
    try:
        with open(filepath, "r", encoding=encoding) as f_handle:
            content = f_handle.read() # Add pass / fail metadata extraction 
    except OSError:
        if(not settings_file):
            print("OSError while reading a file", filepath)
    except:
        pass
    return content


def write_file(filename, content, mode="w", encoding="UTF-8"):
    try:
        with open(filename, mode=mode, encoding=encoding) as f_handle:
            f_handle.write(content)
    except OSError:
        print("OSError while writing a file", filename)
    except:
        print("Other error than OSError with file", filename)
    return None


def get_title(title_key, lang):
    return TEXT[lang][title_key]


def print_title(title):
    print(f"--- {title} ---")


def create_dash(a="-", dash_count=80, get_dash=False):
    if(get_dash):
        return a*dash_count
    else:
        print(a*dash_count)

