"""File for any template class used in ASPA. Templates are used to store
multivalue information about stored elements, i.e. they are often struc
like objects.
"""

class NodeTemplate():
    """General template class for any ast node."""

    def __init__(self, name, lineno, astree):
        self.name = name
        self.astree = astree # AST of the node
        self.lineno = lineno

    # @property
    # def name(self):

# TODO add property for each variable, now they are referred directly by
# name.

class FunctionTemplate(NodeTemplate):
    """Template class for functions found during preanalysis."""

    def __init__(self, name, lineno, astree, pos_args, kw_args):
        NodeTemplate.__init__(self, name, lineno, astree)
        self.pos_args = pos_args    # Positional arguments before *args
        self.kw_args = kw_args      # Keyword arguments before **kwargs


class ImportTemplate(NodeTemplate):
    """Template class for imports found during preanalysis."""

    def __init__(self, name, lineno, astree, import_from=False):
        NodeTemplate.__init__(self, name, lineno, astree)
        self.import_from = import_from


class ClassTemplate(NodeTemplate):
    """Template class for classes found during preanalysis."""

    def __init__(self, name, lineno, astree):
        NodeTemplate.__init__(self, name, lineno, astree)


class GlobalTemplate(NodeTemplate):
    """Template class for global variables found during preanalysis."""

    def __init__(self, name, lineno, astree):
        NodeTemplate.__init__(self, name, lineno, astree)


class CallTemplate(NodeTemplate):
    """Template class for (function or class) calls found during
    preanalysis.
    """

    def __init__(self, name, lineno, astree):
        NodeTemplate.__init__(self, name, lineno, astree)


class ObjectTemplate(NodeTemplate):
    """Template class for objects used in data structure analysis."""

    def __init__(self, name, lineno, astree):
        NodeTemplate.__init__(self, name, lineno, astree)


class ViolationTemplate():
    """Template class for violations found during any analysis."""

    def __init__(self, vid, args, lineno, status):

        self.vid = vid          # Violation identifier
        # self.vtype = vtype      # Violation type
        self.args = args
        self.lineno = lineno
        self.status = status    # Violation status True/False


        def get_msg(self):
            """Return a violation message as a string. Violation message
            is constructed based on self.vid, self.lineno and
            self.vtype.
            """

            msg = "msg"          # Violation message
            return msg


class FilepathTemplate():
    """Template class for filepaths found during directory crawling."""

    def __init__(self, path, student=None, week=None, exercise=None, course=None):
        self._path = path
        self._student = student
        self._exercise = exercise
        self._week = week
        self._course = course

    @property
    def path(self):
        return self._path

    @property
    def student(self):
        return self._student

    @property
    def exercise(self):
        return self._exercise

    @property
    def week(self):
        return self._week

    @property
    def course(self):
        return self._course