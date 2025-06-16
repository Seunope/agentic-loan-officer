import pytest
from src.agents.recommendation import RecommendationAgent

@pytest.fixture
def recommendation():
    return RecommendationAgent()

def test_recommendation_instruction(recommendation):
    assert "loan recommendation specialist" in recommendation.instructions