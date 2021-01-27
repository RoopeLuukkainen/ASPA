"""BKT analyser file."""

class BayesianKnowledgeTracingAnalyser():
    """
    docstring
    """

    def __init__(self, P_Guess=0.3, P_Slip=0.1, P_T=0.7):
        self.PG = P_Guess   # Does not know the concept but guess correctly
        self.PS = P_Slip    # Knows the concept but does a mistake
        self.PT = P_T       # Acquisition, i.e. probability to learn

    def update_Ln(self, PLn: float, correct: int) -> float:
        if(correct):
            action = ((1 - self.PS) * PLn) / (((1 - self.PS) * PLn) + (self.PG * (1 - PLn)))
        else:
            action = (self.PS * PLn) / ((self.PS * PLn) + ((1 - self.PG) * (1 - PLn)))

        PLn = action + ((1 - action) * self.PT)
        return PLn

    def update_parameters(self):
        pass
        # P_irs = P_ir * w_is / (P_ir * w_is + (1 - P_ir))
        # where P_ir is a best fitting parameter estimate for the rule across all students
        # and W_is is the corresponding individual difference weight for the student.

def main():
    BKTA = BayesianKnowledgeTracingAnalyser()
    test_lists = [
        [0],
        [0, 0],
        [0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [1],
        [1, 1],
        [1, 1, 1],
        [1, 1, 1, 1],
        [1, 1, 1, 1, 1],
        [1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0],
        [1, 0, 0, 1, 0],
    ]
    for test in test_lists:
        Ln = 0.05
        # Ln = 0.35
        for exercise in test:
            Ln = BKTA.update_Ln(Ln, exercise)
        print(Ln, test)

if __name__ == "__main__":
    main()