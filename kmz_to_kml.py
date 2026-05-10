import streamlit as st
import zipfile
import os

def convert_kmz_to_kml(kmz_file):
    """Extracts the doc.kml from a KMZ file."""
    with zipfile.ZipFile(kmz_file, 'r') as z:
        # KMZ files usually contain a 'doc.kml' at the root
        kml_filenames = [f for f in z.namelist() if f.endswith('.kml')]
        
        if not kml_filenames:
            return None, "No KML file found inside the KMZ."
        
        # We take the first KML found (usually doc.kml)
        kml_data = z.read(kml_filenames[0])
        return kml_data, kml_filenames[0]

# --- UI Setup ---
st.set_page_config(page_title="KMZ to KML Converter", page_icon="🌍")

st.title("🌍 KMZ to KML Converter")
st.markdown("Upload a `.kmz` file to extract the underlying `.kml` data.")

uploaded_file = st.file_uploader("Choose a KMZ file", type="kmz")

if uploaded_file is not None:
    # Perform conversion
    kml_content, filename = convert_kmz_to_kml(uploaded_file)
    
    if kml_content:
        st.success(f"Successfully extracted: **{filename}**")
        
        # Create download button
        new_filename = uploaded_file.name.replace(".kmz", ".kml")
        st.download_button(
            label="📥 Download KML",
            data=kml_content,
            file_name=new_filename,
            mime="application/vnd.google-earth.kml+xml"
        )
    else:
        st.error(filename)

st.divider()
st.caption("Note: This app extracts the main KML file. It does not package local images or icons bundled in the KMZ.")
