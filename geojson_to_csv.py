import streamlit as st
import geopandas as gpd
import json
import pandas as pd
from shapely.geometry import mapping

st.title("🌍 GeoJSON Country Splitter → CSV v.1.1")

uploaded = st.file_uploader("Upload world GeoJSON", type=["geojson", "json"])

if uploaded:
    # Load raw JSON
    data = json.load(uploaded)

    # GeoPandas can read directly from the FeatureCollection dict
    gdf = gpd.GeoDataFrame.from_features(
        data["features"],
        crs="EPSG:4326"  # your file explicitly uses EPSG:4326
    )

    # Validate required field
    if "NAME_ENGL" not in gdf.columns:
        st.error("The GeoJSON does not contain a 'NAME_ENGL' property.")
        st.stop()

    # Convert geometry to GeoJSON string
    def geom_to_geojson(geom):
        return json.dumps(mapping(geom))

    df = pd.DataFrame({
        "NAME_ENGL": gdf["NAME_ENGL"],
        "geometry_geojson": gdf["geometry"].apply(geom_to_geojson)
    })

    st.success("Successfully processed the GeoJSON!")

    st.dataframe(df.head())

    # Download CSV
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download CSV",
        data=csv_bytes,
        file_name="countries_geojson.csv",
        mime="text/csv"
    )
