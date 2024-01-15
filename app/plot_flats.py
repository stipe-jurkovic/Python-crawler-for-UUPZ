import folium
import pandas as pd

# Sample data (replace this with your actual data)
data = {
    'Flat': ['Flat1', 'Flat2', 'Flat3'],
    'Latitude': [45.1, 45.2, 45.3],
    'Longitude': [15.1, 15.2, 15.3]
}

df = pd.DataFrame(data)

# Create a folium map centered around Croatia
croatia_map = folium.Map(location=[45.1, 15.5], zoom_start=7)

# Add markers for each flat
for index, row in df.iterrows():
    folium.Marker([row['Latitude'], row['Longitude']], popup=row['Flat']).add_to(croatia_map)

# Save the map to an HTML file
croatia_map.save('flats_map.html')
