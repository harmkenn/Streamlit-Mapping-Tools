import streamlit as st
import geopandas as gpd
from shapely.ops import unary_union

st.set_page_config(layout="wide")

st.title("World Map with Merged Western Sahara and Morocco v1.1")

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
        
        # Identify Morocco and Western Sahara using the 'name' property
        morocco = world[world['name'] == 'Morocco'].geometry.squeeze()
        western_sahara = world[world['name'] == 'Western Sahara'].geometry.squeeze()
        
        # Merge the geometries
        merged_geometry = unary_union([morocco, western_sahara])
        
        # Update Morocco's geometry
        world.loc[world['name'] == 'Morocco', 'geometry'] = merged_geometry
        
        # Remove Western Sahara
        world = world[world['name'] != 'Western Sahara']
        
        return world

    except Exception as e:
        st.error(f"An error occurred: {e}")
        # If you get an error, you can uncomment the next lines to see the available columns
        # world_check = gpd.read_file("https://datahub.io/core/geo-countries/r/countries.geojson")
        # st.write("Available columns:", world_check.columns)
        return None

world_data = get_country_boundaries()

if world_data is not None:
    st.markdown("This map displays the countries of the world. The boundary of Western Sahara has been merged into Morocco.")
    
    # Display the map using Streamlit's st.map()
    st.map(world_data, color="#0000FF")

    st.markdown("### Country Data")
    # Use 'name' and 'ISO3166-1-Alpha-3' for the dataframe
    st.dataframe(world_data[['name', 'ISO3166-1-Alpha-3']].rename(columns={'name': 'Country', 'ISO3166-1-Alpha-3': 'ISO Code'}))

