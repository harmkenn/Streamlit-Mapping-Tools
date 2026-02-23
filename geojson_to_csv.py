import streamlit as st
import geopandas as gpd
import json
import pandas as pd
from shapely.geometry import mapping

st.title("🌍 GeoJSON Country Splitter → CSV 1.5")

uploaded = st.file_uploader("Upload world GeoJSON", type=["geojson", "json"])

if uploaded:
    data = json.load(uploaded)

    gdf = gpd.GeoDataFrame.from_features(
        data["features"],
        crs="EPSG:4326"
    )

    # Show available columns
    st.write("Detected columns:", list(gdf.columns))

    # Try to find a name field automatically
    possible_name_fields = [
        "NAME_ENGL", "name_engl",
        "CNTR_NAME", "cntr_name",
        "NAME", "name",
        "ADMIN", "admin",
        "ISO3_CODE", "iso3_code",
        "iso_a3"
    ]

    name_field = None
    for field in possible_name_fields:
        if field in gdf.columns:
            name_field = field
            break

    if not name_field:
        st.error("No suitable country name field found.")
        st.stop()

    st.success(f"Using '{name_field}' as the country name field.")

    def geom_to_geojson(geom):
        return json.dumps(mapping(geom))

    df = pd.DataFrame({
        "country_name": gdf[name_field],
        "geometry_geojson": gdf["geometry"].apply(geom_to_geojson)
    })

    st.dataframe(df)

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    
    st.download_button(
        label="Download CSV",
        data=csv_bytes,
        file_name="countries_geojson.csv",
        mime="text/csv"
    )

