"""
File for all the detected structures for structure analyser.
TODO: Split to smaller files, e.g. based on major ID code.
"""

############################################################
# STRUCTUREs
############################################################

# VARIABLES

# string and substring
bar = "foo"
sub_bar = bar[1:5:2]
index_bar = bar[0]

foo = [[1, 2], [3, 4]]
index_foo = foo[0][1]

# COMPARE
# Booleans
1 and 2
1 or 2 or 3


# Values
1 == 2
1 != 2
1 < 2
1 > 2
1 <= 2
1 >= 2
1 is 2
1 is not 2
1 in [2]
1 not in [2]

# Loops
for i in [1,2]:
    pass
else:
    print("1")

while True:
    break
else:
    pass

[i for i in (1, 2)]
(i for i in (1, 2))
{i for i in (1, 2)}
{i:i for i in (1, 2)}

# Conditions
1 if True else 2

# Case 1
if True:
    pass
elif False:
    pass

# Case 2
if True:
    pass
else:
    if False:
        pass

# Case 3
if True:
    pass
elif False:
    pass
elif True:
    pass
else:
    a = 1

# Functions
def func1(): return "None"
def func3(): return None
def fun4(): return
async def func2(*ag, a=1): yield 2
lambda x: x

# Imports
import math
from random import randint
from datetime import * # pylint: disable=unused-wildcard-import

# File handling
f = open("a.txt", "r")
f.read()
f.readline()
f.readlines()
f.close()

with open("b.txt", "w") as f:
    f.write()
    f.writelines()

# Data structures
[]
{}
(1,)
{1}

list()
dict()
tuple()
set()

# Class
class LUOKKA():
    pass

LUOKKA() # TODO object creation, done in original checks

# Exception handling
try:
    pass
except Exception:
    pass
else:
    pass
finally:
    pass

try: pass
except: pass
finally: pass