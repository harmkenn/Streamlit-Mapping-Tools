import streamlit as st
import geopandas as gpd
import json

st.title("🌍 Africa Boundaries — Merge Western Sahara into Morocco")

st.write("""
This app loads Africa boundaries, reassigns Western Sahara to Morocco,
and dissolves them into a single Morocco polygon.
""")

if st.button("Generate Africa (WS merged into Morocco)"):
    try:
        # Load Natural Earth world boundaries
        world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))

        # Filter to Africa
        africa = world[world["continent"] == "Africa"].copy()

        # Identify Western Sahara
        ws_mask = africa["name"] == "Western Sahara"

        # Reassign Western Sahara to Morocco
        africa.loc[ws_mask, "name"] = "Morocco"

        # Dissolve by country name
        africa_merged = africa.dissolve(by="name", as_index=False)

        # Convert to GeoJSON
        africa_geojson = json.loads(africa_merged.to_json())

        st.success("Western Sahara successfully merged into Morocco!")
        st.json(africa_geojson)

        # Download
        st.download_button(
            "Download GeoJSON",
            json.dumps(africa_geojson),
            file_name="africa_ws_merged.geojson",
            mime="application/geo+json"
        )

    except Exception as e:
        st.error(f"Error: {e}")
