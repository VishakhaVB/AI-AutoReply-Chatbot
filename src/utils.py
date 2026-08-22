import re
import hashlib
from typing import Dict

class ChatAnalyzer:
    """
    Provides utility methods to parse and analyze chat histories from WhatsApp Web logs.
    
    Includes functionality to extract message metadata, identify message senders,
    and generate unique signatures for message deduplication.
    """

    # Robust regex pattern matching WhatsApp Web message format.
    # Formats matched: [HH:MM, DD/MM/YYYY] Sender Name: Message Body
    # Supports: optional square brackets, 12/24 hour time with optional seconds/AM/PM, 
    # and dates using slashes or hyphens.
    MESSAGE_PATTERN = re.compile(
        r'(?:\[?(\d{1,2}:\d{2}(?::\d{2})?(?:\s?[APap][Mm])?),\s(\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2})\]?)\s+([^:]+):\s*(.*)'
    )

    def extract_last_message(self, chat_history: str) -> Dict[str, str]:
        """
        Extracts the sender, timestamp, and text content of the most recent message.
        
        Handles multiline messages by capturing all text trailing the last matched header.
        
        Args:
            chat_history (str): The raw text logs copied from WhatsApp Web.
            
        Returns:
            Dict[str, str]: A dictionary containing keys:
                - 'timestamp': Combined date and time (e.g. "21:02, 12/6/2024") or empty string.
                - 'sender': Name of the message sender or empty string.
                - 'message': Body of the message or empty string.
        """
        empty_result = {"timestamp": "", "sender": "", "message": ""}
        
        if not chat_history or not chat_history.strip():
            return empty_result

        # Locate all message boundaries matching the standard header format
        matches = list(self.MESSAGE_PATTERN.finditer(chat_history))
        
        if not matches:
            # Safely return empty structure if the text is malformed or has no match
            return empty_result

        last_match = matches[-1]
        time_part = last_match.group(1)
        date_part = last_match.group(2)
        sender = last_match.group(3).strip()
        
        # Capture the message content starting from the beginning of group 4 to the end of the text.
        # This naturally collects multiline text that belongs to the last message.
        message_content = chat_history[last_match.start(4):].strip()
        timestamp = f"{time_part}, {date_part}"

        return {
            "timestamp": timestamp,
            "sender": sender,
            "message": message_content
        }

    def is_last_message_from_user(self, chat_history: str, my_name: str) -> bool:
        """
        Determines whether the most recent message was sent by the user (self).
        
        Args:
            chat_history (str): The raw text logs copied from WhatsApp Web.
            my_name (str): The user's name to match against.
            
        Returns:
            bool: True if the sender of the last message matches my_name, False otherwise.
        """
        if not my_name:
            return False
            
        last_message = self.extract_last_message(chat_history)
        return last_message["sender"].lower() == my_name.lower()

    def generate_message_id(self, chat_history: str) -> str:
        """
        Generates a unique SHA-256 hash identifier for the latest message.
        
        Combines message metadata (timestamp, sender, content) to produce a unique signature.
        
        Args:
            chat_history (str): The raw text logs copied from WhatsApp Web.
            
        Returns:
            str: Hexadecimal SHA-256 digest of the message signature, or empty string if invalid.
        """
        last_message = self.extract_last_message(chat_history)
        
        # Check if the extracted data is empty/invalid to prevent hashing empty attributes
        if not last_message["timestamp"] and not last_message["sender"] and not last_message["message"]:
            return ""

        # Delimit fields uniquely to generate a consistent hash signature
        signature_source = f"{last_message['timestamp']}|{last_message['sender']}|{last_message['message']}"
        
        # Return SHA-256 hex digest
        return hashlib.sha256(signature_source.encode('utf-8')).hexdigest()

    def is_duplicate_message(self, message_id: str, last_message_id: str) -> bool:
        """
        Checks if the given message ID matches the last processed message ID.
        
        Args:
            message_id (str): Hash ID of the newly scanned message.
            last_message_id (str): Hash ID of the previously replied message.
            
        Returns:
            bool: True if the IDs are identical (indicating a duplicate), False otherwise.
        """
        if not message_id or not last_message_id:
            return False
        return message_id == last_message_id
