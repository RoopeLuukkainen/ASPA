"""Library file containing generally used ASPA ast checks."""

import ast

import src.analysers.analysis_utils as au

# Constants
FUNC = (ast.FunctionDef, ast.AsyncFunctionDef)
CLS_FUNC = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
LOOP = (ast.For, ast.While)

# AST checks
def has_exception_handling(node, denied=FUNC):
    """ Check to determine if node is inside exception handling."""

    if au.get_parent(node, ast.Try, denied=denied) is None:
       return False
    return True
