import streamlit as st
import geopandas as gpd
from shapely.ops import unary_union

st.markdown("v1.0")

def merge_western_sahara_into_morocco(world_gdf):
    # Filter Morocco and Western Sahara
    morocco = world_gdf[world_gdf['NAME'] == 'Morocco']
    western_sahara = world_gdf[world_gdf['NAME'] == 'Western Sahara']
    
    # Perform union operation to merge geometries
    merged_geometry = unary_union([morocco.geometry.iloc[0], western_sahara.geometry.iloc[0]])
    
    # Update Morocco's geometry
    world_gdf.loc[world_gdf['NAME'] == 'Morocco', 'geometry'] = merged_geometry
    
    # Remove Western Sahara from the dataset
    world_gdf = world_gdf[world_gdf['NAME'] != 'Western Sahara']
    
    return world_gdf

def main():
    st.title("World Country Boundaries with Western Sahara Merged into Morocco")
    
    # Load Natural Earth dataset
    st.write("Downloading world country boundaries...")
    world_gdf = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    
    # Merge Western Sahara into Morocco
    st.write("Merging Western Sahara into Morocco...")
    modified_gdf = merge_western_sahara_into_morocco(world_gdf)
    
    # Display the map
    st.write("Modified country boundaries:")
    st.map(modified_gdf)
    
    # Allow user to download the modified GeoJSON
    st.write("Download the modified GeoJSON file:")
    geojson_data = modified_gdf.to_json()
    st.download_button(
        label="Download GeoJSON",
        data=geojson_data,
        file_name="modified_world_boundaries.geojson",
        mime="application/json"
    )

if __name__ == "__main__":
    main()
