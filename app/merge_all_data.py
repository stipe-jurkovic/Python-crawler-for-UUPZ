import pandas as pd
import os


# Navigate to the 'data' directory relative to the current working directory
data_dir = os.path.join(os.getcwd(), os.pardir, "data")
os.chdir(data_dir)
print("Current Working Directory:", os.getcwd())

# Check if 'data' directory exists, create it if not
if not os.path.exists("data"):
    os.makedirs("data")
    print("Created directory: data")

# Navigate to the 'csvovi' directory
csvovi_path = os.path.join(os.getcwd(), "csvovi")
os.chdir(csvovi_path)
print("CSV Directory:", csvovi_path)

# Initialize an empty DataFrame to store the merged data
merged_df = pd.DataFrame()

# For each folder in the directory, navigate to it and print the list of files
for folder in os.listdir():
    folder_path = os.path.join(csvovi_path, folder)
    print("Navigating to folder:", folder_path)

    try:
        os.chdir(folder_path)

        # Load all the CSV files in the directory into a DataFrame that have the word 'cleaned' in their name
        folder_df = pd.concat([pd.read_csv(file) for file in os.listdir() if "cleaned" in file])
        print("Data loaded successfully from folder:", folder)

        # Append the folder's data to the merged DataFrame
        merged_df = pd.concat([merged_df, folder_df])

    except FileNotFoundError as e:
        print("Error navigating to folder:", folder_path)
        print(e)
    finally:
        # Always return to the 'csvovi' directory after processing each folder
        os.chdir(csvovi_path)

# Sort the merged DataFrame first by 'price' in ascending order and then by 'linenum'
merged_df = merged_df.sort_values(by=['price', 'linenum']).reset_index(drop=True)

# Reset the index of the merged DataFrame and add a new column 'linenum' with unique values
merged_df['linenum'] = merged_df.index + 1

# Filter rows with price values below 20000.0
merged_df = merged_df[merged_df['price'] >= 20000.0]

# Reset the 'linenum' column to start from 1 for the filtered DataFrame
merged_df['linenum'] = range(1, len(merged_df) + 1)

# Save the merged DataFrame as a CSV file in the 'data' directory
output_csv_path = os.path.join(os.pardir, "data", "merged_data_filtered.csv")
merged_df.to_csv(output_csv_path, index=False)
print(f"Filtered and merged DataFrame saved as {output_csv_path}")
