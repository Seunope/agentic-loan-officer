from agents import Agent
from ..utils.agent_prompt import AgentPrompt

class RepaymentPredictorAgent:
    def __init__(self, model):
        self.agent_prompt = AgentPrompt()
        self.agent = Agent(
            name="Repayment Probability Agent",
            model=model,
            instructions=self.agent_prompt.repaymentProbabilityInstruction(),
            tools=[]
        )