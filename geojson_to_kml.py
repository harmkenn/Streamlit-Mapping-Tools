import streamlit as st
import geopandas as gpd
from shapely.geometry import shape
import json
import tempfile

st.title("🌍 Africa Country Extractor & KML Converter")

st.write(
    "Upload a world GeoJSON file. This app will filter out only African countries "
    "and convert the result into a downloadable KML file."
)

uploaded = st.file_uploader("Upload world GeoJSON", type=["geojson", "json"])

# List of all African countries
africa_countries = {
    "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cabo Verde",
    "Cameroon", "Central African Republic", "Chad", "Comoros", "Congo",
    "Democratic Republic of the Congo", "Djibouti", "Egypt", "Equatorial Guinea",
    "Eritrea", "Eswatini", "Ethiopia", "Gabon", "Gambia", "Ghana", "Guinea",
    "Guinea-Bissau", "Kenya", "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi",
    "Mali", "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger",
    "Nigeria", "Rwanda", "Sao Tome and Principe", "Senegal", "Seychelles",
    "Sierra Leone", "Somalia", "South Africa", "South Sudan", "Sudan", "Tanzania",
    "Togo", "Tunisia", "Uganda", "Zambia", "Zimbabwe"
}

if uploaded:
    try:
        # Load GeoJSON into GeoDataFrame
        data = json.load(uploaded)
        gdf = gpd.GeoDataFrame.from_features(data["features"])

        # Normalize column names
        gdf.columns = [c.lower() for c in gdf.columns]

        # Try to detect the name field
        possible_name_fields = ["name", "NAME", "admin", "ADMIN", "country", "COUNTRY"]
        name_field = None
        for f in possible_name_fields:
            if f.lower() in gdf.columns:
                name_field = f.lower()
                break

        if not name_field:
            st.error("Could not find a country name field in your GeoJSON.")
        else:
            africa = gdf[gdf[name_field].isin(africa_countries)]

            st.success(f"Found {len(africa)} African countries.")

            # Convert to KML using a temporary file
            with tempfile.NamedTemporaryFile(suffix=".kml") as tmp:
                africa.to_file(tmp.name, driver="KML")

                with open(tmp.name, "rb") as f:
                    kml_bytes = f.read()

                st.download_button(
                    label="Download Africa Countries as KML",
                    data=kml_bytes,
                    file_name="africa_countries.kml",
                    mime="application/vnd.google-earth.kml+xml"
                )

            st.write("Preview of filtered data:")
            st.dataframe(africa[[c for c in africa.columns if c != "geometry"]])

    except Exception as e:
        st.error(f"Error processing file: {e}")
