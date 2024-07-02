import io
import logging
import requests  # Add this import statement

API_URL = 'https://api.scaleway.com/apple-silicon/v1alpha1/zones/fr-par-1/server-types'
CHECK_INTERVAL = 60  # Interval in seconds
TARGET_SERVER = 'M2-M'


TELEGRAM_TOKEN = '7119782068:AAHm5qatChCeyaHdNmlt6FBGF8NxVxj0OV4'
CHAT_IDS = ['376895924']  # List of chat IDs

def send_telegram_message(message: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    success = True
    for chat_id in CHAT_IDS:
        logging.info(f"Sending message to chat ID: {chat_id}")
        data = {'chat_id': chat_id, 'text': message}
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            logging.info(f"Message sent successfully to chat ID: {chat_id}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to send Telegram message to chat ID {chat_id}: {e}")
            if response.text:
                logging.error(f"Telegram API response: {response.text}")
            success = False
    return success
