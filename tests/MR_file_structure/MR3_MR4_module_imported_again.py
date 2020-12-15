"""Test file for MR3 check.
MR3 check detects extra imports.
Include check MR4 import is not at the global scope.
"""

import math
import datetime

def MR3():
    import datetime
    return None
import math

# MR3()
