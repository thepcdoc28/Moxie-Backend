import datetime
from app.services.ai_service import stream_ai_response

class NvidiaModelAgent:
    def __init__(self, model_id):
        self.model_id = model_id
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        self.system_prompt = (
            f"You are Moxie, a highly intelligent and helpful AI assistant (powered by {model_id}). "
            f"Today's date is {current_date}. "
            "Always respond directly, naturally, and conversationally. "
            "NEVER explain your internal processes or mention that you are using tools/functions. "
            "CRITICAL RULES FOR INTERACTION:\n"
            "1. Always be extremely polite, decent, and respectful. Never use hurtful, offensive, or inappropriate language.\n"
            "2. Provide highly informative, detailed, and comprehensive answers. Do not give overly short or brief replies.\n"
            "3. If you need to search for current events, include the current year in your search query to get the most up-to-date information."
        )

    def process_message(self, message_history):
        return stream_ai_response(
            message_history, 
            system_prompt=self.system_prompt, 
            model_id=self.model_id
        )

class DatabaseAgent(NvidiaModelAgent):
    def __init__(self, model_id="meta/llama-3.1-70b-instruct"):
        super().__init__(model_id)
        self.system_prompt = "You are a database expert. Help the user write SQL queries."

def get_agent_for_request(message, model="meta/llama-3.1-70b-instruct"):
    if "sql" in message.lower() or "database" in message.lower():
        return DatabaseAgent(model)
        
    return NvidiaModelAgent(model)
