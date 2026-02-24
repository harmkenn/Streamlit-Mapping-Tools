import streamlit as st
import geopandas as gpd
from shapely.ops import unary_union
import pydeck as pdk
import pandas as pd
import json
import tempfile
import os

st.set_page_config(layout="wide")

st.title("World Map with Merged Western Sahara and Morocco v1.6")

@st.cache_data
def get_country_boundaries():
    """
    Fetches and processes the country boundaries.
    Merges Western Sahara into Morocco.
    """
    try:
        url = "https://datahub.io/core/geo-countries/r/countries.geojson"
        world = gpd.read_file(url).to_crs(epsg=4326)
        
        morocco_geom = world[world['name'] == 'Morocco'].geometry.squeeze()
        western_sahara_geom = world[world['name'] == 'Western Sahara'].geometry.squeeze()
        
        merged_geometry = unary_union([morocco_geom, western_sahara_geom])
        
        world.loc[world['name'] == 'Morocco', 'geometry'] = gpd.GeoSeries([merged_geometry], crs=world.crs).iloc[0]
        world = world[world['name'] != 'Western Sahara']
        
        return world

    except Exception as e:
        st.error(f"An error occurred during data processing: {e}")
        return None

# Get the main data
world_data = get_country_boundaries()

if world_data is not None:
    st.markdown("This map displays the countries of the world. The boundary of Western Sahara has been merged into Morocco.")

    # --- Pydeck Map Visualization ---
    view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1.2, pitch=0)
    geojson_layer = pdk.Layer(
        "GeoJsonLayer",
        data=world_data,
        get_fill_color="[70, 130, 180, 160]",
        get_line_color=[255, 255, 255],
        pickable=True, stroked=True, filled=True,
        line_width_min_pixels=1,
    )
    deck = pdk.Deck(
        layers=[geojson_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/light-v9",
        tooltip={"text": "Country: {name}"}
    )
    st.pydeck_chart(deck)
    
    st.markdown("---")
    
    # --- Data Preparation for Downloads and Saving ---
    # 1. GeoJSON
    geojson_data = world_data.to_json()

    # 2. KML
    kml_data = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".kml", delete=False) as tmpfile:
            tmp_path = tmpfile.name
            world_data.to_file(tmp_path, driver='KML')
        with open(tmp_path, 'rb') as f:
            kml_data = f.read()
    finally:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)

    # 3. CSV (both as a DataFrame and as encoded bytes for download)
    csv_df = pd.DataFrame({
        'Country': world_data['name'],
        'Geometry_WKT': world_data['geometry'].to_wkt()
    })
    csv_bytes = csv_df.to_csv(index=False).encode('utf-8')

    # --- Download Section ---
    st.header("Download Data to Your Computer")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button("Download as GeoJSON", geojson_data, "countries_merged.geojson", "application/json")
    
    with col2:
        if kml_data:
            st.download_button("Download as KML", kml_data, "countries_merged.kml", "application/vnd.google-earth.kml+xml")
        else:
            st.warning("Could not generate KML.")
        
    with col3:
        st.download_button("Download as CSV", csv_bytes, "countries_with_geometry.csv", "text/csv")
    
    # --- NEW: Save to Server Section ---
    st.markdown("---")
    st.header("Save CSV on the Server")

    # Define the output filename and path
    output_filename = "countries_with_geometry.csv"
    # Get the absolute path of the directory where the script is running
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, output_filename)

    if st.button(f"Save CSV to App Folder"):
        try:
            # Use the pandas DataFrame to save the file directly to the calculated path
            csv_df.to_csv(output_path, index=False)
            st.success(f"Successfully saved file to: {output_path}")
        except Exception as e:
            st.error(f"Failed to save file: {e}")
    
    # --- Display Data Table ---
    st.markdown("---")
    st.markdown("### Country Data Table")
    st.dataframe(world_data[['name', 'ISO3166-1-Alpha-3']].rename(columns={'name': 'Country', 'ISO3166-1-Alpha-3': 'ISO Code'}))
