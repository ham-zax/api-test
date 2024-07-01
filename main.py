import subprocess
import requests
import pandas as pd
import os
import logging
import time
import random
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed

# Run the add_proxies_to_config.py script
subprocess.run(["python", "add_proxies_to_config.py"], check=True)

# Load configuration
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Base URL of the API
base_url = config['api']['base_url']

# Headers including the token
headers = config['api']['headers']

# Pagination: start with the first page
max_pages = config['pagination']['max_pages']
output_filename = config['output']['filename']
max_retries = config['retries']['max_retries']

# Number of threads for parallel processing
num_threads = config['threads']['num_threads']

# Remove the output file if it exists
if os.path.exists(output_filename):
    os.remove(output_filename)

logging.info("Starting the data retrieval process...")

# List of proxies
proxies = config['proxies']

def fetch_data(page):
    logging.debug(f"Fetching data from page {page}...")
    # Construct the URL for the current page
    url = f"{base_url}/{page}"
    
    retries = 0
    use_proxies = False

    while retries < max_retries:
        try:
            # Make the API request, optionally using a proxy
            if use_proxies:
                proxy = random.choice(proxies)
                logging.debug(f"Using proxy {proxy} for page {page}...")
                response = requests.get(url, headers=headers, proxies={"http": proxy, "https": proxy})
            else:
                response = requests.get(url, headers=headers)
                
            response.raise_for_status()  # Raise an exception for HTTP errors
            # If we get here, the request was successful
            break
        except requests.exceptions.RequestException as e:
            retries += 1
            wait_time = 2 ** retries  # Exponential backoff
            if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code in [429, 525]:
                use_proxies = True
                logging.warning(f"Received {e.response.status_code} for page {page}. Switching to proxies.")
            logging.error(f"Failed to retrieve data from page {page}. Error: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    else:
        logging.error(f"Failed to retrieve data from page {page} after {max_retries} retries. Skipping this page.")
        return None
    
    # Parse the JSON response
    response_data = response.json()
    
    # Extract the block rewards
    block_rewards = response_data.get('block_rewards', [])
    
    if not block_rewards:
        logging.info(f"No more block rewards found on page {page}.")
        return None
    
    logging.debug(f"Processing {len(block_rewards)} rewards from page {page}...")
    
    # Process each block reward
    page_data = []
    for reward in block_rewards:
        processor = reward.get('processor')
        processor_quantity = reward.get('processor_quantity')
        total_score = reward.get('total_score')
        normalized_score = reward.get('normalized_score')
        reward_value = reward.get('rewarded')
        
        # Compute normalized score per processor
        normalized_score_per_processor = normalized_score / processor_quantity if processor_quantity else None
        
        # Append the extracted data to the page_data list
        page_data.append({
            "Processor": processor,
            "Processor Quantity": processor_quantity,
            "Reward": reward_value,
            "Total Score": total_score,
            "Normalized Score": normalized_score,
            "Normalized Score per Processor": normalized_score_per_processor
        })
    
    return page_data

# Use ThreadPoolExecutor to run fetch_data in parallel
def main():
    all_data = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_page = {executor.submit(fetch_data, page): page for page in range(1, max_pages + 1)}
        
        for future in as_completed(future_to_page):
            page = future_to_page[future]
            try:
                data = future.result()
                if data:
                    all_data.extend(data)
                else:
                    logging.info(f"Page {page} has no data.")
            except Exception as e:
                logging.error(f"Exception occurred while processing page {page}: {e}")
    
    # Save all data to Excel
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_excel(output_filename, index=False)
        logging.info(f"Data retrieval process completed and saved to {output_filename}")
    else:
        logging.warning("No data retrieved.")

if __name__ == "__main__":
    main()
