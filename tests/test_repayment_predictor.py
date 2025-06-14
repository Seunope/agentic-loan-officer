import pytest
from src.agents.repayment_predictor import RepaymentPredictorAgent

@pytest.fixture
def repayment_predictor():
    return RepaymentPredictorAgent("mock-model")

def test_repayment_instruction(repayment_predictor):
    instruction = repayment_predictor.agent_prompt.repaymentProbabilityInstruction()
    assert "Senior Loan Risk Analyst" in instruction
    assert "repaymentProbabilityScore" in instruction