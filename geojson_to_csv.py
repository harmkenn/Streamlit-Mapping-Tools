import streamlit as st
import json
import pandas as pd

def process_geojson(geojson_data):
    """
    Processes the GeoJSON data to extract country names and boundaries.
    Returns a DataFrame with two columns: 'Country Name' and 'GeoJSON Boundaries'.
    """
    countries = []
    boundaries = []

    for feature in geojson_data['features']:
        # Extract country name and geometry
        country_name = feature['properties'].get('NAME_ENGL', 'Unknown')
        geometry = feature['geometry']
        
        # Append to lists
        countries.append(country_name)
        boundaries.append(json.dumps(geometry))  # Convert geometry to JSON string

    # Create a DataFrame
    df = pd.DataFrame({'Country Name': countries, 'GeoJSON Boundaries': boundaries})
    return df

# Streamlit app
st.title("GeoJSON to CSV Converter")

# File uploader
uploaded_file = st.file_uploader("Upload a GeoJSON file", type=["geojson"])

if uploaded_file is not None:
    # Load the GeoJSON file
    geojson_data = json.load(uploaded_file)
    
    # Process the GeoJSON data
    df = process_geojson(geojson_data)
    
    # Display the DataFrame
    st.write("Extracted Data:")
    st.dataframe(df)
    
    # Download the CSV file
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="country_boundaries.csv",
        mime="text/csv"
    )
