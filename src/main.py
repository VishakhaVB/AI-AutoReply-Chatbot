import os
import time
import logging
import pyautogui
import pyperclip
from src.automation import WhatsAppAutomation
from src.utils import ChatAnalyzer
from src.database.memory import MemoryManager
from src.analyzer import ConversationAnalyzer
from src.safety import SafetyGuard
from src.config import settings

MY_NAME = "Vishakha~4✨"


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
        # Step 4: Copy Chat
        chat_history = self.automation.copy_chat_history()
        logging.info("Chat copied")
        
        # Step 5: Extract last sender dynamically
        last_message = self.chat_utils.get_last_message(chat_history)
        contact_name = last_message["sender"]
        message_body = last_message["message"]
        
        if not contact_name or not message_body:
            logging.info("No valid messages found in the active chat area.")
            return

        logging.info(f"Current chat: {contact_name}")

        # Step 6: Ignore if sender == MY_NAME
        if contact_name == MY_NAME:
            logging.info(f"Last message was sent by '{contact_name}' (myself). Ignoring.")
            return

        # Generate message ID for duplicate checking
        message_id = self.chat_utils.generate_message_id(chat_history)
        if self.chat_utils.is_duplicate_message(message_id, self.last_processed_message_id):
            logging.debug("Latest message is a duplicate (already processed). Ignoring.")
            return

        # Step 7: Load memory from SQLite
        user_profile = self.memory.get_user(contact_name)
        if not user_profile:
            logging.info(f"No existing database profile found for '{contact_name}'. Registering defaults.")
            # Set default preferences: English, Casual
            self.memory.save_or_update_user(contact_name, language="English", tone="Casual")
            user_profile = self.memory.get_user(contact_name)
            
        logging.info(f"User profile context loaded: {user_profile}")

        # Step 8: Gemini analysis (language/sentiment detection) and Reply generation
        logging.info("Generating reply")
        analysis = self.analyzer.analyze(message_body, relationship="friend")
        detected_lang = analysis.get("language", "English")
        detected_emotion = analysis.get("emotion", "Neutral")
        logging.info(f"Profile analysis complete. Language: '{detected_lang}', Emotion: '{detected_emotion}'")

        reply_options = self.safety.generate_three_replies(chat_history, user_profile)
        casual_reply = reply_options.get("casual")
        
        if not casual_reply:
            logging.warning("No valid casual reply generated. Skipping cycle.")
            return
            
        logging.info(f"Generated reply candidates: {reply_options}")

        # Step 9: Safety check
        logging.info(f"Running SafetyGuard evaluation on candidate reply: '{casual_reply}'")
        risk_result = self.safety.check_risk(casual_reply)
        is_safe = self.safety.should_send(risk_result)

        if is_safe:
            # Step 10: Focus input
            self.automation.focus_message_box()
            
            # Step 11: Paste
            pyperclip.copy(casual_reply)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.3)
            
            # Step 12: Enter
            pyautogui.press("enter")
            time.sleep(0.5)
            
            # Step 13: If Enter fails -> click send button
            try:
                send_pos = pyautogui.locateOnScreen(str(settings.SEND_BUTTON), confidence=0.85)
                if send_pos is not None:
                    logging.warning("Enter key failed to send. Clicking the send button...")
                    self.automation.click_send_button()
            except Exception as e:
                logging.error(f"Error checking send button visibility: {e}")

            logging.info("Message sent")
            
            # Step 14: Save SQLite
            self.memory.save_conversation(contact_name, message_body, casual_reply)
            logging.info("Conversation saved")
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
        
        # Step 1: Open Chrome, Step 2: Verify WhatsApp Tab, Step 3: Wait for user to select chat
        try:
            self.automation.open_chrome()
            logging.info("Chrome activated")
            
            self.automation.verify_whatsapp_tab()
            logging.info("WhatsApp tab detected")
            
            self.automation.wait_for_user_chat_selection()
            logging.info("Waiting for user chat selection")
        except Exception as e:
            logging.critical(f"Initialization failed: {e}", exc_info=True)
            return

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