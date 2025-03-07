# chatbot.py

import spacy
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import requests
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables securely from .env file
load_dotenv()

# Initialize spaCy NLP model for intent recognition
nlp = spacy.load('en_core_web_sm')

# Initialize ChatterBot instance
chatbot = ChatBot('LinkedInChatBot')

# Train chatbot initially (run separately)
def train_bot():
    trainer = ChatterBotCorpusTrainer(chatbot)
    trainer.train('chatterbot.corpus.english')

# Intent recognition function using spaCy NLP model (rule-based)
def recognize_intent(user_input):
    doc = nlp(user_input.lower())
    greeting_keywords = {"hi", "hello", "hey", "greetings"}
    goodbye_keywords = {"bye", "goodbye", "see you"}
    interest_keywords = {"pricing", "services", "demo", "quote", "consultation", "contact"}
    website_keywords = {"website", "web", "link", "site"}

    if any(token.text in greeting_keywords for token in doc):
        return "greeting"
    elif any(token.text in goodbye_keywords for token in doc):
        return "goodbye"
    elif any(token.text in interest_keywords for token in doc):
        return "interest_lead"
    elif any(token.text in {"website", "link", "web"} for token in doc):
        return "website_request"
    else:
        return "general"

# CRM Integration (Example: Salesforce via REST API)
def send_lead_to_salesforce(name, email, message):
    SALESFORCE_API_URL = os.getenv("SALESFORCE_API_URL")
    SALESFORCE_ACCESS_TOKEN = os.getenv("SALESFORCE_ACCESS_TOKEN")

    headers = {
        'Authorization': f'Bearer {os.getenv("SALESFORCE_API_KEY")}',
        'Content-Type': 'application/json'
    }

    data = {
        'FirstName': name.split()[0],
        'LastName': name.split()[-1],
        'Email': f"{name.replace(' ', '').lower()}@example.com",
        'LeadSource': 'LinkedIn Chatbot',
        'Description': f"Inbound lead captured via LinkedIn chatbot on {datetime.now().isoformat()}"
    }

    response = requests.post(
        os.getenv("SALESFORCE_API_ENDPOINT"),
        headers=headers,
        data=json.dumps(data)
    )

    if response.status_code == 201:
        log_event("CRM Integration Success", f"Lead added: {name}")
    else:
        log_error("CRM Integration Failed", response=response.text)

# Analytics & Logging setup
def log_interaction(user_message, bot_response, intent):
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'user_message': user_message,
        'bot_response': bot_response,
        'intent': intent,
    }
    with open('chat_logs.jsonl', 'a') as logfile:
        logfile.write(json.dumps(log_entry) + "\n")

def log_error(error_message, response=""):
    error_entry = {
        'timestamp': datetime.now().isoformat(),
        'error_message': error_message,
        'response': response if response else ""
    }
    with open('error_logs.jsonl', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

# Continuous Retraining (simple example)
def retrain_chatbot(new_conversation_pairs):
    trainer = ChatterBotCorpusTrainer(chatbot)

    # Assume new conversations are stored in a JSONL file called new_conversations.jsonl
    with open('new_training_data.jsonl', 'a') as f:
        for pair in new_conversations:
            f.write(json.dumps(pair) + '\n')

    # Load and retrain periodically (e.g., weekly)
    trainer.train('chatterbot.corpus.english')
    log_interaction("System", "Retrained chatbot with latest data.", "system_update")

# Generate chatbot responses integrated with CRM and logging
def get_bot_response(user_message, user_name="User"):
    intent = recognize_intent(user_message)

    if intent == "greeting":
        response_text = "Hello! Welcome to Prosparity AI. How can I assist you today?"

    elif intent == "goodbye":
        response_text = ("Goodbye! Feel free to visit us anytime at https://prosparityai.com.")

    elif intent == "interest_lead":
        response_text = ("It sounds like you're interested in our offerings! "
                        "Please visit our website at https://prosparityai.com to learn more or schedule a consultation.")

        # Send lead to Salesforce CRM automatically as inbound lead example (dummy name used here)
        send_lead_to_salesforce(name="LinkedIn User")

    elif intent == "website_request":
        response_text = ("You can explore more about us directly at our official website: https://prosparityai.com")

    else:
        response = chatbot.get_response(user_message)

        if response.confidence < 0.6:
            response_text = ("I'm not sure I fully understand your request. "
                            "Please visit https://prosparityai.com for detailed information.")
            intent = "fallback"
        else:
            response_text = str(response)

    # Log interaction details for analytics purposes.
    log_interaction(user_message, response_text, intent)

    return response_text

if __name__ == "__main__":
    print("Training chatbot...")
    train_bot()
    print("Training complete.")