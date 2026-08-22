import time
from src.ai_reply import GeminiReplyGenerator

bot = GeminiReplyGenerator()

start = time.perf_counter()

reply = bot.generate_reply("User: Hello, how are you?")

end = time.perf_counter()

print("\n✅ Gemini Working")
print(f"⏱ Time: {end - start:.2f} seconds")
print("Reply:", reply)