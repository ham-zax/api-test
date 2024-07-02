import requests
import time
import logging
from scaleawaysession import X_Session_Token
import config  # Import the config module

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Function to check server stock
def check_server_stock():
    try:
        response = requests.get(config.API_URL, headers={
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'dnt': '1',
            'origin': 'https://console.scaleway.com',
            'priority': 'u=1, i',
            'referer': 'https://console.scaleway.com/',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'x-scw-console': 'console@3.343.0',
            'x-session-token': X_Session_Token
        })
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()
        for server_type in data['server_types']:
            if server_type['name'] == config.TARGET_SERVER:
                if server_type['stock'] != 'no_stock':
                    message = f"Server '{config.TARGET_SERVER}' is now in stock!"
                    logging.info(message)
                    config.send_telegram_message(message)
                else:
                    logging.info(f"Server '{config.TARGET_SERVER}' is still out of stock.")
                return
        logging.warning(f"Server type '{config.TARGET_SERVER}' not found in the response.")

    except requests.RequestException as e:
        logging.error(f"Error checking server stock: {e}")

if __name__ == "__main__":
    logging.info("Starting server stock checker...")
    while True:
        check_server_stock()
        time.sleep(config.CHECK_INTERVAL)
