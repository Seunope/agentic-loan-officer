# src/agents/coordinator.py
from openai import AsyncOpenAI
from src.utils.agent_prompt import AgentPrompt
from src.utils.nl_extractor import ApplicationExtractor
from src.models.validation_models import LoanApplicationValidator
from agents import Agent, Runner, trace
from pydantic import ValidationError
from typing import Dict, Any
import json
import re

class CoordinatorAgent:
    def __init__(self, repayment_predictor, recommendation, emailer, model="gpt-4o-mini"):
        self.agent_prompt = AgentPrompt()
        self.extractor = ApplicationExtractor()
        self.repayment_predictor = repayment_predictor 
        self.recommendation = recommendation
        self.emailer = emailer
        self.instructions = """
            You are a Nigerian loan application coordinator officer. Your job is to collect and validate information from users who want to apply for a loan. Note all amounts are in Naira.

            Follow these steps:
            1. Collect all required information for the loan application:
               - Age (must be between 19-70)
               - Gender (must be male, female, or other)
               - Marital status (must be single, married, divorced, or widowed)
               - Location (state where the applicant lives in Nigeria)
               - Loan amount (must be greater than 0 and not exceed 1,000,000)
               - Loan tenure in days (must be greater than 6 and not exceed 180 days)

            2. Keep track of what information has been provided and what's still missing.

            3. When a user provides a value, validate it according to the requirements and ask for corrections if needed.

            4. After collecting all required information, summarize the complete application and ask the user to confirm before proceeding.

            5. If the user wants to modify any information, allow them to do so before final confirmation.

            6. After confirmation use the loan_repayment_probability_tool to get the repayment probability score and risk level.

            7. Pass this information to the loan_recommendation_tool to get a recommendation.

            8. When you have the complete analysis and recommendation, hand off to the Email Manager to send the results to the user's email.

            Always be friendly, professional, and helpful throughout the process.
        """
        self.agent = Agent(
            name="Loan Application Coordinator",
            model=model,
            instructions=self.instructions,
            tools=[
                repayment_predictor.agent.as_tool(
                    tool_name="loan_repayment_probability_tool",
                    tool_description="Get loan repayment probability score and risk level"
                ),
                recommendation.agent.as_tool(
                    tool_name="loan_recommendation_tool",
                    tool_description="Get loan recommendation based on application data and repayment probability"
                )
            ],
            handoffs=[emailer.agent]
        )

    async def process(self, message, session_state):
        if session_state is None:
            session_state = self.initialize_session_state()
        
        if session_state.get("email_stage", False):
            return await self.handle_email_stage(message, session_state)
        
        if session_state.get("processing_stage", False):
            return await self.handle_processing_stage(message, session_state)
        
        if session_state.get("confirmation_stage", False):
            return await self.handle_confirmation_stage(message, session_state)
        
        return await self.handle_collection_stage(message, session_state)

    def initialize_session_state(self):
        return {
            "application_data": {},
            "fields_collected": set(),
            "required_fields": {"age", "gender", "marital_status", "location", "amount", "tenure"},
            "confirmation_stage": False,
            "processing_stage": False,
            "email_stage": False,
            "extractor": self.extractor,
            "prediction_result": None,
            "recommendation_result": None,
            "user_email": None
        }

    def format_application_data(self, app_data, fields_collected, required_fields):
        summary = "### Application Progress\n\n"
        if fields_collected:
            summary += "**Collected Information:**\n"
            for field in fields_collected:
                if field in app_data:
                    summary += f"- {field.replace('_', ' ').title()}: {app_data[field]}\n"
            summary += "\n"
        missing = required_fields - fields_collected
        if missing:
            summary += "**Information Still Needed:**\n"
            for field in missing:
                summary += f"- {field.replace('_', ' ').title()}\n"
        return summary

    def create_email_body(self, application_data, prediction_result, recommendation_result):
        return f"""
        # Loan Application Decision

        Dear Applicant,

        Thank you for your loan application. We have completed the review process and here are the details:

        ## Application Details
        - **Age**: {application_data.get('age', 'N/A')}
        - **Gender**: {application_data.get('gender', 'N/A')}
        - **Marital Status**: {application_data.get('marital_status', 'N/A')}
        - **Location**: {application_data.get('location', 'N/A')}
        - **Loan Amount**: ₦{application_data.get('amount', 'N/A')}
        - **Loan Tenure**: {application_data.get('tenure', 'N/A')} days

        ## Risk Assessment
        {prediction_result}

        ## Our Decision
        {recommendation_result}

        If you have any questions about this decision, please don't hesitate to contact us.

        Best regards,
        Loan Agentic Team
        """

    async def handle_email_stage(self, message, session_state):
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, message)
        
        if emails:
            session_state["user_email"] = emails[0]
            email_body = self.create_email_body(
                session_state["application_data"],
                session_state.get("prediction_result", "No prediction available"),
                session_state.get("recommendation_result", "No recommendation available")
            )
            
            with trace("Email Processing"):
                email_prompt = f"""
                Please send a loan application decision email with the following details:
                
                Recipient Email: {session_state["user_email"]}
                
                Email Body:
                {email_body}
                
                Please format this professionally and send it to the recipient.
                """
                run_result = await Runner.run(self.emailer.agent, email_prompt)
                response = f"Thank you! Your loan application summary has been sent to {session_state['user_email']}. You will receive our decision within 2-3 business days.\n\nEmail Status: {run_result.final_output}"

            session_state = self.initialize_session_state()
            return response, session_state
        else:
            return "Please provide a valid email address.", session_state

    async def handle_processing_stage(self, message, session_state):
        try:
            validated = LoanApplicationValidator(**session_state["application_data"])

            with trace("Repayment Prediction"):
                run_result = await Runner.run(
                self.repayment_predictor.agent,  # Use the stored agent object
                self.agent_prompt.userDataPrompt(validated)
                )
                session_state["prediction_result"] = run_result.final_output

            with trace("Loan Recommendation"):
                app_data_str = json.dumps(session_state["application_data"])
                recommendation_input = f"""
                Loan Application Data: {app_data_str}
                Repayment Prediction Result: {session_state['prediction_result']}

                Please provide your recommendation for this loan application.
                """
                run_result = await Runner.run(
                self.recommendation.agent,  # Use the stored agent object
                recommendation_input
                )
                session_state["recommendation_result"] = run_result.final_output

            session_state["processing_stage"] = False
            session_state["email_stage"] = True

            response = f"""
            Loan Application Processing Complete

            Repayment Analysis:
            {session_state['prediction_result']}

            Recommendation:
            {session_state['recommendation_result']}

            Please provide your email address so we can send you the complete application summary and decision.
            """
            return response, session_state

        except ValidationError as e:
            session_state["processing_stage"] = False
            session_state["confirmation_stage"] = False
            return f"Validation Error: {str(e)}\n\nPlease provide the correct information.", session_state

    async def handle_confirmation_stage(self, message, session_state):
        if any(confirm in message.lower() for confirm in ["confirm", "yes", "correct", "submit", "proceed"]):
            session_state["confirmation_stage"] = False
            session_state["processing_stage"] = True
            return await self.handle_processing_stage("process", session_state)

        elif any(modify in message.lower() for modify in ["modify", "change", "edit", "no", "incorrect"]):
            session_state["confirmation_stage"] = False
            return "What information would you like to modify?", session_state

    async def handle_collection_stage(self, message, session_state):
        missing_fields = session_state["required_fields"] - session_state["fields_collected"]
        extracted_data = session_state["extractor"].extract_all_fields(
        message,
        missing_fields,
        session_state["application_data"]
        )

        for field, (value, confidence) in extracted_data.items():
            session_state["application_data"][field] = value
            session_state["fields_collected"].add(field)

        with trace("Loan Coordinator"):
            app_summary = self.format_application_data(
            session_state["application_data"],
            session_state["fields_collected"],
            session_state["required_fields"]
            )

        if extracted_data:
            newly_extracted = "\n\n[SYSTEM INFO: Newly extracted fields]\n"
            for field, (value, confidence) in extracted_data.items():
                newly_extracted += f"- {field}: {value} (confidence: {confidence:.2f})\n"
                enhanced_message = f"{message}\n\n[SYSTEM INFO: Current application state]\n{app_summary}{newly_extracted}"
        else:
            enhanced_message = f"{message}\n\n[SYSTEM INFO: Current application state]\n{app_summary}"

        run_result = await Runner.run(self.agent, enhanced_message)
        agent_response = run_result.final_output

        if session_state["fields_collected"] == session_state["required_fields"] and not session_state["confirmation_stage"]:
            session_state["confirmation_stage"] = True
            confirmation = "\n\n### Complete Application Summary\n\n"

            for field, value in session_state["application_data"].items():
                confirmation += f"- {field.replace('_', ' ').title()}: {value}\n"

            confirmation += "\nIs this information correct? Please confirm to proceed or say 'modify' to make changes."
            agent_response += confirmation

        return agent_response, session_state        