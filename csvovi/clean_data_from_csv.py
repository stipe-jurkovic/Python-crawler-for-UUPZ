import pandas as pd

# Specify the path to the CSV file
csv_file_path = "primorsko-goranska/njuskalo_scrape_listing_links_primorsko-goranska_13-12-2023_22-45-53obrađena(početak obrade u _14-12-2023_00-07-41).csv"

# Load the CSV file into a DataFrame
df = pd.read_csv(csv_file_path)

# Create an empty DataFrame to store problematic rows
problematic_rows = pd.DataFrame(columns=df.columns)

# Remove the currency symbol from the price column and convert it to a float
df["price"] = df["price"].str.replace("kn", "").str.replace("€", "").str.replace("\xa0", "").str.replace(".", "").str.replace(",", ".").astype(float)

# Calculate the average latitude and longitude for each town
average_lat_lng = df.groupby("location")[["lat", "lng"]].mean()

# Fill missing latitude and longitude values with the average values for each town
df["lat"] = df.apply(lambda row: average_lat_lng.loc[row["location"], "lat"] if pd.isnull(row["lat"]) else row["lat"], axis=1)
df["lng"] = df.apply(lambda row: average_lat_lng.loc[row["location"], "lng"] if pd.isnull(row["lng"]) else row["lng"], axis=1)

# Extract the first character of the 'buildingFloorPosition' column and convert it to an integer
df['buildingFloorPosition'] = df['buildingFloorPosition'].apply(lambda x: int(str(x)[0]) if str(x)[0].isdigit() else x)

# Calculate the average of the 'buildingFloorPosition' column and round it to the nearest integer
average_floor = df['buildingFloorPosition'][df['buildingFloorPosition'].apply(lambda x: isinstance(x, int))].mean().__round__()

# Define a dictionary to map the string values to their replacements
buildingFloorPositionReplacements = {
    'Prizemlje': 0,
    'Suteren': 0,
    'Visoko prizemlje': 1,
    'Potkrovlje': average_floor+1,
    'Visoko potkrovlje': average_floor+2,
    'Penthouse': average_floor+4,
}

# Define a dictionary to map the string values to their replacements
flatBuildingTypeReplacements = {
    'U stambenoj zgradi': 0,
    'U kući': 1,
}

# Replace the string values in the 'flatBuildingType' column
df['flatBuildingtype'] = df['flatBuildingtype'].replace(flatBuildingTypeReplacements).fillna(0)

# Replace the string values in the 'buildingFloorPosition' column
df['buildingFloorPosition'] = df['buildingFloorPosition'].replace(buildingFloorPositionReplacements).fillna(average_floor)

# Convert the 'buildingFloorPosition' column to integer
df['buildingFloorPosition'] = df['buildingFloorPosition'].astype(int)

# Replace 'Garsonijera' with '0' and keep the first character if it's a digit in the 'numberOfRooms' column
df['numberOfRooms'] = df['numberOfRooms'].apply(lambda x: 0 if x == 'Garsonijera' else int(str(x)[0]) if str(x)[0].isdigit() else x)

# Convert the 'numberOfRooms' column to integer
df['numberOfRooms'] = df['numberOfRooms'].astype(int)

# Print the DataFrame head
print(df.head())

# Order by price descending
df = df.sort_values(by="price", ascending=False)

# Remove the top 1% and bottom 1% of the rows
df = df.iloc[int(len(df)*0.01):int(len(df)*0.99)]

# Generate a new CSV file with the cleaned data and name the file 'cleaned.csv'
df.to_csv("cleanedDataExample.csv", index=False)
