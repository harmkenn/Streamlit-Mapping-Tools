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
    3. Merges Somaliland into Somalia.
    """
    try:
        url = "https://datahub.io/core/geo-countries/r/countries.geojson"
        world = gpd.read_file(url).to_crs(epsg=4326)
        
        # --- Step 1: Separate Spanish territories ---
        spain_full_geom = world[world['name'] == 'Spain'].geometry.squeeze()
        spain_african_parts = []
        spain_european_parts = []

        for poly in spain_full_geom.geoms:
            if 35 < poly.centroid.y < 37:
                spain_african_parts.append(poly)
            else:
                spain_european_parts.append(poly)
        
        spain_africa_union = unary_union(spain_african_parts)
        spain_new_geom = MultiPolygon(spain_european_parts)
        world.loc[world['name'] == 'Spain', 'geometry'] = gpd.GeoSeries([spain_new_geom], crs=world.crs).iloc[0]

        # --- Step 2: Merge Western Sahara + Spanish African exclaves into Morocco ---
        morocco_geom = world[world['name'] == 'Morocco'].geometry.squeeze()
        western_sahara_geom = world[world['name'] == 'Western Sahara'].geometry.squeeze()
        
        final_morocco_geom = unary_union([morocco_geom, western_sahara_geom, spain_africa_union])
        
        world.loc[world['name'] == 'Morocco', 'geometry'] = gpd.GeoSeries([final_morocco_geom], crs=world.crs).iloc[0]
        world = world[world['name'] != 'Western Sahara']

        # --- Step 3: Merge Somaliland into Somalia ---
        somaliland_names = ["Somaliland", "Somalia (Somaliland)", "Northwestern Somalia"]
        somaliland_rows = world[world['name'].isin(somaliland_names)]

        if not somaliland_rows.empty:
            somalia_geom = world[world['name'] == 'Somalia'].geometry.squeeze()
            somaliland_geom = unary_union(somaliland_rows.geometry)

            final_somalia_geom = unary_union([somalia_geom, somaliland_geom])

            world.loc[world['name'] == 'Somalia', 'geometry'] = gpd.GeoSeries(
                [final_somalia_geom], crs=world.crs
            ).iloc[0]

            world = world[~world['name'].isin(somaliland_names)]

        return world

    except Exception as e:
        st.error(f"An error occurred during data processing: {e}")
        return None

# --- Main App Logic ---
world_data = get_country_boundaries()

if world_data is not None:
    st.markdown("This map displays the countries of the world. The boundaries of **Western Sahara**, the **Spanish exclaves in North Africa**, and **Somaliland** have been merged into **Morocco** and **Somalia**, respectively.")

    # Pydeck Map Visualization
    view_state = pdk.ViewState(latitude=28, longitude=0, zoom=1.5, pitch=0)
    geojson_layer = pdk.Layer(
        "GeoJsonLayer",
        data=world_data,
        get_fill_color="[70, 130, 180, 160]",
        get_line_color=[255, 255, 255],
        pickable=True,
        stroked=True,
        filled=True,
        line_width_min_pixels=1
    )
    deck = pdk.Deck(
        layers=[geojson_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/light-v9",
        tooltip={"text": "Country: {name}"}
    )
    st.pydeck_chart(deck)
    
    st.markdown("---")
    
    # Data Preparation
    geojson_data = world_data.to_json()
    csv_df = pd.DataFrame({
        'Country': world_data['name'],
        'Geometry_WKT': world_data['geometry'].to_wkt()
    })
    csv_bytes = csv_df.to_csv(index=False).encode('utf-8')

    # KML Export
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
        st.download_button(
            label="Download as GeoJSON",
            data=geojson_data,
            file_name="countries_merged.geojson",
            mime="application/json"
        )
    with col2:
        if kml_data:
            st.download_button(
                label="Download as KML",
                data=kml_data,
                file_name="countries_merged.kml",
                mime="application/vnd.google-earth.kml+xml"
            )
    with col3:
        st.download_button(
            label="Download as CSV",
            data=csv_bytes,
            file_name="countries_with_geometry.csv",
            mime="text/csv"
        )
    
    # Save to Server Section
    st.markdown("---")
    st.header("Save CSV on the Server")
    output_filename = "countries_with_geometry.csv"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, output_filename)

    if st.button("Save CSV to App Folder"):
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
