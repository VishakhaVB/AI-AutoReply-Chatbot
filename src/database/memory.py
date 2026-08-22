import sqlite3
import logging
from typing import Dict, List, Any

class MemoryManager:
    """
    Manages conversational memory and user preferences using a SQLite database.
    
    This class handles the creation and updating of user records (preferences, 
    running summaries) and historical logs of conversations.
    """

    def __init__(self, db_path: str = "memory.db") -> None:
        """
        Initializes the MemoryManager and verifies table existence.
        
        Args:
            db_path (str): File path to the SQLite database file. Defaults to 'memory.db'.
        """
        self.db_path = db_path
        self.create_tables()

    def create_tables(self) -> None:
        """
        Creates the 'users' and 'conversations' tables if they do not exist.
        
        Raises:
            RuntimeError: If database table creation fails.
        """
        users_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                preferred_language TEXT,
                preferred_tone TEXT,
                conversation_summary TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        
        conversations_table_query = """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                user_message TEXT,
                ai_reply TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_name) REFERENCES users (name) ON DELETE CASCADE
            )
        """

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(users_table_query)
                cursor.execute(conversations_table_query)
                conn.commit()
                logging.info("SQLite database tables verified/created.")
        except sqlite3.Error as e:
            logging.error(f"Database table verification/creation failed: {e}", exc_info=True)
            raise RuntimeError(f"Database table verification/creation failed: {e}") from e

    def save_or_update_user(self, name: str, language: str, tone: str) -> None:
        """
        Inserts a new user or updates details for an existing user name.
        
        Args:
            name (str): Unique name identifier of the user.
            language (str): Preferred language for replies.
            tone (str): Preferred tone/personality for replies.
            
        Raises:
            RuntimeError: If database operation fails.
        """
        query = """
            INSERT INTO users (name, preferred_language, preferred_tone, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(name) DO UPDATE SET
                preferred_language = excluded.preferred_language,
                preferred_tone = excluded.preferred_tone,
                updated_at = CURRENT_TIMESTAMP
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (name, language, tone))
                conn.commit()
                logging.info(f"User preferences updated for name: '{name}'.")
        except sqlite3.Error as e:
            logging.error(f"Failed to save or update user '{name}': {e}", exc_info=True)
            raise RuntimeError(f"Failed to save or update user record: {e}") from e

    def get_user(self, name: str) -> Dict[str, Any]:
        """
        Retrieves user profile and conversation summary for a given username.
        
        Args:
            name (str): The unique name of the user.
            
        Returns:
            Dict[str, Any]: Dictionary representing user profile or empty dictionary if not found.
            
        Raises:
            RuntimeError: If database query fails.
        """
        query = """
            SELECT id, name, preferred_language, preferred_tone, conversation_summary, updated_at 
            FROM users 
            WHERE name = ?
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Set row factory to retrieve dict-like row entries
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, (name,))
                row = cursor.fetchone()
                
                return dict(row) if row else {}
        except sqlite3.Error as e:
            logging.error(f"Failed to retrieve user '{name}': {e}", exc_info=True)
            raise RuntimeError(f"Failed to retrieve user record: {e}") from e

    def save_conversation(self, name: str, user_message: str, ai_reply: str) -> None:
        """
        Saves a conversation turn to the database.
        
        Automatically inserts the user name into the users table if they are not already registered.
        
        Args:
            name (str): Name of the user in context.
            user_message (str): Message content sent by the user.
            ai_reply (str): Response content generated by the AI.
            
        Raises:
            RuntimeError: If database operation fails.
        """
        ensure_user_query = """
            INSERT OR IGNORE INTO users (name, preferred_language, preferred_tone, updated_at)
            VALUES (?, 'English', 'Helpful', CURRENT_TIMESTAMP)
        """
        insert_conv_query = """
            INSERT INTO conversations (user_name, user_message, ai_reply, timestamp)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Run pre-insert to enforce user relationship without crash
                cursor.execute(ensure_user_query, (name,))
                # Save the new conversation log
                cursor.execute(insert_conv_query, (name, user_message, ai_reply))
                conn.commit()
                logging.info(f"Conversation record logged for user: '{name}'.")
        except sqlite3.Error as e:
            logging.error(f"Failed to save conversation entry for user '{name}': {e}", exc_info=True)
            raise RuntimeError(f"Failed to save conversation: {e}") from e

    def get_recent_context(self, name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves the most recent conversation logs for a given user name.
        
        Returns context in chronological order (oldest to newest).
        
        Args:
            name (str): The unique name of the user.
            limit (int): The max number of conversation turns to return. Defaults to 5.
            
        Returns:
            List[Dict[str, Any]]: A list of dictionary objects containing conversation logs.
            
        Raises:
            RuntimeError: If query execution fails.
        """
        query = """
            SELECT id, user_name, user_message, ai_reply, timestamp 
            FROM conversations 
            WHERE user_name = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, (name, limit))
                rows = cursor.fetchall()
                
                # Reverse the rows to return context chronologically
                return [dict(row) for row in reversed(rows)]
        except sqlite3.Error as e:
            logging.error(f"Failed to retrieve conversation context for user '{name}': {e}", exc_info=True)
            raise RuntimeError(f"Failed to retrieve conversation context: {e}") from e

    def update_conversation_summary(self, name: str, summary: str) -> None:
        """
        Updates the running conversation summary for a specific user name.
        
        If the user does not exist, they are registered with the summary.
        
        Args:
            name (str): The unique name identifier of the user.
            summary (str): The updated summary description of previous chats.
            
        Raises:
            RuntimeError: If update operation fails.
        """
        query = """
            INSERT INTO users (name, conversation_summary, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(name) DO UPDATE SET
                conversation_summary = excluded.conversation_summary,
                updated_at = CURRENT_TIMESTAMP
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (name, summary))
                conn.commit()
                logging.info(f"Conversation summary updated for user: '{name}'.")
        except sqlite3.Error as e:
            logging.error(f"Failed to update conversation summary for user '{name}': {e}", exc_info=True)
            raise RuntimeError(f"Failed to update conversation summary: {e}") from e
