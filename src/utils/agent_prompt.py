from src.models.validation_models import LoanApplicationValidator

class AgentPrompt:
    def repaymentProbabilityInstruction(self):
        return """
        **Role**: Senior Loan Risk Analyst at a Tier-1 African Bank

        **Task**: Predict the repayment probability score (0-99 scale). Provide results in JSON format.

        **Key Rules**:
        - ABSOLUTE RULE: Never predict 100 (maximum allowed is 99)
        - Typical range: 20-95
        - Interpretation: Lower repayment probability scores indicate higher default risk
        - High risk (0-40), medium risk (41-70), acceptable risk (71-99)

        **Output Format**:
        {
            "repaymentProbabilityScore": [integer 0-99],
            "riskLevel": [string: "high", "medium", or "acceptable"]
        }
        """

    def userDataPrompt(self, dto: LoanApplicationValidator):
        return f"""User Details:
            - Marital Status: {dto.marital_status}
            - Gender: {dto.gender}
            - Location: {dto.location}, Nigeria
            - Age: {dto.age}
            - Loan Amount: {dto.amount}
            - Loan Tenure: {dto.tenure} days.

            Output is
        """