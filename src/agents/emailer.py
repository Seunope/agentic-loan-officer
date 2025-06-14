# src/agents/emailer.py
from agents import Agent, function_tool, OpenAIChatCompletionsModel
from openai import AsyncOpenAI
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import os
from typing import Dict

# Define send_html_email as a standalone function
@function_tool
def send_html_email(subject: str, html_body: str, recipient_email: str) -> Dict[str, str]:
    """Send out an email with the given subject and HTML body to the recipient"""
    try:
        sg = SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        from_email = Email("seunope2004@gmail.com")
        to_email = To(recipient_email)
        content = Content("text/html", html_body)
        mail = Mail(from_email, to_email, subject, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        print('Email sent successfully', response.status_code)
        return {"status": "success", "message": f"Email sent to {recipient_email}"}
    except Exception as e:
        print(f'Error sending email: {str(e)}')
        return {"status": "error", "message": f"Failed to send email: {str(e)}"}

class EmailerAgent:
    def __init__(self, google_api_key, groq_api_key, model="gpt-4o-mini"):
        self.gemini_client = AsyncOpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/", api_key=google_api_key)
        self.groq_client = AsyncOpenAI(base_url="https://api.groq.com/openai/v1", api_key=groq_api_key)
        
        self.subject_instructions = """
        You are an expert at writing compelling email subjects for loan applications.
        Write a clear, professional subject line that conveys the loan application status/decision.
        Keep it concise and informative.
        """
        
        self.html_instructions = """
        You are an expert at converting text to professional HTML emails.
        Convert the given text/markdown to a clean, professional HTML email with:
        - Proper structure with headers and sections
        - Clear formatting for loan details
        - Professional styling
        - Mobile-friendly layout
        Use simple, clean HTML that renders well across email clients.
        """
        
        self.email_instructions = """
        You are a professional email formatter and sender for loan applications.
        
        Your process:
        1. First, use the subject_writer tool to create an appropriate subject line for the loan application email
        2. Then, use the html_converter tool to convert the email body to professional HTML format
        3. Finally, use the send_html_email tool to send the email with the subject, HTML body, and recipient email
        
        Always ensure the email is professional, clear, and contains all relevant loan application information.
        """
        
        self.subject_writer = Agent(
            name="Llama 3.2 Agent",
            instructions=self.subject_instructions,
            model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=self.gemini_client)
        )
        
        self.html_converter = Agent(
            name="Gemini Agent",
            instructions=self.html_instructions,
            model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=self.gemini_client)
        )
        
        self.email_tools = [
            self.subject_writer.as_tool(tool_name="subject_writer", tool_description="Write a subject for loan email"),
            self.html_converter.as_tool(tool_name="html_converter", tool_description="Convert a text email body to an HTML email body"),
            send_html_email 
        ]
        
        self.agent = Agent(
            name="Email Manager",
            instructions=self.email_instructions,
            tools=self.email_tools,
            model=model,
            handoff_description="Convert an email to HTML and send it"
        )