import streamlit as st
import geopandas as gpd
from shapely.ops import unary_union

st.set_page_config(layout="wide")

st.title("World Map with Merged Western Sahara and Morocco v1.0")

@st.cache_data
def get_country_boundaries():
    """
    Fetches and processes the country boundaries.
    Merges Western Sahara into Morocco.
    """
    try:
        # URL of the GeoJSON file
        url = "https://datahub.io/core/geo-countries/r/countries.geojson"
        
        # Read the GeoJSON file into a GeoDataFrame
        world = gpd.read_file(url)
        
        # Identify Morocco and Western Sahara
        morocco = world[world['ADMIN'] == 'Morocco'].geometry.squeeze()
        western_sahara = world[world['ADMIN'] == 'Western Sahara'].geometry.squeeze()
        
        # Merge the geometries
        merged_geometry = unary_union([morocco, western_sahara])
        
        # Update Morocco's geometry
        world.loc[world['ADMIN'] == 'Morocco', 'geometry'] = merged_geometry
        
        # Remove Western Sahara
        world = world[world['ADMIN'] != 'Western Sahara']
        
        return world

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

world_data = get_country_boundaries()

if world_data is not None:
    st.markdown("This map displays the countries of the world. The boundary of Western Sahara has been merged into Morocco.")
    
    # Display the map using Streamlit's st.map()
    st.map(world_data, color="#0000FF") # You can customize the color

    st.markdown("### Country Data")
    st.dataframe(world_data[['ADMIN', 'ISO_A3']].rename(columns={'ADMIN': 'Country', 'ISO_A3': 'ISO Code'}))

