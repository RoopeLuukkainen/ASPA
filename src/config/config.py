"""Configuration file containing predefined constants."""

import ast
import pathlib

DEFAULT_SETTINGS = {
    "root": str(pathlib.Path(__file__).parent.absolute()),
    "language": "FIN",
    "dump_tree": False,
    "console_print": False,
    "file_write": True,
    "GUI_print": True,
    "result_path": str(pathlib.Path(__file__).parent.absolute().joinpath("tarkistukset.txt")),
    "only_leaf_files": False,
    "show_statistics": False,
    "settings_file": "settings.json"
}

# Analysis constants
MAIN_FUNC_NAME = "paaohjelma"

# Add names of special functions which are allowed/denied inside class.
# Use * to match any function names. Allowed overrides denied.
ALLOWED_FUNCTIONS = {"__init__"}
DENIED_FUNCTIONS = {"*"}

# Add function names which are allowed to miss return command.
MISSING_RETURN_ALLOWED = {"__init__"}

# Add keys of ignored error messages
IGNORE = {"PT1", "PK1", "MR5", "AR6-1", "AR6-2"}
GENERAL = 0
ERROR = 1
WARNING = 2
NOTE = 3
GOOD = 4
DEBUG = 5

ELEMENT_ORDER = (# Header comment should be first
                 ((ast.Import, ast.ImportFrom), tuple(), tuple(), "E1"),
                 (ast.Assign, tuple(), tuple(), "E3"),
                 (ast.ClassDef, tuple(), tuple(), "E2"),
                 ((ast.AsyncFunctionDef, ast.FunctionDef), tuple(), (MAIN_FUNC_NAME,), "E4"),
                 (ast.FunctionDef, (MAIN_FUNC_NAME,), tuple(), "E5"),
                 (ast.Expr, (MAIN_FUNC_NAME,), tuple(), "E6")
                )

ALLOWED_ELEMENTS = {ast.Import, ast.ImportFrom, ast.Assign, ast.ClassDef,
                    ast.AsyncFunctionDef, ast.FunctionDef, ast.Expr}

# ELEMENT_TEXT = {
#     "ENG": {
#         "E1": "Imports",
#         "E2": "Class definitions",
#         "E3": "Constants",
#         "E4": "Function definitions",
#         "E5": f"Definition of {MAIN_FUNC_NAME}",
#         "E6": f"{MAIN_FUNC_NAME}() call"
#     },
#     "FIN": {
#         "E1": "Sisällytykset",
#         "E2": "Luokkien määrittelyt",
#         "E3": "Kiintoarvot",
#         "E4": "Aliohjelmien määrittelyt",
#         "E5": f"{MAIN_FUNC_NAME}-määrittely",
#         "E6": f"{MAIN_FUNC_NAME}-kutsu"
#     }
# }

# Analysis category names
CHECKBOX_OPTIONS = ["basic",
                    "function",
                    "file_handling",
                    "data_structure",
                    "library",
                    "exception_handling"
                   ]

TEXT = {
    "FIN": {
        "basic": "Perustoiminnot",
        "function": "Aliohjelmat",
        "file_handling": "Tiedostonkäsittely",
        "data_structure": "Tietorakenteet",
        "library": "Kirjaston käyttö",
        "exception_handling": "Poikkeustenkäsittely",
        "file_error": "Tiedostovirhe", # File error e.g. SyntaxError
        "ASPA_error": "Analysointi virhe"  # Analysing error in ASPA
    },
    "ENG": {
        "basic": "Basic commands",
        "function": "Functions",
        "file_handling": "File handling",
        "data_structure": "Data structures",
        "library": "Library usage",
        "exception_handling": "Exception handling",
        "file_error": "File Error", # File error e.g. SyntaxError
        "ASPA_error": "Analysis error" # Analysing error in ASPA
    }
}

# GUI constants
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


TOOL_NAME = "ASPA - Abstrakti SyntaksiPuu Analysaattori"
TOOL_NAME_SHORT = "ASPA"
BG_COLOR = None #"#bababa" #None # "#383838"
FRAME_COLOR = None #"#ffcfcf"
PAD = 5
LARGE_FONT = "None 12 bold"
NORMAL_FONT = "None 10"
SMALL_FONT = "None 8"
FONT_COLOR = "black"
BD_STYLE = "ridge" #tk.RIDGE # Border style
BD = 2              # Border width

HIGHLIGHT = {
    GOOD: "#00aa00", #""green",
    NOTE: "#0000ff", # "blue",
    WARNING: "#ff7700", #"orange",
    ERROR: "#dd0000" #"red"
}

# THERE ARE ALSO predefined fonts like these
    # TkDefaultFont The default for all GUI items not otherwise specified.
    # TkTextFont    Used for entry widgets, listboxes, etc.
    # TkFixedFont   A standard fixed-width font.
    # TkMenuFont    The font used for menu items.
    # TkHeadingFont A font for column headings in lists and tables.
    # TkCaptionFont A font for window and dialog caption bars.
    # TkSmallCaptionFont    A smaller caption font for subwindows or tool dialogs.
    # TkIconFont    A font for icon captions.
    # TkTooltipFont A font for tooltips.

# Example guide texts
EXAMPLES = {
    "EX0": "Liite 5",
    "EX1": "Tiedon tulostaminen ruudulle",
    "EX2": "Tiedon lukeminen käyttäjältä",
    "EX3": "Valintarakenne",
    "EX4": "Toistorakenteet",
    "EX5": "Aliohjelmat",
    "EX6": "Tiedostoon kirjoittaminen",
    "EX7": "Tiedostosta lukeminen",
    "EX8": "Listan käsittely",
    "EX9": "Monimutkaisempi tietorakenne",
    "EX10": "Poikkeukset",
    "EX11": "Luku 8 asiat kokoava esimerkki",
    "EX12": "Liite 3: Tulkin virheilmoitusten tulkinta"
}

TITLE_TO_EXAMPLES = {
    "basic": ("EX0", "EX1","EX2","EX3","EX4",),
    "function": ("EX0", "EX5",),
    "file_handling": ("EX0", "EX6","EX7",),
    "data_structure": ("EX0", "EX5", "EX8","EX9",),
    "library": ("EX11",),
    "exception_handling": ("EX0", "EX10",),
    "file_error": ("EX12",)
}

# Violation messages
MSG = {
    "ENG": {
        "default": ("Error occured!", ERROR),
        "error_error": ("Error while printing an error message. "
                        + "Probably too few *args.", DEBUG), # Debug
        "type_error": ("Abstract Syntax Tree parameter has wrong type, e.g. None.", DEBUG), # Debug
        "syntax_error": ("File has a syntax error.", ERROR),
        "tool_error": (f"{TOOL_NAME_SHORT} error while analysing the file '{{}}'.", ERROR),
        "PT1": ("Command '{}' is used.", NOTE),
        "PT2": ("Name '{}' contains other than A-Z, 0-9 and underscore characters.", WARNING),
        # "PT2-1": ("Name '{}' is Python keyword.", WARNING), # using keyword actually creates syntax error to ast.parse
        "PT4-1": ("Loop never breaks.", ERROR),
        "PT5": ("Unreachable code after command '{}'.", ERROR),
        "AR1": (f"No function defition for '{MAIN_FUNC_NAME}'.", NOTE),
        "AR2-1": ("Definition of the function '{}' is not at the global scope.", ERROR),
        "AR3": ("Global variable '{}'.", ERROR),
        # "AR3-2": ("Variable or object is used in global scope '{}.{}'.", ERROR), # Works only with objects
        "AR4": ("Recursive function call.", NOTE),
        "AR5-1": ("Function '{}' requires at least {} parameters, but {} given.", ERROR),
        "AR5-2": ("Function '{}' requires at most {} parameters, but {} given.", ERROR),
        "AR5-3": ("In call of function '{}', '{}' is invalid keyword argument.", ERROR),
        "AR6": ("Missing return at the end of the function '{}'.", ERROR),
        "AR6-1": ("Usage of '{}' in function '{}'.", NOTE), # Yield and yield from detection
        "AR6-2": ("Return statement at the middle of the function.", NOTE),
        "AR6-3": ("Missing value from the return-statement.", WARNING),
        "AR6-4": ("Return value is a constant.", NOTE),
        "AR6-5": ("Returning multiple values at once.", NOTE),
        "AR6-6": ("Returning something else than a variable or constant.", NOTE),
        # "AR7": ("<Statement which should not be in global scope.>", WARNING),
        # "MR1": ("Element '{}' should be before '{}'.", WARNING),
        "MR1": ("Statement seem to be in wrong location.", WARNING),
        "MR2-3": ("Function call '{}()' is {} function call in global scope. There "
                + f"should be only one (1) function call '{MAIN_FUNC_NAME}()'.",
                WARNING),
        "MR2-4": ("Function call '{}.{}()' in global scope does not call the"
                + "main function.", WARNING),
        "MR3": ("Module '{}' is imported again.", ERROR),
        "MR3-1": ("From module '{}' function(s) or module(s) are imported again.", WARNING),
        "MR4": ("Import of the module '{}' is not at the global scope.", ERROR),
        "MR5": ("Missing some or all header comments at {} first lines of the file.", WARNING),
        "PK1": ("Error handling has only one (1) except.", NOTE),
        "PK1-1": ("Missing exception type.", WARNING),
        "PK3": ("Missing exception handling from the file opening.", ERROR),
        "PK4": ("Missing exception handling from the file operation '{}.{}'.", ERROR),
        "PK4b": ("Missing exception handling from the file operation '{}'.", ERROR),
        "TK1": ("File handle '{}' is left open.", ERROR),
        "TK1-1": ("In this course usage of '{}' is not recommended.", NOTE),
        "TK1-2": ("File handle '{}' is closed in except-branch.", WARNING),
        "TK1-3": ("Missing parenthesis from file closing '{}.{}'.", ERROR),
        "TK2": ("File operation '{}.{}' is in different function than file open and close.", ERROR),
        "TR2-1": ("Class is being used directly without an object '{}.{}'.", ERROR),
        "TR2-2": ("Missing parenthesis from object creation. Should be '{}()'.", ERROR),
        "TR2-3": ("Class '{}' is not defined in global scope.", ERROR),
        "TR2-4": ("Name of the class '{}' is not in UPPERCASE.", NOTE),
        "OK": (": No violations detected.", GOOD),
        "NOTE": (", violations detected please see", GENERAL),
        "LINE": ("Line", GENERAL),
        "WELCOME": ("In prints **-marking stands for warning, and ++ for note, "
                 + "all others are errors.", GENERAL),
        "NOTE_INFO": ("All messages with this colour are notes.", NOTE),
        "WARNING_INFO": ("All messages with this colour are warnings.", WARNING),
        "ERROR_INFO": ("All messages with this colour are errors.", ERROR)
    },
    "FIN": {
        "default": ("Tapahtui virhe!", ERROR),
        "error_error": ("Virhe tulostettaessa virhettä. Luultavasti "
                      + "liian vähän argumentteja (*args).", DEBUG), # Debug
        "type_error": ("Syntaksipuun parametri on väärää tyyppiä, esim. None.", DEBUG), # Debug
        "syntax_error": ("Tiedostossa on syntaksi virhe.", ERROR),
        "tool_error": (f"{TOOL_NAME_SHORT}:n virhe analysoitaessa tiedostoa '{{}}'.", ERROR),
        "PT1": ("Komentoa '{}' on käytetty.", NOTE),
        "PT2": ("Nimessä '{}' on muita kuin A-Z, 0-9 ja alaviiva merkkejä.", WARNING),
        # "PT2-1": ("Nimi '{}' on Pythonin avainsana.", WARNING), # using keyword actually creates syntax error to ast.parse
        "PT4-1": ("Silmukkaa ei koskaan pysäytetä.", ERROR),
        "PT5": ("Koodirivejä komennon '{}' jälkeen.", ERROR),
        "AR1": (f"Ohjelmasta ei löytynyt määrittelyä '{MAIN_FUNC_NAME}':lle.", NOTE),
        "AR2-1": ("Aliohjelman '{}' määrittely ei ole päätasolla.", ERROR),
        "AR3": ("Globaalimuuttuja '{}'.", ERROR),
        # "AR3-2": ("Muuttujan tai olion globaali käyttö '{}.{}'.", ERROR),
        "AR4": ("Rekursiivinen aliohjelmakutsu.", NOTE),
        "AR5-1": ("Aliohjelma '{}' vaatii vähintään {} kpl parametreja, mutta {} lähetetty.", ERROR),
        "AR5-2": ("Aliohjelma '{}' vaatii enintään {} kpl parametreja, mutta {} lähetetty.", ERROR),
        "AR5-3": ("Aliohjelmakutsussa '{}', '{}' on virheellinen parametrin nimi.", ERROR), # Using word parametri here, not argumentti
        "AR6": ("Aliohjelman '{}' lopusta puuttuu return-komento.", ERROR),
        "AR6-1": ("Käytetään generaattoria '{}' aliohjelmassa '{}'.", NOTE), # Yield and yield from detection
        "AR6-2": ("Keskellä aliohjelmaa on return.", NOTE),
        "AR6-3": ("return-komennosta puuttuu paluuarvo.", WARNING),
        "AR6-4": ("Paluuarvo on vakio.", NOTE),
        "AR6-5": ("Palautetaan useita paluuarvoja.", NOTE),
        "AR6-6": ("Palautetaan jotain muuta kuin muuttujia tai avainsana.", NOTE),
        # "AR7": ("<Komento, jonka ei tulisi olla päätasolla.>", WARNING),
        # "MR1": ("Komennon '{}' pitäisi olla ennen '{}'.", WARNING),
        "MR1": ("Komento vaikuttaisi olevan väärässä kohdin tiedostoa.", WARNING),
        "MR2-3": ("Aliohjelmakutsu '{}()' on {}. aliohjelmakutsu. Pitäisi olla vain "
                + f"yksi (1) aliohjelmakutsu '{MAIN_FUNC_NAME}()'.", WARNING),
        "MR2-4": ("Päätason aliohjelmakutsu '{}.{}()' ei viittaa tiedoston pääohjelmaan.", WARNING),
        "MR3": ("Kirjasto '{}' sisällytetään (eng. import) uudelleen.", ERROR),
        "MR3-1": ("Kirjastosta '{}' sisällytetään sisältöä uudelleen.", WARNING),
        "MR4": ("Kirjaston '{}' sisällytys (eng. import) ei ole päätasolla.", ERROR),
        "MR5": ("Tiedostossa ei ole kaikkia alkukommentteja tiedoston {}"
                + " ensimmäisellä rivillä.", WARNING),
        "PK1": ("Virheenkäsittelyssä vain yksi (1) except.", NOTE),
        "PK1-1": ("Exceptistä puuttuu virhetyyppi.", WARNING),
        "PK3": ("Tiedoston avaamisesta puuttuu poikkeustenkäsittely.", ERROR),
        "PK4": ("Tiedosto-operaatiosta '{}.{}' puuttuu poikkeustenkäsittely.", ERROR),
        "PK4b": ("Tiedosto-operaatiosta '{}' puuttuu poikkeustenkäsittely.", ERROR),
        "TK1": ("Tiedostokahva '{}' on sulkematta.", ERROR),
        "TK1-1": ("Tällä kurssilla '{}':n käyttö ei ole suositeltu rakenne.", NOTE),
        "TK1-2": ("Tiedostokahva '{}' suljetaan except-osiossa.", WARNING),
        "TK1-3": ("Tiedoston sulkukomenosta '{}.{}' puuttuvat sulut.", ERROR),
        "TK2": ("Tiedosto-operaatio '{}.{}' eri aliohjelmassa kuin avaus ja sulkeminen.", ERROR),
        "TR2-1": ("Luokan käyttö suoraan ilman oliota '{}.{}'.", ERROR),
        "TR2-2": ("Olion luonnista puuttuvat sulkeet. Pitäisi olla '{}()'.", ERROR),
        "TR2-3": ("Luokkaa '{}' ei ole määritelty päätasolla.", ERROR),
        "TR2-4": ("Luokan '{}' nimi ei ole kirjoitettu SUURAAKKOSIN.", NOTE),
        "NOTE": (", tyylirikkeitä havaittu, ole hyvä ja katso", GENERAL),
        "OK": (": Ei tunnistettu tyylirikkomuksia.", GOOD),
        "LINE": ("Rivi", GENERAL),
        "WELCOME": ("Tulosteissa **-merkintä tarkoittaa varoitusta ja ++-merkintä ilmoitusta, "
                 + "muut ovat virheitä.", GENERAL),
        "NOTE_INFO": ("Tällä värillä merkityt viestit ovat huomioita.", NOTE),
        "WARNING_INFO": ("Tällä värillä merkityt viestit ovat varoituksia.", WARNING),
        "ERROR_INFO": ("Tällä värillä merkityt viestit ovat virheitä.", ERROR)
    }
}
