"""Test file for MR2-4 check.
MR2-4 check detects global scope function calls which are calling 
functions from library or class.
"""

import math
import datetime

def MR2_4():
    return None

math.sqrt(4)
datetime.datetime.strptime("01.01.2020", "%d.%m.%Y")
# MR2_4()
