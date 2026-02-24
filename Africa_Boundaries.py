import streamlit as st
import geopandas as gpd
import json
import requests
import zipfile
import tempfile
import os
import io   # ← THIS is the missing import


st.title("🌍 Africa Country Boundaries — GeoJSON Exporter (Fully Compatible) v1.4")

st.write("""
This app downloads Natural Earth boundaries directly from the official source,
extracts them safely, filters to Africa, and optionally merges Western Sahara into Morocco.
""")

merge_ws = st.checkbox("Merge Western Sahara into Morocco", value=True)

if st.button("Generate Africa GeoJSON"):
    try:
        # Natural Earth 110m Admin 0 Countries (official download URL)
        url = "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_countries.zip"

        st.write("Downloading Natural Earth dataset…")
        r = requests.get(url)

        # Create a temporary directory
        tmpdir = tempfile.mkdtemp()

        # Extract ZIP into the temp directory
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            z.extractall(tmpdir)

        # Find the .shp file
        shp_file = None
        for f in os.listdir(tmpdir):
            if f.endswith(".shp"):
                shp_file = os.path.join(tmpdir, f)
                break

        if shp_file is None:
            raise Exception("Shapefile not found inside ZIP")

        # Load shapefile normally (no vsizip)
        world = gpd.read_file(shp_file)

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
