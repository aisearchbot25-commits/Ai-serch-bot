import telebot
import requests
import os
import logging
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- SETTINGS ---
TELEGRAM_TOKEN = '8395098302:AAGXfH0zjBBylqUWyug-obrNINkbDS3S2F0'
GOOGLE_API_KEY = 'AIzaSyBdww3w_lvPXCnBmVe3FWc4yV-jtgfOxc4'
SEARCH_ENGINE_ID = '2287c31f5b9174d59'
DEV_INSTAGRAM = "https://www.instagram.com/risham004?igsh=MTc2azZobHFsbm15Yw=="

# Logging setup to track errors
logging.basicConfig(level=logging.INFO)
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running Professionally!"

def run_web_server():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def get_professional_results(query):
    # Search optimization
    search_query = f"{query} price in India Amazon Flipkart"
    url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&q={search_query}"
    
    try:
        r = requests.get(url).json()
        if 'items' in r:
            return r['items'][:4] # Top 4 results for clean look
        return None
    except Exception as e:
        logging.error(f"Search Error: {e}")
        return None

def create_keyboard(results=None, show_dev=True):
    markup = InlineKeyboardMarkup(row_width=1)
    if results:
        for item in results:
            # Clean title for button
            btn_title = item['title'][:35] + "..."
            markup.add(InlineKeyboardButton(text=f"🛒 {btn_title}", url=item['link']))
    
    if show_dev:
        markup.add(InlineKeyboardButton(text="👨‍💻 Contact Developer", url=DEV_INSTAGRAM))
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_msg = (
        "✨ *Welcome to PriceTracker Pro* ✨\n\n"
        "I can help you find the best prices from Amazon, Flipkart, and more.\n\n"
        "💡 *Just send me a product name!*"
    )
    bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=create_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_query(message):
    query = message.text
    temp_msg = bot.reply_to(message, "🔍 *Searching professional databases...*", parse_mode="Markdown")
    
    results = get_professional_results(query)
    
    if results:
        response_text = f"✅ *Found the best matches for:* _{query}_\n\nClick the buttons below to view products:"
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=temp_msg.message_id,
            text=response_text,
            parse_mode="Markdown",
            reply_markup=create_keyboard(results)
        )
    else:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=temp_msg.message_id,
            text="❌ *Sorry, no matches found.*\nTry a different product name.",
            parse_mode="Markdown",
            reply_markup=create_keyboard()
        )

if __name__ == "__main__":
    Thread(target=run_web_server).start()
    bot.remove_webhook()
    print("Professional Bot Started...")
    bot.infinity_polling(skip_pending=True)
