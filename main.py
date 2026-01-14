import telebot
import requests
import os
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- CONFIGURATION ---
TELEGRAM_TOKEN = '8455878492:AAHOvRNri-cTN7tqI4jb1Wvywv5yul0RcFU'
GOOGLE_API_KEY = 'AIzaSyBdww3w_lvPXCnBmVe3FWc4yV-jtgfOxc4'
SEARCH_ENGINE_ID = '2287c31f5b9174d59'

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Price Bot is active!"

def run_web_server():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def get_prices(product_name):
    # Search query optimized for English results
    query = f"{product_name} price in Amazon Flipkart"
    url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}"
    
    try:
        r = requests.get(url).json()
        if 'items' in r:
            results = f"💰 **Price Results for: {product_name}**\n\n"
            for i in r['items'][:5]:
                title = i['title']
                link = i['link']
                snippet = i['snippet']
                results += f"📍 **{title}**\n📝 {snippet}\n🔗 [View Product]({link})\n\n"
            return results
        return "❌ No price information found for this product."
    except Exception as e:
        return f"⚠️ Error: {e}"

# --- HELP BUTTON ---
def help_markup():
    markup = InlineKeyboardMarkup()
    help_button = InlineKeyboardButton("Contact Developer 👨‍💻", url="https://www.instagram.com/risham004?igsh=MTc2azZobHFsbm15Yw==")
    markup.add(help_button)
    return markup

@bot.message_handler(commands=['start', 'help'])
def welcome(message):
    welcome_text = (
        "Welcome to PriceTracker AI! 🛍️\n\n"
        "Send me any product name to find the best prices and deals from online stores.\n\n"
        "Example: 'iPhone 15' or 'Samsung S24'"
    )
    bot.reply_to(message, welcome_text, reply_markup=help_markup())

@bot.message_handler(func=lambda message: True)
def handle_price_query(message):
    product = message.text
    status = bot.reply_to(message, "Searching for the best prices... 🔍")
    
    price_info = get_prices(product)
    
    try:
        bot.edit_message_text(
            price_info, 
            chat_id=message.chat.id, 
            message_id=status.message_id, 
            parse_mode="Markdown", 
            disable_web_page_preview=True,
            reply_markup=help_markup()
        )
    except:
        bot.send_message(message.chat.id, price_info, parse_mode="Markdown", reply_markup=help_markup())

if __name__ == "__main__":
    Thread(target=run_web_server).start()
    bot.remove_webhook()
    print("Price Tracker Bot is running in English...")
    bot.infinity_polling(skip_pending=True)
