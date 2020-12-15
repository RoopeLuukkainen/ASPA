"""Test file for MR3-1 check.
MR3-1 check detects extra imports.
Include check MR4 import is not at the global scope.
"""

import math
from datetime import datetime
from random import *  # pylint: disable=unused-wildcard-import
from random import randint

def MR3_1():
    from datetime import timedelta
    return None
from math import sqrt

# MR3_1()
