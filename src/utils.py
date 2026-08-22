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

    def extract_messages(self, chat_history: str) -> list[dict[str, str]]:
        """
        Parses the entire chat history and extracts all messages.
        
        Supports emojis, Marathi, Hindi, English, and multiline messages.
        
        Args:
            chat_history (str): The raw text logs copied from WhatsApp Web.
            
        Returns:
            list[dict[str, str]]: A list of dictionaries containing:
                - 'timestamp': Combined time and date.
                - 'sender': Name of the message sender.
                - 'message': Message body.
        """
        messages = []
        if not chat_history or not chat_history.strip():
            return messages

        # Find all message headers
        matches = list(self.MESSAGE_PATTERN.finditer(chat_history))
        if not matches:
            return messages

        for i, match in enumerate(matches):
            time_part = match.group(1)
            date_part = match.group(2)
            sender = match.group(3).strip()
            
            # Determine where this message's body ends
            start_index = match.start(4)
            if i + 1 < len(matches):
                end_index = matches[i + 1].start()
            else:
                end_index = len(chat_history)
                
            message_content = chat_history[start_index:end_index].strip()
            timestamp = f"{time_part}, {date_part}"
            
            messages.append({
                "timestamp": timestamp,
                "sender": sender,
                "message": message_content
            })
            
        return messages

    def get_last_message(self, chat_history: str) -> dict[str, str]:
        """
        Extracts the sender, timestamp, and text content of the most recent message.
        
        Args:
            chat_history (str): The raw text logs copied from WhatsApp Web.
            
        Returns:
            dict[str, str]: A dictionary containing keys:
                - 'timestamp': Combined date and time (e.g. "21:02, 12/6/2024") or empty string.
                - 'sender': Name of the message sender or empty string.
                - 'message': Body of the message or empty string.
        """
        empty_result = {"timestamp": "", "sender": "", "message": ""}
        messages = self.extract_messages(chat_history)
        if not messages:
            return empty_result
        return messages[-1]

    def is_last_message_from_me(self, chat_history: str, my_name: str) -> bool:
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
            
        last_message = self.get_last_message(chat_history)
        return last_message["sender"].lower() == my_name.lower()

    # Backwards-compatible aliases
    extract_last_message = get_last_message
    is_last_message_from_user = is_last_message_from_me

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
