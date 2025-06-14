import pytest
from src.agents.emailer import EmailerAgent

@pytest.fixture
def emailer():
    return EmailerAgent("mock-google-key", "mock-groq-key")

def test_emailer_initialization(emailer):
    assert emailer.agent.name == "Email Manager"
    assert len(emailer.email_tools) == 3