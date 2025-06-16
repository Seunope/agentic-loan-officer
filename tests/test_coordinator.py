import pytest
import asyncio
from src.agents.coordinator import CoordinatorAgent
from src.agents.repayment_predictor import RepaymentPredictorAgent
from src.agents.recommendation import RecommendationAgent
from src.agents.emailer import EmailerAgent

@pytest.fixture
def coordinator():
    repayment_predictor = RepaymentPredictorAgent("mock-model")
    recommendation = RecommendationAgent()
    emailer = EmailerAgent("mock-google-key", "mock-groq-key")
    return CoordinatorAgent(repayment_predictor, recommendation, emailer)

@pytest.mark.asyncio
async def test_coordinator_collects_data(coordinator):
    session_state = coordinator.initialize_session_state()
    message = "I'm 30 years old, male, single, living in Lagos"
    response, new_state = await coordinator.process(message, session_state)
    assert "age" in new_state["fields_collected"]
    assert "gender" in new_state["fields_collected"]
    assert "marital_status" in new_state["fields_collected"]
    assert "location" in new_state["fields_collected"]