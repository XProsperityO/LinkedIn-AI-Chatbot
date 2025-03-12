# chatbot.py

import spacy
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
from typing import Dict, List, Optional, Union, Any
import requests
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
import os
import config
import time
import random

# Load environment variables securely from .env file
load_dotenv()

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=config.LOG_FILE,
    filemode='a'
)
logger = logging.getLogger(__name__)

class LinkedInChatBot:
    """
    AI chatbot for LinkedIn marketing and sales conversations.
    Uses ChatterBot with custom training data focused on marketing.
    """

    def __init__(self, name: str = "LinkedInAIBot"):
        """
        Initialize the chatbot.

        Args:
            name: Name of the chatbot
        """
        self.name = name
        self.bot = None
        self.conversation_history = {}
        self.trained = False

        # Load spaCy model for NLP tasks
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy model for NLP")
        except OSError:
            logger.warning("spaCy model not found. Downloading...")
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

        self.initialize_bot()

    def initialize_bot(self) -> None:
        """Initialize the chatbot with appropriate settings."""
        try:
            self.bot = ChatBot(
                self.name,
                storage_adapter="chatterbot.storage.SQLStorageAdapter",
                database_uri=f"sqlite:///{config.DB_PATH}",
                logic_adapters=[
                    {
                        "import_path": "chatterbot.logic.BestMatch",
                        "default_response": "I'm not sure how to respond to that.",
                        "maximum_similarity_threshold": 0.65
                    },
                    {
                        "import_path": "chatterbot.logic.MathematicalEvaluation"
                    }
                ],
                preprocessing=["chatterbot.preprocessors.clean_whitespace"]
            )
            logger.info(f"Initialized chatbot: {self.name}")
        except Exception as e:
            logger.error(f"Error initializing chatbot: {str(e)}")
            raise

    def train(self, training_data: Optional[List[List[str]]] = None) -> None:
        """
        Train the chatbot using corpus data and optionally custom data.

        Args:
            training_data: Optional list of conversation pairs for training
        """
        if not self.bot:
            logger.error("Bot not initialized. Cannot train.")
            return

        try:
            # Train with corpus data first
            corpus_trainer = ChatterBotCorpusTrainer(self.bot)
            corpus_trainer.train("chatterbot.corpus.english")
            logger.info("Completed corpus training")

            # If custom training data provided, train with that
            if training_data:
                list_trainer = ListTrainer(self.bot)
                for conversation in training_data:
                    list_trainer.train(conversation)

            self.trained = True
            logger.info("Chatbot training complete")
        except Exception as e:
            logger.error
