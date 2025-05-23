from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any



class LoanRequestValidator(BaseModel):
    maritalStatus: str = Field(..., description="Marital status of the applicant")
    gender: str = Field(..., description="Gender of the applicant")
    state: str = Field(..., description="Location of the applicant (city)")
    age: int = Field(..., description="Age of the applicant")
    loanAmount: int = Field(..., description="Requested loan amount")
    tenorInDays: int = Field(..., description="Loan tenure in days")


class LoanApplicationValidator(BaseModel):
    age: int = Field(..., description="Age of the applicant", gt=18, lt=100)
    gender: str = Field(..., description="Gender of the applicant", pattern="^(male|female|other)$")
    marital_status: str = Field(..., description="Marital status of the applicant", pattern="^(single|married|divorced|widowed)$")
    location: str = Field(..., description="City where the applicant lives", min_length=2, max_length=50)
    amount: float = Field(..., description="Loan amount requested", gt=0)
    tenure: int = Field(..., description="Loan tenure in days", gt=6, le=180)  # covers both <7 and >180

    @field_validator('amount')
    def check_max_amount(cls, v):
        if v > 1000000:
            raise ValueError('Loan amount cannot exceed 1,000,000')
        return v

# class LoanApplicationValidator(BaseModel):
#     age: int = Field(..., description="Age of the applicant", gt=18, lt=100)
#     gender: str = Field(..., description="Gender of the applicant", pattern="^(male|female|other)$")
#     marital_status: str = Field(..., description="Marital status of the applicant", pattern="^(single|married|divorced|widowed)$")
#     location: str = Field(..., description="City where the applicant lives", min_length=2, max_length=50)
#     amount: float = Field(..., description="Loan amount requested", gt=0)
#     tenure: int = Field(..., description="Loan tenure in days", gt=14, le=180)

#     @field_validator('amount')
#     def validate_amount(cls, v):
#         if v > 1000000:  # Example limit
#             raise ValueError('Loan amount cannot exceed 1,000,000')
#         return v
    
#     @field_validator('tenure')
#     def validate_amount(cls, v):
#         if v > 180:  # Example limit
#             raise ValueError('Loan tenure cannot exceed 180 days')
#         return v
#     @field_validator('tenure')
#     def validate_amount(cls, v):
#         if v < 7:  # Example limit
#             raise ValueError('Loan tenure cannot be less than 7 days')
#         return v
