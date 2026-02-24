import streamlit as st
import geopandas as gpd
from shapely.geometry import MultiPolygon
from shapely.ops import unary_union
import pydeck as pdk
import pandas as pd
import json
import tempfile
import os

st.set_page_config(layout="wide")

st.title("World Map with Custom Merged Boundaries")

@st.cache_data
def get_country_boundaries():
    """
    Fetches and processes country boundaries.
    1. Merges Western Sahara into Morocco.
    2. Merges Spanish exclaves in North Africa into Morocco.
    """
    try:
        url = "https://datahub.io/core/geo-countries/r/countries.geojson"
        world = gpd.read_file(url).to_crs(epsg=4326)
        
        # --- Step 1: Separate Spanish territories ---
        spain_full_geom = world[world['name'] == 'Spain'].geometry.squeeze()
        spain_african_parts = []
        spain_european_parts = []

        # A MultiPolygon is a collection of individual Polygons.
        # We iterate through them and separate them based on latitude.
        # This heuristic isolates Ceuta and Melilla (lat ~35-36) from mainland Spain (>37) and the Canary Islands (<30).
        for poly in spain_full_geom.geoms:
            if 35 < poly.centroid.y < 37:
                spain_african_parts.append(poly)
            else:
                spain_european_parts.append(poly)
        
        # Create a single geometry object for the African parts
        spain_africa_union = unary_union(spain_african_parts)
        
        # Create a new MultiPolygon for the European parts and update Spain's geometry
        spain_new_geom = MultiPolygon(spain_european_parts)
        world.loc[world['name'] == 'Spain', 'geometry'] = gpd.GeoSeries([spain_new_geom], crs=world.crs).iloc[0]

        # --- Step 2: Merge all pieces into Morocco ---
        morocco_geom = world[world['name'] == 'Morocco'].geometry.squeeze()
        western_sahara_geom = world[world['name'] == 'Western Sahara'].geometry.squeeze()
        
        # Combine Morocco, Western Sahara, and the Spanish African parts
        final_morocco_geom = unary_union([morocco_geom, western_sahara_geom, spain_africa_union])
        
        # Update Morocco's geometry with the final combined shape
        world.loc[world['name'] == 'Morocco', 'geometry'] = gpd.GeoSeries([final_morocco_geom], crs=world.crs).iloc[0]
        
        # --- Step 3: Clean up by removing the old Western Sahara row ---
        world = world[world['name'] != 'Western Sahara']
        
        return world

    except Exception as e:
        st.error(f"An error occurred during data processing: {e}")
        return None

# --- Main App Logic ---
world_data = get_country_boundaries()

if world_data is not None:
    st.markdown("This map displays the countries of the world. The boundaries of **Western Sahara** and the **Spanish exclaves in North Africa** have been merged into **Morocco**.")

    # Pydeck Map Visualization
    view_state = pdk.ViewState(latitude=28, longitude=0, zoom=1.5, pitch=0)
    geojson_layer = pdk.Layer("GeoJsonLayer", data=world_data, get_fill_color="[70, 130, 180, 160]", get_line_color=[255, 255, 255], pickable=True, stroked=True, filled=True, line_width_min_pixels=1)
    deck = pdk.Deck(layers=[geojson_layer], initial_view_state=view_state, map_style="mapbox://styles/mapbox/light-v9", tooltip={"text": "Country: {name}"})
    st.pydeck_chart(deck)
    
    st.markdown("---")
    
    # Data Preparation
    geojson_data = world_data.to_json()
    csv_df = pd.DataFrame({'Country': world_data['name'], 'Geometry_WKT': world_data['geometry'].to_wkt()})
    csv_bytes = csv_df.to_csv(index=False).encode('utf-8')
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

    # Download Section
    st.header("Download Data to Your Computer")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(label="Download as GeoJSON", data=geojson_data, file_name="countries_merged.geojson", mime="application/json")
    with col2:
        if kml_data:
            st.download_button(label="Download as KML", data=kml_data, file_name="countries_merged.kml", mime="application/vnd.google-earth.kml+xml")
    with col3:
        st.download_button(label="Download as CSV", data=csv_bytes, file_name="countries_with_geometry.csv", mime="text/csv")
    
    # Save to Server Section
    st.markdown("---")
    st.header("Save CSV on the Server")
    output_filename = "countries_with_geometry.csv"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, output_filename)
    if st.button(f"Save CSV to App Folder"):
        try:
            csv_df.to_csv(output_path, index=False)
            st.success(f"Successfully saved file to: {output_path}")
        except Exception as e:
            st.error(f"Failed to save file: {e}")
    
    # Raw CSV Display Section
    st.markdown("---")
    st.header("Raw CSV Content (with full geometry)")
    raw_csv_text = csv_bytes.decode('utf-8')
    st.code(raw_csv_text, language='text')

