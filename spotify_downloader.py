import streamlit as st
from spotdl import Spotdl
import pandas as pd

st.set_page_config(page_title="Spotify Playlist Extractor", layout="centered")

st.title("🎵 Spotify Playlist Extractor")
st.markdown("Paste a Spotify playlist URL to extract the list of songs and their individual URLs.")

# Sidebar for optional credentials
with st.sidebar:
    st.header("Settings")
    client_id = st.text_input("Client ID", value="", type="password", help="Required. Get it from Spotify Developer Dashboard.")
    client_secret = st.text_input("Client Secret", value="", type="password", help="Required. Get it from Spotify Developer Dashboard.")
    st.caption("Spotify Developer credentials are required for API access.")
    st.markdown("[Click here to create an app](https://developer.spotify.com/dashboard)")

    st.info("ℹ️ Credentials are recommended for large playlists to avoid rate limits.")

@st.cache_resource
def get_spotdl_instance(client_id, client_secret):
    """Initializes and caches the Spotdl instance to avoid repeated authentication."""
    return Spotdl(client_id=client_id, client_secret=client_secret)

query = st.text_input("Spotify Playlist URL", value="https://open.spotify.com/playlist/3sUduxBCejV1zTB61YrVjP")

if st.button("Get Tracklist"):
    if not query:
        st.warning("Please enter a URL.")
    else:
        with st.spinner("Fetching tracklist..."):
            try:
                c_id = client_id if client_id.strip() else None
                c_secret = client_secret if client_secret.strip() else None
                spotdl = get_spotdl_instance(c_id, c_secret)

                found_songs = spotdl.search([query])

                if not found_songs:
                    st.error("No songs found.")
                else:
                    st.success(f"Found {len(found_songs)} songs.")
                    
                    # Create DataFrame
                    data = []
                    for song in found_songs:
                        data.append({
                            "Artist": song.artist,
                            "Title": song.name,
                            "URL": song.url
                        })
                    
                    df = pd.DataFrame(data)
                    
                    # Display as a dataframe with links
                    st.dataframe(
                        df,
                        column_config={
                            "URL": st.column_config.LinkColumn("Spotify Link")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    # CSV Download
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Download as CSV",
                        csv,
                        "spotify_tracks.csv",
                        "text/csv",
                        key='download-csv'
                    )

            except Exception as e:
                st.error(f"An error occurred: {e}")