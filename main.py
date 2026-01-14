import telebot
import requests
import os
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
TELEGRAM_TOKEN = '8455878492:AAHOvRNri-cTN7tqI4jb1Wvywv5yul0RcFU' # നിങ്ങളുടെ പുതിയ ടോക്കൺ
GOOGLE_API_KEY = 'AIzaSyBdww3w_lvPXCnBmVe3FWc4yV-jtgfOxc4'
SEARCH_ENGINE_ID = '2287c31f5b9174d59'
GEMINI_API_KEY = 'AIzaSyAw_HK2uD1ZHLLk4OFutTaeAZPEy3bSjh0'

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is active!"

def run_web_server():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def get_web_info(query):
    print(f"Searching web for: {query}")
    url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}"
    try:
        r = requests.get(url).json()
        if 'items' in r:
            snippets = [f"{i['title']}: {i['snippet']}" for i in r['items'][:5]]
            return "\n\n".join(snippets)
        print("Google result: No items found. Check CSE settings.")
        return ""
    except Exception as e:
        print(f"Google Error: {e}")
        return ""

def ask_gemini(query, context):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    prompt = f"User Question: {query}\n\nWeb Data:\n{context}\n\nAnswer in Malayalam based on the data."
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(url, headers=headers, json=payload).json()
        return res['candidates'][0]['content']['parts'][0]['text']
    except:
        return "Gemini AI-ലേക്ക് കണക്ട് ചെയ്യാൻ പറ്റിയില്ല."

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "ഞാൻ റെഡിയാണ്! എന്താണ് നിങ്ങൾക്ക് അറിയേണ്ടത്?")

@bot.message_handler(func=lambda message: True)
def process(message):
    query = message.text
    msg = bot.reply_to(message, "തിരയുന്നു... 🔍")
    
    context = get_web_info(query)
    if not context:
        bot.edit_message_text("ക്ഷമിക്കണം, വെബ്സൈറ്റുകളിൽ നിന്ന് വിവരങ്ങൾ കണ്ടെത്താനായില്ല. ഗൂഗിൾ സെർച്ച് എൻജിൻ സെറ്റിങ്‌സ് ഒന്ന് പരിശോധിക്കൂ.", chat_id=message.chat.id, message_id=msg.message_id)
        return

    answer = ask_gemini(query, context)
    try:
        bot.edit_message_text(answer, chat_id=message.chat.id, message_id=msg.message_id)
    except:
        bot.send_message(message.chat.id, answer)

if __name__ == "__main__":
    Thread(target=run_web_server).start()
    bot.remove_webhook()
    print("Bot is running...")
    bot.infinity_polling(skip_pending=True)
