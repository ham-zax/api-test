import requests
import pandas as pd
import os
import logging
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Base URL of the API
base_url = "https://api.io.solutions/v1/io-blocks/blocks/2024-06-28T21:00:00/workers/all"

# Headers including the token
headers = {
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'DNT': '1',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://explorer.io.net/',
    'Token': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ink2SUlqV1JidlBKR1pIRzdCYV9rYSJ9.eyJodHRwczovL2lvLm5ldC91c2VyIjp7ImNyZWF0ZWQiOmZhbHNlLCJpb19pZCI6IjEyZjA5ODViLTJmZDctNDkzYi1hZWUzLWY2YmQzN2JjY2I4NiIsInByaW1hcnlfbWFpbCI6ImhkYW1uaXRAZ21haWwuY29tIn0sImlzcyI6Imh0dHBzOi8vdGVzdC11c2Vycy1taWdyYXRpb24udXMuYXV0aDAuY29tLyIsInN1YiI6Imdvb2dsZS1vYXV0aDJ8MTE3NjA5Nzc1OTk2NTQ4NzczODczIiwiYXVkIjpbImh0dHBzOi8vdGVzdC11c2Vycy1taWdyYXRpb24udXMuYXV0aDAuY29tL2FwaS92Mi8iLCJodHRwczovL3Rlc3QtdXNlcnMtbWlncmF0aW9uLnVzLmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE3MTk0MDY4MTcsImV4cCI6MTcyMTEzNDgxNywic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCB1cGRhdGU6Y3VycmVudF91c2VyX21ldGFkYXRhIHJlYWQ6Y3VycmVudF91c2VyIG9mZmxpbmVfYWNjZXNzIiwiYXpwIjoicnY5amkzb2o0YnRzSWljVXNya0hyN0JzdkNSaHV3SGIifQ.VL3UBB94g0Z3SXUg-jErmr-3LIXeVvfkB-zd8n_KyuhrjgLXAZ3Gmcti7yf1vhfRyuqj6v1_trBnMvF8m3JxCXVtqkoxNLoKZZ6D3XeDB6TL3lNPvQ4XmSFbgvbTESZkjCXS7NcnBCK16EKfyIE7R1a8_-ZtQltVWKcWZdZBQAyfBNDABRBvZStdBl_6DmnEJA0J_DkTD_KB74f8u38SQTAGLEF4SG945zebb-KSxt7MKoC9Q_dHws-JrEEodZ1Z6BdcV3Y3sM3-iIExVHkt3So2_x2TfS8CAHEbERUolqEGHieb6e_IXYNIpj0Be7dmWMS6GYBlFPvv9h02FDBknQ'
}

# Pagination: start with the first page
max_pages = 300  # Set default limit to 300 pages
csv_filename = "block_rewards.csv"
max_retries = 5  # Number of retries for a failed request

# Number of threads for parallel processing
num_threads = 8

# Remove the CSV file if it exists
if os.path.exists(csv_filename):
    os.remove(csv_filename)

logging.info("Starting the data retrieval process...")

def fetch_data(page):
    logging.debug(f"Fetching data from page {page}...")
    # Construct the URL for the current page
    url = f"{base_url}/{page}"
    
    retries = 0
    success = False

    while retries < max_retries and not success:
        try:
            # Make the API request
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            success = True
        except requests.exceptions.RequestException as e:
            retries += 1
            wait_time = 2 ** retries  # Exponential backoff
            logging.error(f"Failed to retrieve data from page {page}. Error: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    
    if not success:
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
    
    # Save the DataFrame to the CSV file, append if it exists
    df = pd.DataFrame(page_data)
    if not os.path.exists(csv_filename):
        df.to_csv(csv_filename, index=False)
    else:
        df.to_csv(csv_filename, mode='a', header=False, index=False)

    logging.info(f"Data from page {page} has been saved to {csv_filename}")

    # Random delay between 1 to 2 seconds
    time.sleep(random.uniform(1, 2))
    
    return page_data

# Use ThreadPoolExecutor to run fetch_data in parallel
def main():
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(fetch_data, page): page for page in range(1, max_pages + 1)}
        
        for future in as_completed(futures):
            page = futures[future]
            try:
                data = future.result()
                if data is None:
                    logging.info(f"Page {page} has no data.")
            except Exception as e:
                logging.error(f"Exception occurred while processing page {page}: {e}")

if __name__ == "__main__":
    main()

logging.info(f"Data retrieval process completed and saved to {csv_filename}")
