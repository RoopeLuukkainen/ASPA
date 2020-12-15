"""Test file for TK2 check.
TK2 check detects file operations which are not in same function with
file opening and closing.

Include TK1, which is file handle left open.
"""

def another_way():
    try:
        f2 = open("test.txt", "r")
        print(file_operation(f2))
        f2.close()
    except OSError:
        pass
    return None


def opening(name):
    try:
        f = open(name, "r")
    except OSError:
        pass
    return f


def file_operation(f):
    try:
        line = f.readline()
        for i in f:
            print(i)
    except OSError:
        pass
    return line


def closing(f):
    try:
        f.close()
    except OSError:
        pass
    return None


def TK2():
    # Open, operation and close all in different functions.
    fhandle = opening("test.txt")
    line = file_operation(fhandle)
    print(line)
    closing(fhandle)

    # Open and close in same function, operation in different function.
    another_way()
    return None


def paaohjelma():
    # Excepted way
    try:
        f1 = open("test.txt", "w")
        f1.write("qwerty\n")
        f1.close()
    except OSError:
        pass
    TK2()
    return None
paaohjelma()
