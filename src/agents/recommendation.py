from agents import Agent

class RecommendationAgent:
    def __init__(self, model="gpt-4o-mini"):
        self.instructions = """
        You are a loan recommendation specialist. Based on the loan application data and repayment probability analysis, provide a clear recommendation on whether to approve, reject, 
        or conditionally approve the loan application. Include specific reasons for your decision. 
        Note, loan tenures are in days.
        """
        self.agent = Agent(
            name="Loan Application Recommendation Agent",
            model=model,
            instructions=self.instructions,
            tools=[]
        )