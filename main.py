import telebot
import requests
import os
from flask import Flask
from threading import Thread

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
    # സെർച്ച് റിസൾട്ടിൽ വില വരാൻ 'price in India' എന്ന് ചേർക്കുന്നു
    query = f"{product_name} price in Amazon Flipkart"
    url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}"
    
    try:
        r = requests.get(url).json()
        if 'items' in r:
            results = f"💰 **Price Results for: {product_name}**\n\n"
            for i in r['items'][:5]:
                title = i['title']
                link = i['link']
                # Snippet-ൽ നിന്ന് വില കണ്ടെത്താൻ ശ്രമിക്കുന്നു
                snippet = i['snippet']
                
                results += f"📍 **{title}**\n📝 {snippet}\n🔗 [View Product]({link})\n\n"
            return results
        return "❌ വില വിവരങ്ങൾ കണ്ടെത്താനായില്ല."
    except Exception as e:
        return f"⚠️ Error: {e}"

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "സ്വാഗതം! ഏത് സാധനത്തിന്റെ വിലയാണ് അറിയേണ്ടത്? പേര് ടൈപ്പ് ചെയ്യൂ. (ഉദാ: iPhone 15)")

@bot.message_handler(func=lambda message: True)
def handle_price_query(message):
    product = message.text
    status = bot.reply_to(message, "വിവിധ സൈറ്റുകളിൽ വില പരിശോധിക്കുന്നു... 🔍")
    
    price_info = get_prices(product)
    
    # മെസ്സേജ് അയക്കുന്നു (Markdown ഉപയോഗിച്ച് ലിങ്കുകൾ വർക്ക് ചെയ്യാൻ)
    try:
        bot.edit_message_text(price_info, chat_id=message.chat.id, message_id=status.message_id, parse_mode="Markdown", disable_web_page_preview=True)
    except:
        bot.send_message(message.chat.id, price_info, parse_mode="Markdown")

if __name__ == "__main__":
    Thread(target=run_web_server).start()
    bot.remove_webhook()
    print("Price Tracker Bot is running...")
    bot.infinity_polling(skip_pending=True)
