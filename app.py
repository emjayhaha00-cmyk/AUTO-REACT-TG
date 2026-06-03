import os
import random
import time
import threading
from flask import Flask
from telegram import Bot

# ===== CONFIGURE YOUR BOTS HERE =====
# Paste your bot tokens from BotFather (comma-separated)
BOT_TOKENS_STR = os.environ.get("BOT_TOKENS", "8874178948:AAGVHeLyG-cM9uwEydmyOL6RzIBn0nxL0Pk")
BOT_TOKENS = [t.strip() for t in BOT_TOKENS_STR.split(",") if t.strip()]

# Choose emojis for reactions
EMOJIS = ["👍", "🔥", "❤️", "😂", "😎", "🎉", "👏", "💯"]

# ===== BOT CODE (Don't change below unless you know what you're doing) =====

# Flask app for Render health checks
app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health_check():
    return "Bot is running!", 200

def run_bot(token):
    """Run a single bot instance"""
    bot = Bot(token=token)
    last_update_id = 0
    print(f"✅ Bot started: {token[:10]}...")
    
    while True:
        try:
            # Get new messages
            updates = bot.get_updates(offset=last_update_id + 1, timeout=30)
            
            for update in updates:
                last_update_id = update.update_id
                
                if update.message:
                    chat_id = update.message.chat.id
                    message_id = update.message.message_id
                    
                    # Random delay to look natural
                    time.sleep(random.uniform(0.5, 3))
                    
                    # Pick random emoji
                    emoji = random.choice(EMOJIS)
                    
                    # Add reaction (bots can only add 1 reaction per message) [citation:1][citation:5]
                    bot.set_message_reaction(
                        chat_id=chat_id,
                        message_id=message_id,
                        reaction=[{"type": "emoji", "emoji": emoji}]
                    )
                    print(f"🎯 Reacted with {emoji} (bot: {token[:10]}...)")
                    
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(5)

def start_bots():
    """Start all bots in separate threads"""
    if not BOT_TOKENS or BOT_TOKENS == ['']:
        print("❌ ERROR: No BOT_TOKENS found! Add them in Render environment variables.")
        return
    
    threads = []
    for token in BOT_TOKENS:
        thread = threading.Thread(target=run_bot, args=(token,))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    print(f"🚀 Started {len(threads)} bot(s)")
    
    # Keep threads alive
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    # Start bot threads
    bot_thread = threading.Thread(target=start_bots)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Start Flask server (required for Render to keep the service alive)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
