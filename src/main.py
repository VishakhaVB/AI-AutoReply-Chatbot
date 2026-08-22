import os
import time
import logging
from src.automation import WhatsAppAutomation
from src.ai_reply import GeminiReplyGenerator
from src.utils import ChatAnalyzer

class AutoReplyBot:
    """
    Coordinates chat automation, history analysis, and AI response generation.
    
    Periodically polls the chat window, checks for new incoming messages from
    other users, and automatically sends AI-generated replies using Gemini.
    """

    def __init__(self) -> None:
        """
        Initializes the bot, instantiating the required subsystem modules.
        """
        logging.info("Initializing AutoReplyBot subsystems...")
        self.automation = WhatsAppAutomation()
        self.generator = GeminiReplyGenerator()
        self.analyzer = ChatAnalyzer()
        
        # Track the last successfully replied message ID to avoid duplicate actions
        self.last_processed_message_id: str = ""

    def process_chat(self) -> None:
        """
        Performs a single cycle of checking, analyzing, and replying to chat history.
        """
        # Step 1: Copy chat history to clipboard
        chat_history = self.automation.copy_chat_history()
        
        # Step 2: Extract details of the last message
        last_message_info = self.analyzer.extract_last_message(chat_history)
        sender = last_message_info.get("sender")
        message_body = last_message_info.get("message")
        
        if not sender or not message_body:
            logging.info("No valid messages parsed from history.")
            return

        # Generate a unique hash for the latest message
        message_id = self.analyzer.generate_message_id(chat_history)
        
        # Step 3: Ignore if it's my own message
        my_name = os.getenv("MY_NAME", "Me")
        if self.analyzer.is_last_message_from_user(chat_history, my_name):
            logging.info(f"Last message is from user '{sender}' (myself). Ignoring.")
            return
            
        # Step 4: Ignore duplicate/already processed messages
        if self.analyzer.is_duplicate_message(message_id, self.last_processed_message_id):
            logging.debug("Last message is already processed. Ignoring.")
            return

        logging.info(f"New incoming message detected from '{sender}': '{message_body}'")

        # Step 5: Generate AI reply
        ai_reply = self.generator.generate_reply(chat_history)
        logging.info(f"Generated AI response: '{ai_reply}'")

        # Step 6: Send reply
        self.automation.focus_message_box()
        self.automation.send_message(ai_reply)
        logging.info("AI response sent successfully.")

        # Step 7: Save latest message ID to prevent infinite loops
        self.last_processed_message_id = message_id

    def run(self) -> None:
        """
        Runs the main execution loop, polling the chat window periodically.
        """
        logging.info("Starting AutoReplyBot loop...")
        
        # Load polling interval configuration (defaulting to 5 seconds)
        polling_interval = float(os.getenv("POLLING_INTERVAL_SECONDS", "5.0"))
        
        # Focus on the WhatsApp chat window at startup
        try:
            self.automation.open_whatsapp()
        except Exception as e:
            logging.error(f"Failed to focus WhatsApp window on startup: {e}")
            # Continue execution loop in case window is already open

        logging.info(f"AutoReplyBot is running. Polling interval: {polling_interval} seconds.")
        
        while True:
            try:
                # Select the chat log area
                self.automation.select_chat_area()
                # Process the selected chat log
                self.process_chat()
            except Exception as e:
                # Handle exceptions gracefully to prevent the loop from crashing
                logging.error(f"Error encountered in bot run cycle: {e}", exc_info=True)
                
            # Sleep until the next polling cycle
            time.sleep(polling_interval)

if __name__ == "__main__":
    # Configure the standard logging output structure
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    try:
        bot = AutoReplyBot()
        bot.run()
    except Exception as e:
        logging.critical(f"Failed to start AutoReplyBot: {e}", exc_info=True)