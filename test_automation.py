from src.automation import WhatsAppAutomation

bot = WhatsAppAutomation()

print("Opening WhatsApp...")
bot.open_whatsapp()

print("Selecting chat...")
bot.select_chat_area()

print("Copying chat...")

chat = bot.copy_chat_history()

print("\n===== COPIED CHAT =====\n")
print(chat[:1000])      # show first 1000 characters only
print("\n=======================\n")