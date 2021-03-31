"""File for any template class used in ASPA. Templates are used to store
multivalue information about stored elements, i.e. they are often struc
like objects.
"""

 # TODO Move ViolationTemplate somewhere else because it is not a Template
 # anymore but rather a real class. Same time utils are not needed anymore.
from .. import utils_lib as utils

class NodeTemplate():
    """General template class for any ast node."""

    def __init__(self, name, lineno, astree):
        self._name = name
        self._astree = astree # AST of the node
        self._lineno = lineno

    @property
    def name(self):
        return self._name

    @property
    def astree(self):
        return self._astree

    @property
    def lineno(self):
        return self._lineno

class FunctionTemplate(NodeTemplate):
    """Template class for functions found during preanalysis."""

    def __init__(self, name, lineno, astree, pos_args, kw_args):
        NodeTemplate.__init__(self, name, lineno, astree)
        self._pos_args = pos_args    # Positional arguments before *args
        self._kw_args = kw_args      # Keyword arguments before **kwargs

    @property
    def pos_args(self):
        return self._pos_args

    @property
    def kw_args(self):
        return self._kw_args

class ImportTemplate(NodeTemplate):
    """Template class for imports found during preanalysis."""

    def __init__(self, name, lineno, astree, import_from=False):
        NodeTemplate.__init__(self, name, lineno, astree)
        self._import_from = import_from

    @property
    def import_from(self):
        return self._import_from

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

        self._vid = vid          # Violation identifier
        # self.vtype = vtype      # Violation type
        self._args = args
        self._lineno = lineno
        self._status = status    # Violation status True/False
        self._msg_tuple = None
        self._lang = None

    @property
    def vid(self):
        return self._vid

    @property
    def args(self):
        return self._args

    @property
    def status(self):
        return self._status

    @property
    def lineno(self):
        return self._lineno

    def get_msg(self, lang):
        """
        Return a violation message as a string. Violation message
        is currently constructed in utils lib.
        """

        if self._msg_tuple is None or lang != self._lang:
            self._lang = lang
            self._msg_tuple = utils.create_msg(
                self._vid,
                *self._args,
                lineno=self._lineno,
                lang=self._lang
            )

        return self._msg_tuple


class FilepathTemplate():
    """Template class for filepaths found during directory crawling."""

    def __init__(self, path, student=None, week=None, exercise=None, course=None):
        self._path = path # Pathlib object
        self._filename = path.name
        self._student = student
        self._exercise = exercise
        self._week = week
        self._course = course

    @property
    def path(self):
        return self._path

    @property
    def filename(self):
        return self._filename

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


class FilehandleTemplate(NodeTemplate):
    """Template class for filehandles found during file analysis."""

    def __init__(self, name, lineno, astree, closed=0):
        NodeTemplate.__init__(self, name, lineno, astree)
        self._closed = closed

    @property
    def closed(self):
        return self._closed

    @property
    def opened(self):
        return self._lineno

    @property
    def filehandle(self):
        return self._name

    def set_closed(self, closing_line):
        # If _closed is != 0 it is already closed. The first closing is
        # interesting and therefore only that is stored.
        if self._closed == 0:
            self._closed = closing_line