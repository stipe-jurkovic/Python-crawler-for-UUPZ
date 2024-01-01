import pandas as pd
import os

# Navigate to the parent directory and then the 'data' directory
os.chdir(os.path.join(os.getcwd(), os.pardir, "data"))
print(os.getcwd())
# Navigate to the csvovi directory
os.chdir(os.path.join(os.getcwd(), "csvovi"))

# For each folder in the directory navigate to it and print the list of files
for folder in os.listdir():
    os.chdir(os.path.join(os.getcwd(), folder))
    # Load all the CSV files in the directory into a DataFrame that have the word 'scraped' in their name
    df = pd.concat([pd.read_csv(file) for file in os.listdir() if "scraped" in file])

    #################################################################################################################################################
    # LAT AND LNG CLEANING

    # For each city in the dataframe, calculate the average latitude and longitude and fill the missing values with the average values for each city
    average_lat_lng = df.groupby("city")[["lat", "lng"]].mean()
    df["lat"] = df.apply(lambda row: average_lat_lng.loc[row["city"], "lat"] if pd.isnull(row["lat"]) else row["lat"], axis=1)
    df["lng"] = df.apply(lambda row: average_lat_lng.loc[row["city"], "lng"] if pd.isnull(row["lng"]) else row["lng"], axis=1)

    # Check if the dataframe has any null values in the 'lat' and 'lng' columns and if it does, print that folder's name
    if df["lat"].isnull().values.any() or df["lng"].isnull().values.any():
        # Remove the rows that have null values in the 'lat' and 'lng' columns
        df = df.dropna(subset=["lat", "lng"])

    # Brišem ove stupce jer ih ima vrlo malo i ne znam zašto ne želi upisati za njih vrijendosti
    #################################################################################################################################################
        
    #################################################################################################################################################
    # PRICE CLEANING

    # Check if the 'price' column is a string and if it is, remove the currency symbol from the price column and convert it to a float
    if df["price"].dtype == "O":
        # Remove the euro symbol from the price column and convert it to a float
        df["price"] = df["price"].str.replace("kn", "").str.replace("€", "").str.replace("\xa0", "").str.replace(".", "").str.replace(",", ".").astype(float)
    # Check if there are any null values in the 'price' column and if there are, print that folder's name
    if df["price"].isnull().values.any():
        # Remove the rows that have null values in the 'price' column
        df = df.dropna(subset=["price"])

    # Remove the top 1% and bottom 1% of the rows based on the price column
    df = df.iloc[int(len(df)*0.01):int(len(df)*0.99)]

    #################################################################################################################################################


    #################################################################################################################################################
    # FLATBUILDINGTYPE CLEANING

    # Define a dictionary to map the string values to their replacements
    flatBuildingTypeReplacements = {
        'U stambenoj zgradi': 0,
        'U kući': 1,
    }

    # Replace the string values in the 'flatBuildingType' column
    df['flatBuildingtype'] = df['flatBuildingtype'].replace(flatBuildingTypeReplacements).fillna(0)
    
    #################################################################################################################################################

    #################################################################################################################################################
    # FLATFLOORCOUNT CLEANING

    # Define a dictionary to map the string values to their replacements
    flatFloorCountReplacements = {
        'jednoetažni': 1,
        'dvoetažni': 2,
        'višeetažni': 3,
    }

    # Replace the string values in the 'flatFloorCount' column
    df['flatFloorCount'] = df['flatFloorCount'].replace(flatFloorCountReplacements).fillna(0)

    #################################################################################################################################################

    #################################################################################################################################################
    # NUMBEROFROOMS CLEANING

    # Replace 'Garsonijera' with '0' and keep the first character if it's a digit in the 'numberOfRooms' column
    df['numberOfRooms'] = df['numberOfRooms'].apply(lambda x: 0 if x == 'Garsonijera' else int(str(x)[0]) if str(x)[0].isdigit() else x)

    # Convert the 'numberOfRooms' column to integer
    df['numberOfRooms'] = df['numberOfRooms'].astype(int)

    #################################################################################################################################################

    #################################################################################################################################################
    # BATHROOMSWITHTOILET CLEANING

    # Check if the column is a string and if it is, keep the first character if it's a digit in the 'bathrooms with toilet' column
    if df["bathrooms with toilet"].dtype == "O":
        df['bathrooms with toilet'] = df['bathrooms with toilet'].apply(lambda x: int(str(x)[0]) if str(x)[0].isdigit() else x)

    # Have all the Nan values be 1
    df['bathrooms with toilet'] = df['bathrooms with toilet'].fillna(1)
    
    # Convert the 'bathrooms with toilet' column to integer
    df['bathrooms with toilet'] = df['bathrooms with toilet'].astype(int)

    #################################################################################################################################################

    #################################################################################################################################################
    # TOILET CLEANING

    # Check if the column is a string and if it is, keep the first character if it's a digit in the 'toilets' column
    if df["toilets"].dtype == "O":
        df['toilets'] = df['toilets'].apply(lambda x: int(str(x)[0]) if str(x)[0].isdigit() else x)

    # Have all the Nan values be 1
    df['toilets'] = df['toilets'].fillna(1)

    # Convert the 'toilets' column to integer
    df['toilets'] = df['toilets'].astype(int)

    #################################################################################################################################################

    #################################################################################################################################################
    # BUILDINGFLOORPOSITION CLEANING

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
        'Penthouse': average_floor+3,
    }

    # Replace the string values in the 'buildingFloorPosition' column
    df['buildingFloorPosition'] = df['buildingFloorPosition'].replace(buildingFloorPositionReplacements).fillna(average_floor)

    # Convert the 'buildingFloorPosition' column to integer
    df['buildingFloorPosition'] = df['buildingFloorPosition'].astype(int)

    # Fill all the Nan values with the average floor
    df['buildingFloorPosition'] = df['buildingFloorPosition'].fillna(average_floor)

    #################################################################################################################################################

    # Generate a new CSV file with the cleaned data and name the file folder's name + 'cleaned.csv'
    df.to_csv(folder + "cleaned.csv", index=False)
    # Print the number of rows in the dataframe
    print(folder)
    print(len(df))

    os.chdir(os.path.join(os.getcwd(), os.pardir))