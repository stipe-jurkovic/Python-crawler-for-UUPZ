import folium
import pandas as pd
from folium.plugins import MarkerCluster

# Read the CSV file
df = pd.read_csv('../data/merged_data_filtered.csv')

# Create an empty list to store the data
data = []

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    # Extract the latitude and longitude values
    latitude = row['lat']
    longitude = row['lng']
    
    # Create a dictionary for each row and append it to the data list
    data.append({
        'url': row['url'],
        'lat': latitude,
        'lng': longitude
    })

# Create a folium map centered around Croatia
croatia_map = folium.Map(location=[45.1, 15.5], zoom_start=7)

# Add markers for each flat
marker_cluster = MarkerCluster(max_cluster_radius=40000).add_to(croatia_map)  # Increase the max_cluster_radius value

# Add markers for each flat to the cluster, not the map
for row in data:
    folium.Marker([row['lat'], row['lng']], popup=row['url']).add_to(marker_cluster)

# Save the map to an HTML file
croatia_map.save('flats_map.html')
