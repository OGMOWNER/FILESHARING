import requests
import time
import sqlite3
import secrets

TOKEN = "7558045354:AAG_hRnQaGykSf-QPpZbThqaqFI6Bpx3dwM"
URL = f"https://api.telegram.org/bot{TOKEN}"
OFFSET = None

# Setup DB
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS files (id TEXT PRIMARY KEY, file_id TEXT, file_name TEXT, user_id INTEGER, upload_time TEXT)")
conn.commit()

def get_updates():
    global OFFSET
    resp = requests.get(f"{URL}/getUpdates", params={"timeout": 30, "offset": OFFSET})
    return resp.json()["result"]

def send_message(chat_id, text):
    requests.post(f"{URL}/sendMessage", data={"chat_id": chat_id, "text": text})

def handle_document(update):
    doc = update["message"]["document"]
    user_id = update["message"]["from"]["id"]
    chat_id = update["message"]["chat"]["id"]
    file_id = doc["file_id"]
    file_name = doc["file_name"]
    file_code = secrets.token_urlsafe(6)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("INSERT INTO files VALUES (?, ?, ?, ?, ?)", (file_code, file_id, file_name, user_id, timestamp))
    conn.commit()

    link = f"http://localhost:8000/download/{file_code}"
    send_message(chat_id, f"✅ File uploaded!\n🔗 Download: {link}")

def handle_start(chat_id):
    send_message(chat_id, "👋 Send me any file and I’ll give you a download link.")

def run_bot():
    global OFFSET
    print("Bot is running...")
    while True:
        updates = get_updates()
        for update in updates:
            OFFSET = update["update_id"] + 1
            message = update.get("message", {})
            chat_id = message.get("chat", {}).get("id")

            if "text" in message and message["text"] == "/start":
                handle_start(chat_id)
            elif "document" in message:
                handle_document(update)

if __name__ == "__main__":
    run_bot()
