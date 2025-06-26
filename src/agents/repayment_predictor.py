from agents import Agent
from src.models.validation_models import RepaymentPredictorSchema
from src.utils.agent_prompt import AgentPrompt

class RepaymentPredictorAgent:
    def __init__(self, model):
        self.agent_prompt = AgentPrompt()
        self.agent = Agent(
            name="Repayment Probability Agent",
            model=model,
            output_type=RepaymentPredictorSchema,
            instructions=self.agent_prompt.repaymentProbabilityInstruction(),
            tools=[]
        )