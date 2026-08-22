import os
import time
import logging
from src.automation import WhatsAppAutomation
from src.utils import ChatAnalyzer
from src.database.memory import MemoryManager
from src.analyzer import ConversationAnalyzer
from src.safety import SafetyGuard

class AutoReplyAssistant:
    """
    Coordinates the execution flow of the AI chatbot:
    - Screen interaction via desktop GUI automation
    - Text extraction and semantic parsing
    - SQLite persistence of user preferences and chat history
    - Sentiment and language classification
    - Safe generation and dispatch of replies
    """

    def __init__(self) -> None:
        """
        Initializes the assistant and instantiates its supporting subsystems.
        """
        logging.info("Initializing AutoReplyAssistant subsystems...")
        self.automation = WhatsAppAutomation()
        self.chat_utils = ChatAnalyzer()
        self.memory = MemoryManager()
        self.analyzer = ConversationAnalyzer()
        self.safety = SafetyGuard()
        
        # Track the last successfully replied message ID to avoid duplicate actions
        self.last_processed_message_id: str = ""

    def process_chat(self) -> None:
        """
        Executes one complete check-and-reply cycle.
        """
        logging.info("Starting new chat analysis cycle...")

        # Step 2: Copy the latest chat
        chat_history = self.automation.copy_chat_history()
        
        # Step 3: Extract the last message
        last_message = self.chat_utils.extract_last_message(chat_history)
        sender = last_message.get("sender")
        message_body = last_message.get("message")
        
        if not sender or not message_body:
            logging.info("No valid messages found in the active chat area.")
            return

        # Step 5: Generate message ID for duplicate checking
        message_id = self.chat_utils.generate_message_id(chat_history)

        # Step 4: Ignore my own messages
        my_name = os.getenv("MY_NAME", "Me")
        if self.chat_utils.is_last_message_from_user(chat_history, my_name):
            logging.info(f"Last message was sent by '{sender}' (myself). Ignoring.")
            return

        # Step 5 (continued): Ignore duplicate messages using message ID
        if self.chat_utils.is_duplicate_message(message_id, self.last_processed_message_id):
            logging.debug("Latest message is a duplicate (already processed). Ignoring.")
            return

        logging.info(f"New incoming message from '{sender}': '{message_body}'")

        # Step 6: Load the user's profile from SQLite
        user_profile = self.memory.get_user(sender)
        if not user_profile:
            logging.info(f"No existing database profile found for '{sender}'. Registering defaults.")
            # Set default preferences: English, Casual
            self.memory.save_or_update_user(sender, language="English", tone="Casual")
            user_profile = self.memory.get_user(sender)
            
        logging.info(f"User profile context loaded: {user_profile}")

        # Step 7: Detect language and emotion
        analysis = self.analyzer.analyze(message_body, relationship="friend")
        detected_lang = analysis.get("language", "English")
        detected_emotion = analysis.get("emotion", "Neutral")
        logging.info(f"Profile analysis complete. Language: '{detected_lang}', Emotion: '{detected_emotion}'")

        # Step 8: Generate three reply options (casual, funny, professional)
        reply_options = self.safety.generate_three_replies(chat_history, user_profile)
        casual_reply = reply_options.get("casual")
        
        if not casual_reply:
            logging.warning("No valid casual reply generated. Skipping cycle.")
            return
            
        logging.info(f"Generated reply candidates: {reply_options}")

        # Step 9: Run SafetyGuard checks on the candidate reply
        logging.info(f"Running SafetyGuard evaluation on candidate reply: '{casual_reply}'")
        risk_result = self.safety.check_risk(casual_reply)
        is_safe = self.safety.should_send(risk_result)

        # Step 10: If safe, automatically send the Casual reply
        if is_safe:
            logging.info(f"Safety status: SAFE. Sending casual reply to '{sender}'...")
            self.automation.focus_message_box()
            self.automation.send_message(casual_reply)
            
            # Step 11: Save the conversation into SQLite
            self.memory.save_conversation(sender, message_body, casual_reply)
            logging.info(f"Conversation saved to database for user '{sender}'.")
        else:
            logging.warning(
                f"Safety status: BLOCKED. Reply violated safety policies.\n"
                f"Classification: {risk_result.get('classification')}\n"
                f"Reason: {risk_result.get('reason')}"
            )

        # Update the processed message ID (regardless of safety result) to prevent reprocessing
        self.last_processed_message_id = message_id

    def run(self) -> None:
        """
        Runs the main loop checking for new chat history at regular intervals.
        """
        logging.info("Starting AutoReplyAssistant daemon service...")
        
        # Pull check interval from environment settings
        polling_interval = float(os.getenv("POLLING_INTERVAL_SECONDS", "5.0"))
        
        # Step 1: Open WhatsApp Web/App window
        try:
            self.automation.open_whatsapp()
        except Exception as e:
            logging.error(f"Failed to focus/open WhatsApp: {e}")
            # Continue running in case the chat window is already visible/active

        logging.info(f"Daemon started. Polling every {polling_interval} seconds.")
        
        while True:
            try:
                # Select the chat window area
                self.automation.select_chat_area()
                # Run main parse and reply pipeline
                self.process_chat()
            except Exception as e:
                # Keep the loop running despite errors
                logging.error(f"Error in execution cycle: {e}", exc_info=True)
                
            # Wait for the next check interval
            time.sleep(polling_interval)

if __name__ == "__main__":
    # Configure standardized logging output structure
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    try:
        assistant = AutoReplyAssistant()
        assistant.run()
    except Exception as e:
        logging.critical(f"Failed to start the AutoReplyAssistant service: {e}", exc_info=True)