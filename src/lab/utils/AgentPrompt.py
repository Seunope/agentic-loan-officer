
from .ValidationModels import LoanApplicationValidator


class AgentPrompt:
    # def __init__(self, dto: LoanRequestValidator):

        # self.dto = dto 
        # self.prompt = f"""User Details:
        #     - Marital Status: {self.dto.maritalStatus}
        #     - Gender: {self.dto.gender}
        #     - Location: {self.dto.state}, Nigeria
        #     - Age: {self.dto.age}
        #     - Loan Amount: {self.dto.loanAmount}
        #     - Loan Tenure: {self.dto.tenorInDays} days.

        #     """

    def repaymentProbabilityInstruction(self):
        """
        Predicts the loan repayment coefficient for an applicant
        using a fine-tuned OpenAI model.
        """

        system_message = """
            **Role**: Senior Loan Risk Analyst at a Tier-1 African Bank

            **Task**: Predict the repayment probability score (0-99 scale). Provide results in JSON format.

            **Key Rules**:
            - ABSOLUTE RULE: Never predict 100 (maximum allowed is 99)
            - Typical range: 20-95
            - Interpretation: Lower repayment probability scores indicate higher default risk
            - High risk (0-40),  medium risk (41-70) acceptable risk (71-99)

            **Output Format**:
            {
                "repaymentProbabilityScore": [integer 0-99],
                "riskLevel": [string: "high", "medium", or "acceptable"]
            }

            """
        return system_message

        # messages = [
        #     {
        #         "role": "system",
        #         "content": system_message,
        #     },
        #     {
        #         "role": "user",
        #         "content": self.prompt
        #     },
        #     {
        #         "role": "assistant",
        #         "content": "Output is"
        #     }
        # ]

    def userDataPrompt(self, dto: LoanApplicationValidator):
        print('dto', dto)
        user_prompt = f"""User Details:
            - Marital Status: {dto.marital_status}
            - Gender: {dto.gender}
            - Location: {dto.location}, Nigeria
            - Age: {dto.age}
            - Loan Amount: {dto.amount}
            - Loan Tenure: {dto.tenure} days.

            Output is
            """
        print('user_prompt', user_prompt)

        return user_prompt


    def _get_recommendation(self, score):
        system_message = """
            **Role**: Senior Loan Risk Analyst at a Tier-1 African Bank

            **Style**:
            - Professional banker's tone - confident, concise, factual

            **Task**: Base on user loan data and repayment probability score (0-99 percent), give detail recommendation with explanation for a loan officer and provide results in JSON format.

            **Key Rules**:
            - Interpretation: Lower repayment probability scores indicate higher default risk
            - Note that repayment probability scores are based on previous users loan data and demography. Let this reflect in your recommendation.

            **Recommendation Guidelines**:
            - If high risk (0-40): Suggest specific loan amount (₦) and tenure 
            - If medium risk (41-70): Provide cautionary approval with conditions 
            - If acceptable risk (71-99): Provide positive reinforcement
        

            **Output Format**:
            {
                "repaymentProbabilityScore": [integer 0-99],
                "recommendation": [string based on risk level],
                "riskLevel": [string: "high", "medium", or "acceptable"]
            }
            
            """
        prompt = self.prompt + f"\n Repayment probability scores: {score}"

        messages = [
                {
                    "role": "system",
                    "content": system_message,
                },
                {
                    "role": "user",
                    "content": prompt
                },
                {
                    "role": "assistant",
                    "content": "Output is"
                }
            ]

    
        response = self.openai.chat.completions.create(
            model="gpt-4o-mini", 
            messages=messages,
            seed=42,
            # max_tokens=5
        )
        reply = response.choices[0].message.content
        # print('Output:', reply)
        return reply
    




