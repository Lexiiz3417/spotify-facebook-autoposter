import os
import requests
import random
from datetime import date
from typing import Tuple

def dapatkan_lagu_dari_playlist() -> Tuple[str, str, str, str, str]:
    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
    playlist_id = os.environ.get('SPOTIFY_PLAYLIST_ID')

    auth_response = requests.post("https://accounts.spotify.com/api/token", {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    auth_response.raise_for_status()
    access_token = auth_response.json()['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}

    playlist_response = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", headers=headers)
    playlist_response.raise_for_status()
    items = playlist_response.json().get('items', [])
    if not items:
        raise ValueError("Playlist kosong atau tidak bisa diakses.")

    lagu_terpilih = random.choice(items)['track']
    nama_lagu = lagu_terpilih['name']
    nama_artis = lagu_terpilih['artists'][0]['name']
    artis_id = lagu_terpilih['artists'][0]['id']
    url_spotify = lagu_terpilih['external_urls']['spotify']
    url_cover_album = lagu_terpilih['album']['images'][0]['url']

    artist_response = requests.get(f"https://api.spotify.com/v1/artists/{artis_id}", headers=headers)
    artist_response.raise_for_status()
    genres = artist_response.json().get('genres', [])
    genre_utama = genres[0] if genres else "Music"

    return nama_lagu, nama_artis, url_spotify, url_cover_album, genre_utama

def dapatkan_songlink_dari_spotify(spotify_url: str) -> str:
    api_endpoint = "https://api.song.link/v1-alpha.1/links"
    try:
        response = requests.get(api_endpoint, params={'url': spotify_url}, timeout=10)
        if response.status_code == 200:
            return response.json().get('pageUrl', spotify_url)
    except requests.RequestException:
        pass
    return spotify_url

def posting_ke_facebook(pesan: str, url_gambar: str):
    page_id = os.environ.get('FACEBOOK_PAGE_ID')
    access_token = os.environ.get('FACEBOOK_ACCESS_TOKEN')

    upload_url = f"https://graph.facebook.com/v20.0/{page_id}/photos"
    params = {
        'url': url_gambar,
        'caption': pesan,
        'access_token': access_token,
        'published': 'true'  # Pastikan ini disetel
    }

    response = requests.post(upload_url, params=params)
    response.raise_for_status()

if __name__ == "__main__":
    try:
        start_date = date(2025, 7, 8)
        today_date = date.today()
        day_number = (today_date - start_date).days + 1

        nama_lagu, nama_artis, url_spotify, url_cover_album, genre_utama = dapatkan_lagu_dari_playlist()
        url_universal = dapatkan_songlink_dari_spotify(url_spotify)

        genre_lower = genre_utama.lower()
        if "lo-fi" in genre_lower or "chill" in genre_lower:
            mood, tags = "\ud83c\udf19 Chill vibes detected!", "#LoFi #ChillBeats"
        elif "rock" in genre_lower or "punk" in genre_lower:
            mood, tags = "\u26a1 Rock the day!", "#RockOn #AltRock"
        elif "pop" in genre_lower:
            mood, tags = "\ud83c\udfa4 Catchy pop anthem!", "#PopHits"
        elif "r&b" in genre_lower or "soul" in genre_lower:
            mood, tags = "\ud83d\udc9c Smooth and soulful", "#RnB #SoulMusic"
        elif "hip hop" in genre_lower or "rap" in genre_lower:
            mood, tags = "\ud83d\udd25 Drop the beat!", "#HipHop #RapDaily"
        elif "electronic" in genre_lower or "edm" in genre_lower or "bass" in genre_lower:
            mood, tags = "\ud83c\udfa7 Electronic energy boost!", "#EDM #Electro"
        elif "sad" in genre_lower or "acoustic" in genre_lower or "piano" in genre_lower:
            mood, tags = "\ud83c\udf27\ufe0f Soft, emotional tune", "#SadSongs #AcousticVibes"
        else:
            mood, tags = "\ud83c\udfb6 Your song of the day!", "#Vibes"

        tag_umum = "#MusicDiscovery #SongOfTheDay #NowPlaying"
caption_template = f"""/\u1020 - \u02d5 -\u30de \u26e7\u00b0. \u22c6\u0f3a\u263e\u0f3b\u22c6. \u00b0\u26e7
\u250d\u222a\u2500\u222a\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500  \ud834\udd1e\u2a7e\u1313\u05d3\u0ed3,\u266b,\u266a
\u2503 {mood}
\u2503 Day {day_number} – Music Pick 🎧
\u2503
\u2503   🎵 {nama_lagu}
\u2503   🎴 {nama_artis}
\u2503   🎼 Genre: {genre_utama.title()}
\u2503
\u2503 Listen Now:
\u2503 {url_universal}
\u2570\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500  \ud834\udd1e\u2a7e\u1313\u05d3\u0ed3,\u266b,\u266a

{tags} {tag_umum}"""

        pesan_post = caption_template.strip()
        posting_ke_facebook(pesan_post, url_cover_album)

    except Exception as e:
        print(f"Error: {e}")
