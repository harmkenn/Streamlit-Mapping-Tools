import streamlit as st

# --- Home Page Function ---
def home():
    # Set default config for the home page (resets layout if coming from a wide page)
    st.set_page_config(page_title="Streamlit Tools Hub", layout="centered")
    
    st.title("🚀 Streamlit Tools Hub")
    st.write("Welcome! Select a tool from the sidebar to get started.")
    
    st.markdown("### 🗺️ Mapping Tools")
    st.info("**Africa Boundaries**: World map with custom merged boundaries (Western Sahara → Morocco).")
    st.info("**GeoJSON to KML**: Extract African countries and convert to KML.")
    st.info("**Merge Polygons**: Merge adjacent GeoJSON polygons (Dissolve).")
    st.info("**GeoJSON to CSV**: Split GeoJSON countries into CSV format.")
    st.info("**KMZ to KML**: Split KMZ into KML format.")
    
    st.markdown("### 🎵 Utilities")
    st.success("**Spotify Extractor**: Get song URLs from playlists.")

# --- Navigation Setup ---
pages = {
    "Home": [
        st.Page(home, title="Home", icon="🏠"),
    ],
    "Mapping Tools": [
        st.Page("Africa_Boundaries.py", title="Africa Boundaries", icon="🌍"),
        st.Page("geojson_to_kml.py", title="GeoJSON to KML", icon="🗺️"),
        st.Page("merge_polygons.py", title="Merge Polygons", icon="🧩"),
        st.Page("geojson_to_csv.py", title="GeoJSON to CSV", icon="📄"),
        st.Page("kmz_to_kml.py", title="KMZ to KML", icon="📄"),
    ],
    "Utilities": [
        st.Page("spotify_downloader.py", title="Spotify Extractor", icon="🎵"),
    ],
}

pg = st.navigation(pages)
pg.run()
