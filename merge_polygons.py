import streamlit as st
import json
from shapely.geometry import shape
from shapely.ops import unary_union

st.title("🧩 Merge Adjacent GeoJSON Polygons (Option B Dissolve)")

st.write("""
Paste two GeoJSON Polygon or MultiPolygon objects below.
The app will merge only polygons that touch or overlap.
""")

geo1_text = st.text_area("GeoJSON #1", height=250)
geo2_text = st.text_area("GeoJSON #2", height=250)

if st.button("Merge Polygons"):
    try:
        # Parse JSON
        g1 = json.loads(geo1_text)
        g2 = json.loads(geo2_text)

        # Convert to Shapely geometries
        geom1 = shape(g1)
        geom2 = shape(g2)

        # Geometric dissolve (Option B)
        merged = unary_union([geom1, geom2])

        # Convert back to GeoJSON
        merged_geojson = merged.__geo_interface__

        st.success("Merged successfully!")
        st.json(merged_geojson)

        # Download button
        merged_str = json.dumps(merged_geojson)
        st.download_button(
            "Download Merged GeoJSON",
            merged_str,
            file_name="merged.geojson",
            mime="application/json"
        )

    except Exception as e:
        st.error(f"Error: {e}")
