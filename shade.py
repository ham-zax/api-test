import requests
import json
import io
import time
import logging
from datetime import datetime
from typing import List, Dict, Any
import matplotlib.pyplot as plt
from prettytable import PrettyTable
import telegram
from tabulate import tabulate

# API URL
url = "https://api.shadeform.ai/v1/instances/types"

# Replace with your actual API key
api_key = "KFpyVQfCUSixFn4yuQ1OdHSe"

# Configuration values
GPU_TYPE_FILTER = "h100"  # Set to empty string to disable GPU type filtering
MAX_PRICE = 300  # Set to None to disable price filtering, in cents
INTERVAL = 60  # Interval in seconds

# Telegram configuration
TELEGRAM_TOKEN = '7119782068:AAHm5qatChCeyaHdNmlt6FBGF8NxVxj0OV4'
CHAT_IDS = ['376895924']  # List of chat IDs

def fetch_instance_types(gpu_type_filter=None):
    headers = {
        "X-API-KEY": api_key
    }
    params = {}
    if gpu_type_filter:
        params["gpu_type"] = gpu_type_filter

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to fetch data: {response.status_code}")
        logging.error(f"Response content: {response.text}")
        return None

def filter_by_price_and_availability(instance_types, max_price):
    if max_price is None:
        max_price = float('inf')  # If no max price, allow any price

    filtered_instances = []
    for instance in instance_types:
        num_gpus = instance["configuration"]["num_gpus"]
        price_per_gpu = instance["hourly_price"] / num_gpus
        if price_per_gpu <= max_price:
            # Check if any region is available
            if any(avl["available"] for avl in instance["availability"]):
                instance["price_per_gpu"] = price_per_gpu  # Add this for sorting later
                filtered_instances.append(instance)
    
    # Sort by Hourly Price per GPU
    filtered_instances.sort(key=lambda x: x["price_per_gpu"])
    return filtered_instances

def create_table_image(instance_types):
    table_data = []
    for instance in instance_types:
        num_gpus = instance["configuration"]["num_gpus"]
        price_per_gpu = instance["price_per_gpu"]
        regions = ", ".join([avl["region"] for avl in instance["availability"] if avl["available"]])
        table_data.append([
            instance["cloud"],
            instance["shade_instance_type"],
            instance["configuration"]["gpu_type"],
            num_gpus,
            instance["configuration"]["memory_in_gb"],
            instance["configuration"]["storage_in_gb"],
            instance["configuration"]["vcpus"],
            instance["hourly_price"],
            round(price_per_gpu, 2),
            regions
        ])
    
    headers = ["Cloud", "Shade Instance Type", "GPU Type", "Num GPUs", "Memory (GB)", "Storage (GB)", "vCPUs", "Hourly Price", "Hourly Price per GPU", "Available Regions"]
    table_string = tabulate(table_data, headers, tablefmt="grid")

    # Create a 16:9 aspect ratio figure
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.axis('off')
    plt.text(0.5, 0.5, table_string, ha='center', va='center', fontsize=10, family='monospace')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

def send_telegram_message(photo: io.BytesIO) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    success = True
    for chat_id in CHAT_IDS:
        logging.info(f"Sending message to chat ID: {chat_id}")
        data = {'chat_id': chat_id}
        try:
            photo.seek(0, 2)  # Seek to the end of the buffer
            photo_size = photo.tell()  # Get the size of the buffer
            photo.seek(0)  # Seek back to the beginning of the buffer
            if photo_size == 0:
                logging.error(f"Photo data is empty for chat ID {chat_id}")
                success = False
                continue

            files = {'photo': photo}
            response = requests.post(url, data=data, files=files)
            response.raise_for_status()
            logging.info(f"Message sent successfully to chat ID: {chat_id}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to send Telegram message to chat ID {chat_id}: {e}")
            if response.text:
                logging.error(f"Telegram API response: {response.text}")
            success = False
    return success

def main():
    while True:
        data = fetch_instance_types(GPU_TYPE_FILTER)
        if data:
            filtered_instances = filter_by_price_and_availability(data['instance_types'], MAX_PRICE)
            if filtered_instances:
                image = create_table_image(filtered_instances)
                send_telegram_message(image)
            else:
                logging.info("No instances match the filter criteria.")
        else:
            logging.info("No data fetched from API")

        time.sleep(INTERVAL)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()