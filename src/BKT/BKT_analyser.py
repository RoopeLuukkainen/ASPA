"""BKT analyser file."""

class BayesianKnowledgeTracingAnalyser():
    """
    docstring
    """

    def __init__(self, p_Guess=0.3, p_Slip=0.1, p_T=0.7):
        self.pG = p_Guess
        self.pS = p_Slip
        self.pT = p_T # Acquisition

    def update_Ln(self, pLn: float, correct: int) -> float:
        if(correct):
            a = ((1 - self.pS) * pLn) / (((1 - self.pS) * pLn) + (self.pG * (1 - pLn)))
        else:
            a = (self.pS * pLn) / ((self.pS * pLn) + ((1 - self.pG) * (1 - pLn)))

        pLn = a + (1 - a * self.pT)
        return pLn


if __name__ == "__main__":
    BKTA = BayesianKnowledgeTracingAnalyser()
    test_lists = [
        [1, 1, 1, 1, 1],
        [1, 0, 1, 0, 1],
        [0, 1, 0, 1, 0],
        [1, 0, 0, 1, 0],
        [0, 0, 0, 0, 0],
    ]
    # Ln = 0
    Ln = 0.35
    for test in test_lists:
        for exercise in test:
            Ln = BKTA.update_Ln(Ln, exercise)
        print(Ln, test)