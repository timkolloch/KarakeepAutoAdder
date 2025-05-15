from telegram.ext import Application, MessageHandler, filters
from dotenv import dotenv_values
from datetime import datetime, UTC
import http.client
import json
import re

URL_REGEX = re.compile(r'https?://[^\s\)\]\}\>\.,]+')
CONFIG = dotenv_values(".env")

async def reply(update, context):
    user_id = update.effective_user.id
    if str(user_id) not in CONFIG.get('AUTHORIZED_USERS'):
        return

    url = update.message.text.strip()
    if not URL_REGEX.match(url):
        await update.message.reply_text("❌ That doesn't look like a valid link.")
        return

    date = datetime.now(UTC).strftime("%c")

    conn = http.client.HTTPSConnection(CONFIG.get("KARAKEEP_URL"))
    payload = json.dumps({
    "createdAt": date,
    "type": "link",
    "url": url
    })
    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {CONFIG.get("KARAKEEP_TOKEN")}'
    }
    conn.request("POST", "/api/v1/bookmarks", payload, headers)
    res = conn.getresponse()

    if res.status == 201:
        await update.message.reply_text('Bookmark added successfully.')
    else:
        await update.message.reply_text(f'Failed to add bookmark: {res.status} - {res.read().decode()}')

def main():
    """
    Handles the initial launch of the program (entry point).
    """
    token = CONFIG.get("TELEGRAM_BOT_TOKEN")
    application = Application.builder().token(token).concurrent_updates(True).read_timeout(30).write_timeout(30).build()
    application.add_handler(MessageHandler(filters.TEXT, reply)) # new text handler here
    print("Telegram Bot started!", flush=True)
    application.run_polling()

if __name__ == '__main__':
    main()
