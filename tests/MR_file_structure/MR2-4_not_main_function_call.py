"""Test file for MR2-4 check.
MR2-4 check detects global scope function calls which are calling
functions from library or class.

Also MR1 violations for mislocated calls which are otherwise fine.
"""

import math
import datetime
import somelibrary

# This is not okay because somelibrary is not allowed in config files:
# "ALLOWED_LIBRARIES_FOR_CONST"-set
const_var =  somelibrary.somefunction(123)
const_random = random.random() # This is not okay because random is imported

const = math.sqrt(43543) # This is okay
const_pvm = datetime.datetime.strptime("01.01.2020", "%d.%m.%Y") # This is okay

def MR2_4():
    return None

math.sqrt(4)  # These are in wrong place i.e. MR1 -violation
datetime.datetime.strptime("01.01.2020", "%d.%m.%Y")
# MR2_4()
