import pandas as pd

# Load the data
df = pd.read_csv('block_rewards.csv')

# Remove rows with 0 in any column
df = df[(df != 0).all(axis=1)]

# Function to check if two values are approximately equal within a given range
def approx_equal(val1, val2, tolerance=0.025):
    return abs(val1 - val2) / ((val1 + val2) / 2) <= tolerance

# Remove duplicates and handle processor quantity
unique_processors = {}
for index, row in df.iterrows():
    processor = row['Processor']
    quantity = row['Processor Quantity']
    norm_score = row['Normalized Score per Processor']

    if processor not in unique_processors:
        unique_processors[processor] = [row]
    else:
        if quantity == 1:
            unique_processors[processor] = [row]
        else:
            for unique_row in unique_processors[processor]:
                if approx_equal(norm_score, unique_row['Normalized Score per Processor']):
                    if quantity == 1:
                        unique_processors[processor] = [row]
                    elif unique_row['Processor Quantity'] != 1:
                        unique_processors[processor].append(row)
                    break
            else:
                unique_processors[processor].append(row)

# Flatten the dictionary into a list of rows
unique_rows = [row for rows in unique_processors.values() for row in rows]

# Convert list back to DataFrame
unique_df = pd.DataFrame(unique_rows)

# Save the cleaned data
unique_df.to_csv('cleaned_block_rewards.csv', index=False)

print("Duplicates removed and data saved to 'cleaned_block_rewards.csv'")
