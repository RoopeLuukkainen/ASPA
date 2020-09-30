"""Library containing utility functions for static analysers."""
__version__ = "0.1.5"
__author__ = "RL"

import ast
import os
# TODO NodeTemplate
class FunctionTemplate:
    def __init__(self, name, astree, pos_args, kw_args):
        self.name = name
        self.pos_args = pos_args # Positional arguments before *args
        self.kw_args = kw_args # Keyword arguments before **kwargs
        self.astree = astree # AST of the function

class ImportTemplate:
    def __init__(self, name, lineno, astree, import_from=False):
        self.name = name
        self.import_from = import_from 
        self.astree = astree # AST of the 'import'/'import from' node
        self.lineno = lineno

MAIN_FUNC_NAME = "paaohjelma"
# TODO: Take this from the configuration file
IGNORE = {"PT1", "PK1", "MR5", "AR6-1"} # Add keys of ignored error messages
GENERAL = 0
ERROR = 1
WARNING = 2
NOTE = 3
GOOD = 4
DEBUG = 5

# <...> means not yet used
MSG = {
    "ENG": {
        "default": ("Error occured!", ERROR),
        "error_error": ("Error while printing an error message. "
                        + "Probably too few *args.", DEBUG), # Debug
        "type_error": ("Abstract Syntax Tree parameter has wrong type, e.g. None.", DEBUG), # Debug
        "syntax_error": ("File has a syntax error.", ERROR),
        "OK": ("No violations detected.", GOOD),
        "PT1": ("Command '{}' is used.", NOTE),
        "PT4-1": ("Loop never breaks.", ERROR),
        "AR1": (f"No function defition for '{MAIN_FUNC_NAME}'.", NOTE),
        "AR2-1": ("Definition of the function '{}' is not at the global scope.", ERROR),
        "AR3": ("Global variable '{}'.", ERROR),
        "AR3-2": ("Variable or object is used in global scope '{}.{}'.", ERROR), # Works only with objects
        "AR4": ("Recursive function call.", NOTE),
        "AR5-1": ("Function '{}' requires at least {} parameters, but {} given.", ERROR),
        "AR5-2": ("Function '{}' requires at most {} parameters, but {} given.", ERROR),
        "AR5-3": ("In call of function '{}', '{}' is invalid keyword argument.", ERROR),
        "AR6": ("Missing return at the end of the function '{}'.", ERROR),
        "AR6-1": ("Usage of '{}' in function '{}'.", NOTE), # Yield and yield from detection
        "AR6-2": ("Return statement at the middle of the function.", NOTE),
        "AR6-3": ("Missing value from the return-statement.", WARNING),
        "AR6-4": ("Return value is a constant.", NOTE),
        "AR6-5": ("<Lines after the return-statement.>", ERROR),
        "MR2-3": ("Function call '{}()' is {} function call in global scope. There "
                + f"should be only one (1) function call '{MAIN_FUNC_NAME}()'.",
                WARNING),
        "MR2-4": ("Function call '{}.{}()' in global scope does not call the"
                + "main function.", WARNING),
        "MR3": ("Module '{}' is imported again.", ERROR),
        "MR3-1": ("From module '{}' function(s) or module(s) are imported again.", WARNING),
        "MR4": ("Import of the module '{}' is not at the global scope.", ERROR),
        "MR4-1": ("<Import of the module '{}' is not at the beginning of the file.>", WARNING),
        "MR5": ("Missing some or all header comments at {} first lines of the file.", WARNING),
        "PK1": ("Error handling has only one (1) except.", NOTE),
        "PK1-1": ("Missing exception type.", WARNING),
        "PK3": ("Missing exception handling from the file opening.", ERROR),
        "PK4": ("Missing exception handling from the file operation '{}.{}'.", ERROR),
        "TK1": ("File handle '{}' is left open.", ERROR),
        "TK1-2": ("File handle '{}' is closed in except-branch.", WARNING),
        "TR2-1": ("Class is being used directly without an object '{}.{}'.", ERROR),
        "TR2-2": ("Missing parenthesis from object creation. Should be '{}()'.", ERROR),
        "TR2-3": ("Class '{}' is not defined in global scope.", ERROR),
        "LINE": ("Line", GENERAL),
        "NOTE": ("detected", GENERAL),
        "WELCOME": ("In prints **-marking stands for warning, and ++ for note, "
                 + "all others are errors.", GENERAL)
    },
    "FIN": {
        "default": ("Tapahtui virhe!", ERROR),
        "error_error": ("Virhe tulostettaessa virhettä. Luultavasti "
                      + "liian vähän argumentteja (*args).", DEBUG), # Debug
        "type_error": ("Syntaksipuun parametri on väärää tyyppiä, esim. None.", DEBUG), # Debug
        "syntax_error": ("Tiedostossa on syntaksi virhe.", ERROR),
        "OK": ("Ei tunnistettu tyylirikkomuksia.", GOOD),
        "PT1": ("Komentoa '{}' on käytetty.", NOTE),
        "PT4-1": ("Silmukkaa ei koskaan pysäytetä.", ERROR),
        "AR1": (f"Ohjelmasta ei löytynyt määrittelyä '{MAIN_FUNC_NAME}':lle.", NOTE),
        "AR2-1": ("Aliohjelman '{}' määrittely ei ole päätasolla.", ERROR),
        "AR3": ("Globaalimuuttuja '{}'.", ERROR),
        "AR3-2": ("Muuttujan tai olion globaali käyttö '{}.{}'.", ERROR),
        "AR4": ("Rekursiivinen aliohjelmakutsu.", NOTE),
        "AR5-1": ("Aliohjelma '{}' vaatii vähintään {} parametria, mutta vain {} lähetetty.", ERROR),
        "AR5-2": ("Aliohjelma '{}' vaatii enintään {} parametria, mutta {} lähetetty.", ERROR),
        "AR5-3": ("Aliohjelmakutsussa '{}', '{}' on virheellinen muuttujan nimi.", ERROR),
        "AR6": ("Aliohjelman '{}' lopusta puuttuu return-komento.", ERROR),
        "AR6-1": ("Käytetään generaattoria '{}' aliohjelmassa '{}'.", NOTE), # Yield and yield from detection
        "AR6-2": ("Keskellä aliohjelmaa on return.", NOTE),
        "AR6-3": ("return-kommenosta puuttuu paluuarvo.", WARNING),
        "AR6-4": ("Paluuarvo on vakio.", NOTE),
        "AR6-5": ("<Koodirivejä return-komennon jälkeen.>", ERROR),
        "MR2-3": ("Aliohjelmakutsu '{}()' on {}. aliohjelmakutsu. Pitäisi olla vain "
                + f"yksi (1) aliohjelmakutsu '{MAIN_FUNC_NAME}()'.", WARNING),
        "MR2-4": ("Päätason aliohjelmakutsu '{}.{}()' ei viittaa tiedoston pääohjelmaan.", WARNING),
        "MR3": ("Kirjasto '{}' sisällytetään (eng. import) uudelleen.", ERROR),
        "MR3-1": ("Kirjastosta '{}' sisällytetään sisältöä uudelleen.", WARNING),
        "MR4": ("Kirjaston '{}' sisällytys (eng. import) ei ole päätasolla.", ERROR),
        "MR4-1": ("<Kirjaston '{}' sisällytys (eng. import) ei ole tiedoston alussa.>", WARNING),
        "MR5": ("Tiedostossa ei ole kaikkia alkukommentteja tiedoston {}"
                + " ensimmäisellä rivillä.", WARNING),
        "PK1": ("Virheenkäsittelyssä vain yksi (1) except.", NOTE),
        "PK1-1": ("Exceptistä puuttuu virhetyyppi.", WARNING),
        "PK3": ("Tiedoston avaamisesta puuttuu virheenkäsittely.", ERROR),
        "PK4": ("Tiedosto-operaatiosta '{}.{}' puuttuu virheenkäsittely.", ERROR),
        "TK1": ("Tiedostokahva '{}' on sulkematta.", ERROR),
        "TK1-2": ("Tiedostokahva '{}' suljetaan except-haarassa.", WARNING),
        "TR2-1": ("Luokan käyttö suoraan ilman objektia '{}.{}'.", ERROR),
        "TR2-2": ("Olion luonnista puuttuvat sulkeet. Pitäisi olla '{}()'.", ERROR),
        "TR2-3": ("Luokkaa '{}' ei ole määritelty päätasolla.", ERROR),
        "NOTE": ("huomioita", GENERAL),
        "LINE": ("Rivi", GENERAL),
        "WELCOME": ("Tulosteissa **-merkintä tarkoittaa varoitusta ja ++-merkintä ilmoitusta, "
                 + "muut ovat virheitä.", GENERAL)
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
    """Function to get parent instance of a node. 
    'allowed' argument defines type of the desired parent, it should be
    any of the ast node types and can be tuple. Optional argument '
    denied' defines not allowed parents as ast node types.
    
    If allowed type is found, returns found node, if denied type is 
    found first or neither of them is found returns None.
    """
    temp = node
    parent = None
    while(hasattr(temp, "parent_node") and not isinstance(temp, denied)):
        temp = temp.parent_node
        if(isinstance(temp, allowed)):
            parent = temp
            break
    return parent


def get_child_instance(node, allowed, denied=tuple()):
    """Function to get child instance of a node.
    'allowed' argument defines type of the desired child, it should be
    any of the ast node types and can be tuple. Optional argument '
    denied' defines not allowed children as ast node types.
    
    If allowed type is found, returns found node, if denied type is 
    found first or neither of them is found returns None.
    """
    child = None
    for child_node in ast.walk(node):
        if(isinstance(child_node, allowed)):
            child = child_node
            break
        elif(isinstance(child_node, denied)):
            break
    return child 


def find_defs(tree, library=None):
    class_list = list()
    function_dict = dict()
    import_list = list()

    for node in ast.walk(tree):
        if(isinstance(node, ast.ClassDef)):
            # print(node.lineno, "class")
            if(library):
                class_list.append(f"{library}.{node.name}")
            else:
                class_list.append(node.name)

        elif(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))):
            # print(node.lineno, "func")
            key = node.name
            pos_args = [i.arg for i in node.args.args]
            kw_args = [i.arg for i in node.args.kwonlyargs]

            parent = get_parent_instance(node, 
                (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            if(parent):
                key = f"{parent.name}.{key}"
            if(library):
                key = f"{library}.{key}"
            #  TODO: If key exist then there are two identically named functions in same scope

            function_dict[key] = FunctionTemplate(
                node.name, node, pos_args, kw_args)

        elif(isinstance(node, ast.Import)):
            # print(node.lineno, "import")
            try:
                for i in node.names:
                    import_list.append(ImportTemplate(
                        i.name, node.lineno, node, ast.Import))
            except AttributeError:
                pass

        elif(isinstance(node, ast.ImportFrom)):
            # print(node.lineno, "import from")
            try:
                import_list.append(ImportTemplate(
                    node.module, node.lineno, node, ast.Import))
            except AttributeError:
                pass
    return class_list, function_dict, import_list


def is_always_true(test):
    """
    Function to define cases where conditional test is always true.
    'test' should be ast.Compare type or ast.Constant. Returns truth
    value.
    TODO: Add more always true cases.
    """
    is_true = False
    try:
        if(isinstance(test, ast.Constant) and test.value == True):
            is_true = True
    except AttributeError:
        pass
    return is_true


def ignore_check(code):
    if(code in IGNORE):
        return True
    else:
        return False


def create_msg(code, *args, lineno=-1, lang="FIN"):
    msg = ""
    if(lineno < 0):
        pass
    elif(lang):
        msg = f"{MSG[lang]['LINE'][0]} {lineno}: "

    try:
        msg += MSG[lang][code][0]
    except KeyError:
        msg += MSG[lang]["default"][0]

    try:
        return msg.format(*args)
    except IndexError:
        return MSG[lang]["error_error"][0]


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


def write_file(filepath, content, mode="w", encoding="UTF-8"):
    try:
        with open(filepath, mode=mode, encoding=encoding) as f_handle:
            f_handle.write(content)
    except OSError:
        print("OSError while writing a file", filepath)
    except:
        print("Other error than OSError with file", filepath)
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

