import gradio as gr
from dotenv import load_dotenv
import os
from .agents.coordinator import CoordinatorAgent
from .agents.repayment_predictor import RepaymentPredictorAgent
from .agents.recommendation import RecommendationAgent
from .agents.emailer import EmailerAgent

def main():
    load_dotenv(override=True)
    
    openai_api_key = os.getenv('OPENAI_API_KEY')
    fine_tune_openai = os.getenv('FINE_TUNED_MODEL')
    google_api_key = os.getenv('GOOGLE_API_KEY')
    groq_api_key = os.getenv('GROQ_API_KEY')

    repayment_predictor = RepaymentPredictorAgent(fine_tune_openai)
    recommendation = RecommendationAgent()
    emailer = EmailerAgent(google_api_key, groq_api_key)
    coordinator = CoordinatorAgent(repayment_predictor, recommendation, emailer)

    async def chat(message, history, session_state):
        response, new_session_state = await coordinator.process(message, session_state)
        history = history or []
        history.append((message, response))
        return "", history, new_session_state

    def update_status(session_state):
        if session_state is None:
            return "### Application Status\nStart by providing your information"
        if session_state.get("email_stage", False):
            return "### Application Status\nWaiting for email address"
        elif session_state.get("processing_stage", False):
            return "### Application Status\nProcessing application..."
        elif session_state.get("confirmation_stage", False):
            return "### Application Status\nWaiting for confirmation"
        else:
            return coordinator.format_application_data(
                session_state["application_data"],
                session_state["fields_collected"],
                session_state["required_fields"]
            )

    with gr.Blocks() as demo:
        session_state = gr.State(coordinator.initialize_session_state())
        gr.Markdown("#Loan Agentic Officer (trained on Nigeria Data)")
        
        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(height=500)
                with gr.Row():
                    msg = gr.Textbox(
                        label="Your message",
                        show_label=False,
                        placeholder="Type your message here...",
                        container=False
                    )
                    submit_btn = gr.Button("Submit")
            with gr.Column(scale=1):
                app_status = gr.Markdown("### Application Status\nStart by providing your information")
        
        with gr.Row():
            clear_btn = gr.Button("Start New Application")

        submit_btn.click(chat, [msg, chatbot, session_state], [msg, chatbot, session_state])
        msg.submit(chat, [msg, chatbot, session_state], [msg, chatbot, session_state])
        session_state.change(update_status, session_state, app_status)
        clear_btn.click(
            lambda: (None, coordinator.initialize_session_state()),
            None,
            [chatbot, session_state],
            queue=False
        )

        demo.launch()

if __name__ == "__main__":
    main()