from src.database.memory import MemoryManager

db = MemoryManager()

print("Creating tables...")
db.create_tables()

print("Saving user...")
db.save_or_update_user(
    name="Rohan",
    language="Hinglish",
    tone="Funny"
)

print("Saving conversation...")
db.save_conversation(
    name="Rohan",
    user_message="Bro SIH karna hai?",
    ai_reply="Haan bhai 5 baje milte!"
)

print("\nFetching user...")
user = db.get_user("Rohan")
print(user)

print("\nRecent Context...")
context = db.get_recent_context("Rohan")
for msg in context:
    print(msg)

print("\n✅ SQLite Memory Working")