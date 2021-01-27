"""Library file containing generally used ASPA ast checks."""

import ast

import src.analysers.analysis_utils as au
import src.config.config as cnf

# AST checks
def has_exception_handling(node, denied=cnf.FUNC):
    """ Check to determine if node is inside exception handling."""

    if au.get_parent(node, ast.Try, denied=denied) is None:
       return False
    return True
