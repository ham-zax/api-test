import yaml

# Function to load the existing config.yaml
def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Function to save the updated config.yaml
def save_config(config, file_path):
    with open(file_path, 'w') as file:
        yaml.safe_dump(config, file)

# Function to add proxies from proxies.txt to config.yaml
def add_proxies_to_config(config_path, proxies_path):
    # Load existing config
    config = load_config(config_path)
    
    # Read proxies from the text file
    with open(proxies_path, 'r') as file:
        proxies = [line.strip() for line in file.readlines()]
    
    # Add proxies to the config
    config['proxies'] = proxies
    
    # Save the updated config
    save_config(config, config_path)
    print(f"Proxies have been added to {config_path}")

# Define the paths
config_path = 'config.yaml'
proxies_path = 'proxies.txt'

# Add proxies to config.yaml
add_proxies_to_config(config_path, proxies_path)
