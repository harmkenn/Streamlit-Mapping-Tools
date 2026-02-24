import streamlit as st
import geopandas as gpd
from shapely.ops import unary_union
import pydeck as pdk

st.set_page_config(layout="wide")

st.title("World Map with Merged Western Sahara and Morocco v1.2")

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

world_data = get_country_boundaries()

if world_data is not None:
    st.markdown("This map displays the countries of the world. The boundary of Western Sahara has been merged into Morocco.")

    # --- Pydeck Map Visualization ---
    
    # 1. Set the initial view for the map
    view_state = pdk.ViewState(
        latitude=20,  # Center the map view
        longitude=0,
        zoom=1.2,
        pitch=0,
    )

    # 2. Define the layer for the country polygons
    geojson_layer = pdk.Layer(
        "GeoJsonLayer",
        data=world_data,
        get_fill_color="[70, 130, 180, 160]",  # SteelBlue with some transparency
        get_line_color=[255, 255, 255],
        pickable=True,  # Allow hovering to see tooltips
        stroked=True,
        filled=True,
        line_width_min_pixels=1,
    )

    # 3. Create the Deck object with the layer and view
    deck = pdk.Deck(
        layers=[geojson_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/light-v9",
        tooltip={"text": "Country: {name}"} # Add a tooltip to show country name on hover
    )

    # 4. Render the pydeck chart in Streamlit
    st.pydeck_chart(deck)
    # --- End of Pydeck Map ---

    st.markdown("### Country Data")
    st.dataframe(world_data[['name', 'ISO3166-1-Alpha-3']].rename(columns={'name': 'Country', 'ISO3166-1-Alpha-3': 'ISO Code'}))
