import streamlit as st
import geopandas as gpd
from shapely.ops import unary_union
import pydeck as pdk
import pandas as pd
import json

st.set_page_config(layout="wide")

st.title("World Map with Merged Western Sahara and Morocco v1.3")

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

        # Ensure the CRS is set to WGS84 for compatibility with web maps
        world = world.to_crs(epsg=4326)
        
        # Identify Morocco and Western Sahara geometries
        morocco_geom = world[world['name'] == 'Morocco'].geometry.squeeze()
        western_sahara_geom = world[world['name'] == 'Western Sahara'].geometry.squeeze()
        
        # Merge the geometries
        merged_geometry = unary_union([morocco_geom, western_sahara_geom])
        
        # Update Morocco's geometry in the GeoDataFrame
        world.loc[world['name'] == 'Morocco', 'geometry'] = gpd.GeoSeries([merged_geometry], crs=world.crs).iloc[0]
        
        # Remove the old Western Sahara entry
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
        pickable=True,
        stroked=True,
        filled=True,
        line_width_min_pixels=1,
    )
    deck = pdk.Deck(
        layers=[geojson_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/light-v9",
        tooltip={"text": "Country: {name}"}
    )
    st.pydeck_chart(deck)
    
    st.markdown("---") # Separator
    
    # --- Download Section ---
    st.header("Download Data")

    # 1. Prepare data for GeoJSON download
    geojson_data = world_data.to_json()

    # 2. Prepare data for KML download
    # To write to KML, we need to enable the KML driver in fiona (used by geopandas)
    gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
    kml_data = world_data.to_file(driver='KML', pretty=True, index=False)

    # 3. Prepare data for CSV with GeoJSON geometry
    # Create a new DataFrame with country name and geometry as a JSON string
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
        st.download_button(
            label="Download as KML",
            data=kml_data,
            file_name="countries_merged.kml",
            mime="application/vnd.google-earth.kml+xml",
        )
        
    with col3:
        st.download_button(
           label="Download as CSV with Geometry",
           data=csv_data,
           file_name="countries_with_geometry.csv",
           mime="text/csv",
        )
    
    # --- Display Data Table ---
    st.markdown("---") # Separator
    st.markdown("### Country Data Table")
    st.dataframe(world_data[['name', 'ISO3166-1-Alpha-3']].rename(columns={'name': 'Country', 'ISO3166-1-Alpha-3': 'ISO Code'}))

