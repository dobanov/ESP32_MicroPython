import urequests
import ujson

# Function to send a message to Telegram
def send_text_to_telegram(bot_token, chat_ids, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    headers = {'Content-Type': 'application/json'}
    chat_ids_list = chat_ids.split(',')

    for chat_id in chat_ids_list:
        payload = ujson.dumps({"chat_id": chat_id, "text": message})
        try:
            response = urequests.post(url, headers=headers, data=payload)
            response.close()
        except Exception as e:
            print(f"Failed to send message to {chat_id}: {e}")
