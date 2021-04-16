"""BKT analyser file."""

from typing import Iterable

class BayesianKnowledgeTracingAnalyser():
    """
    Class to handle Bayesian Knowledge Tracing (BKT) Analysis of student
    submissions.
    """

    def __init__(self, p_Guess=0.3, p_Slip=0.1, p_T=0.7, p_L0=0):
        self.pG = p_Guess   # Does not know the concept but guess correctly
        self.pS = p_Slip    # Knows the concept but does a mistake
        self.pT = p_T       # Acquisition, i.e. probability to learn
        self._Ln = p_L0
        self._success_list = []

    @property
    def success_list(self):
        """Getter for read only success_list value."""
        return self._success_list

    @property
    def Ln(self):
        """Getter for read only Ln value."""
        return self._Ln

    def next_correct(self):
        """
        Function to return the probability that next action is correct.
        """
        pass
        # return (self._Ln * (1 - self.pS)) + ((1 - self._Ln) * self.pG)

    def update_Ln(self, success: int):
        self._success_list.append(success)
        pLn = self._Ln
        if success:
            action = ((1 - self.pS) * pLn) / (((1 - self.pS) * pLn) + (self.pG * (1 - pLn)))
        else:
            action = (self.pS * pLn) / ((self.pS * pLn) + ((1 - self.pG) * (1 - pLn)))

        self._Ln = action + ((1 - action) * self.pT)
        return None

    def update_parameters(self):
        pass
        # P_irs = P_ir * w_is / (P_ir * w_is + (1 - P_ir))
        # where P_ir is a best fitting parameter estimate for the rule across
        # all students and W_is is the corresponding individual difference
        # weight for the student.

class Student():
    """
    Class for handling students Bayesian Knowledge Tracing results.
    """

    def __init__(self, student_id):
        self._student_id = student_id
        self.results = {}

    @property
    def student_id(self):
        """Read only getter for student_id value."""
        return self._student_id

    def get_results(self, key=None):
        if key:
            try:
                return self.results[key]
            except KeyError:
                return None
        return self.results

    def add_results(
        self,
        results: Iterable[object],
        key: str,
        success: str
    ) -> None:
        """
        Method to iterate throught results and update Ln values based on
        each result.

        Arguments:
        1. results - Contains result objects - Itrable[object]
        2. key - Name of an attribute which define analysis key/ID - str
        3. success - Name of an attribute which define if result was
           successful or not - str

        Return: None
        """

        for result in results:
            self.add_result(getattr(result, key), int(getattr(result, success)))
        return None

    def add_result(self, key: str, success: int) -> None:
        """Method to update students BKT analysis results."""

        self.results.setdefault(
            key,
            BayesianKnowledgeTracingAnalyser(
                p_Guess=0.3,
                p_Slip=0.1,
                p_T=0.7,
                p_L0=0
            )
        ).update_Ln(success)

        return None


