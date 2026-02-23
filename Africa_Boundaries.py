import streamlit as st
import geopandas as gpd
import json
import requests
from shapely.ops import unary_union

st.title("🌍 Africa Country Boundaries — GeoJSON Exporter (Updated for GeoPandas 1.0+)")

st.write("""
This app downloads Natural Earth boundaries directly from the official source,
filters to Africa, and optionally merges Western Sahara into Morocco.
""")

merge_ws = st.checkbox("Merge Western Sahara into Morocco", value=True)

if st.button("Generate Africa GeoJSON"):
    try:
        # Natural Earth 110m Admin 0 Countries (official download URL)
        url = "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_countries.zip"

        st.write("Downloading Natural Earth dataset…")
        r = requests.get(url)

        # Save ZIP to memory
        with open("ne_countries.zip", "wb") as f:
            f.write(r.content)

        # Load with GeoPandas
        world = gpd.read_file("zip://ne_countries.zip")

        # Filter to Africa
        africa = world[world["CONTINENT"] == "Africa"].copy()

        # Optional: merge Western Sahara into Morocco
        if merge_ws:
            ws_mask = africa["NAME"] == "Western Sahara"
            africa.loc[ws_mask, "NAME"] = "Morocco"
            africa = africa.dissolve(by="NAME", as_index=False)

        # Convert to GeoJSON
        africa_geojson = json.loads(africa.to_json())

        st.success("Africa GeoJSON generated successfully!")
        st.json(africa_geojson)

        # Download button
        st.download_button(
            label="Download Africa GeoJSON",
            data=json.dumps(africa_geojson),
            file_name="africa_countries.geojson",
            mime="application/geo+json"
        )

    except Exception as e:
        st.error(f"Error: {e}")
