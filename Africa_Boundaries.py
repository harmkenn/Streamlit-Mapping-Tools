import streamlit as st
import geopandas as gpd
from shapely.ops import unary_union
import pydeck as pdk
import pandas as pd
import json
import tempfile
import os

st.set_page_config(layout="wide")

st.title("World Map with Merged Western Sahara and Morocco v1.4")

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
    
    # --- Download Section ---
    st.header("Download Data")

    # 1. Prepare GeoJSON data (in memory)
    geojson_data = world_data.to_json()

    # 2. Prepare KML data by writing to a temporary file and reading back
    kml_data = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".kml", delete=False) as tmpfile:
            tmp_path = tmpfile.name
            # The line below that caused the error has been removed.
            # We now write directly to the temporary file path.
            world_data.to_file(tmp_path, driver='KML')
        
        # Read the content of the temporary file into a variable
        with open(tmp_path, 'rb') as f:
            kml_data = f.read()
    finally:
        # Clean up the temporary file
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)

    # 3. Prepare CSV data (in memory)
    csv_df = pd.DataFrame({
        'Country': world_data['name'],
        'GeoJSON_Geometry': world_data['geometry'].apply(lambda geom: json.dumps(geom.__geo_interface__))
    })
    csv_data = csv_df.to_csv(index=False).encode('utf-8')

    # Create columns for download buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            label="Download as GeoJSON",
            data=geojson_data,
            file_name="countries_merged.geojson",
            mime="application/json",
        )
    
    with col2:
        if kml_data: # Only show button if KML data was created successfully
            st.download_button(
                label="Download as KML",
                data=kml_data,
                file_name="countries_merged.kml",
                mime="application/vnd.google-earth.kml+xml",
            )
        else:
            st.warning("Could not generate KML file.")
        
    with col3:
        st.download_button(
           label="Download as CSV with Geometry",
           data=csv_data,
           file_name="countries_with_geometry.csv",
           mime="text/csv",
        )
    
    st.markdown("---")
    st.markdown("### Country Data Table")
    st.dataframe(world_data[['name', 'ISO3166-1-Alpha-3']].rename(columns={'name': 'Country', 'ISO3166-1-Alpha-3': 'ISO Code'}))
