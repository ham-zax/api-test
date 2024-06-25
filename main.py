import requests
import pandas as pd

# Base URL of the API
base_url = "https://api.io.solutions/v1/io-blocks/blocks/2024-06-25T17:00:00/workers/all"

# Headers including the token
headers = {
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'DNT': '1',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://explorer.io.net/',
    'Token': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ink2SUlqV1JidlBKR1pIRzdCYV9rYSJ9.eyJodHRwczovL2lvLm5ldC91c2VyIjp7ImNyZWF0ZWQiOmZhbHNlLCJpb19pZCI6IjEyZjA5ODViLTJmZDctNDkzYi1hZWUzLWY2YmQzN2JjY2I4NiIsInByaW1hcnlfbWFpbCI6ImhkYW1uaXRAZ21haWwuY29tIn0sImlzcyI6Imh0dHBzOi8vdGVzdC11c2Vycy1taWdyYXRpb24udXMuYXV0aDAuY29tLyIsInN1YiI6Imdvb2dsZS1vYXV0aDJ8MTE3NjA5Nzc1OTk2NTQ4NzczODczIiwiYXVkIjpbImh0dHBzOi8vdGVzdC11c2Vycy1taWdyYXRpb24udXMuYXV0aDAuY29tL2FwaS92Mi8iLCJodHRwczovL3Rlc3QtdXNlcnMtbWlncmF0aW9uLnVzLmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE3MTkwNDAyMzEsImV4cCI6MTcyMDc2ODIzMSwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCB1cGRhdGU6Y3VycmVudF91c2VyX21ldGFkYXRhIHJlYWQ6Y3VycmVudF91c2VyIG9mZmxpbmVfYWNjZXNzIiwiYXpwIjoicnY5amkzb2o0YnRzSWljVXNya0hyN0JzdkNSaHV3SGIifQ.Lle8s8T9pDupq6iRg33KLNpQO5xfwpyGebQ9g5KyUGUsWBqjiAawKKj29rplkq3ojFcq7sjoGn51ZjVr_j_cqAV_uD4PlLjbv5CivCqlg0gFrEoyuaA6bma36LXWT5sIREVO2mIm5yLAIqxCJbgrx3KsIIbFQhDfb2A-h-ImZlLUie5BaN5-3iWgJgpE1JZ_NYqtRiZCosPv8X9IG73V47y7m4GlDSmIMLWaD79M_AVBPLLDWfcCkuh5FBTX3szXUSLRUshC9ClITZG6PRonJ8GN5UZOln6V53JDmp7Qi5xvBPa0YnrYz27F8QxTj-QvEDM3eZC3tkSElR9jJRFWjA',
    'sec-ch-ua-platform': '"Windows"'
}

# Initialize an empty list to store data
data = []

# Pagination: start with the first page
page = 1
while True:
    # Construct the URL for the current page
    url = f"{base_url}/{page}"
    
    # Make the API request
    response = requests.get(url, headers=headers)
    
    # Check if the response is valid
    if response.status_code != 200:
        print(f"Failed to retrieve data from page {page}. Status code: {response.status_code}")
        break
    
    # Parse the JSON response
    response_data = response.json()
    
    # Extract the block rewards
    block_rewards = response_data.get('block_rewards', [])
    
    # Check if there are no more rewards
    if not block_rewards:
        break
    
    # Process each block reward
    for reward in block_rewards:
        processor = reward.get('processor')
        processor_quantity = reward.get('processor_quantity')
        total_score = reward.get('total_score')
        normalized_score = reward.get('normalized_score')
        reward_value = reward.get('rewarded')
        
        # Compute normalized score per processor
        normalized_score_per_processor = normalized_score / processor_quantity if processor_quantity else None
        
        # Append the extracted data to the list
        data.append({
            "Processor": processor,
            "Processor Quantity": processor_quantity,
            "Reward": reward_value,
            "Total Score": total_score,
            "Normalized Score": normalized_score,
            "Normalized Score per Processor": normalized_score_per_processor
        })
    
    # Move to the next page
    page += 1

# Check if data was successfully retrieved
if data:
    # Create a DataFrame from the data
    df = pd.DataFrame(data)
    
    # Save the DataFrame to a CSV file
    csv_filename = "block_rewards.csv"
    df.to_csv(csv_filename, index=False)
    
    print(f"Data has been saved to {csv_filename}")
else:
    print("No data retrieved. CSV file was not created.")
