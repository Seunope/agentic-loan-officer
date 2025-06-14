import pytest
from src.models.validation_models import LoanApplicationValidator
from pydantic import ValidationError

def test_valid_loan_application():
    data = {
        "age": 30,
        "gender": "male",
        "marital_status": "single",
        "location": "Lagos",
        "amount": 50000.0,
        "tenure": 60
    }
    validator = LoanApplicationValidator(**data)
    assert validator.age == 30
    assert validator.amount == 50000.0

def test_invalid_loan_application():
    with pytest.raises(ValidationError):
        LoanApplicationValidator(
            age=15,
            gender="invalid",
            marital_status="unknown",
            location="Lagos",
            amount=2000000.0,
            tenure=5
        )