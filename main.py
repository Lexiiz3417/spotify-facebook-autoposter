import os
import requests
import random
from datetime import date
from typing import Tuple

def dapatkan_lagu_dari_playlist() -> Tuple[str, str, str, str, str]:
    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
    playlist_id = os.environ.get('SPOTIFY_PLAYLIST_ID')

    print("🟢 Mendapatkan token dari Spotify...")
    auth_response = requests.post("https://accounts.spotify.com/api/token", {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    auth_response.raise_for_status()
    access_token = auth_response.json()['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}

    print(f"🟢 Mengambil lagu dari playlist ID: {playlist_id}")
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

    print(f"🟢 Mengambil genre dari artis: {nama_artis}")
    artist_response = requests.get(f"https://api.spotify.com/v1/artists/{artis_id}", headers=headers)
    artist_response.raise_for_status()
    genres = artist_response.json().get('genres', [])
    genre_utama = genres[0] if genres else "Music"

    print(f"Lagu terpilih: {nama_lagu} oleh {nama_artis} | Genre: {genre_utama}")
    return nama_lagu, nama_artis, url_spotify, url_cover_album, genre_utama

def dapatkan_songlink_dari_spotify(spotify_url: str) -> str:
    print(f"🟢 Mengonversi link Spotify...")
    api_endpoint = "https://api.song.link/v1-alpha.1/links"
    try:
        response = requests.get(api_endpoint, params={'url': spotify_url}, timeout=10)
        if response.status_code == 200:
            return response.json().get('pageUrl', spotify_url)
    except requests.RequestException as e:
        print(f"❌ Gagal mengonversi link, error: {e}")
    return spotify_url

# --- FUNGSI POSTING BARU DENGAN TARGET ALBUM & TIMELINE ---
# --- FUNGSI POSTING BARU DENGAN TARGET ALBUM & TIMELINE (PLUS DEBUGGING) ---
def posting_ke_facebook(pesan: str, url_gambar: str):
    page_id = os.environ.get('FACEBOOK_PAGE_ID')
    album_id = os.environ.get('FACEBOOK_ALBUM_ID') 
    access_token = os.environ.get('FACEBOOK_ACCESS_TOKEN')
    
    # --- LANGKAH 1: Upload foto ke ALBUM SPESIFIK ---
    print(f"🟢 Langkah 1: Mengunggah foto ke album ID: {album_id}...")
    photo_upload_url = f"https://graph.facebook.com/v20.0/{album_id}/photos"
    
    photo_payload = {
        'url': url_gambar,
        'access_token': access_token
    }
    
    r_photo = requests.post(photo_upload_url, data=photo_payload)
    
    # --- TAMBAHAN DEBUGGING ---
    print("📢 Respons dari upload foto:")
    print(r_photo.json()) # Kita print responsnya biar keliatan
    # -------------------------

    r_photo.raise_for_status()
    photo_data = r_photo.json()
    photo_id = photo_data['id']
    print(f"✅ Foto berhasil diunggah ke album dengan ID: {photo_id}")

    # --- LANGKAH 2: Buat postingan di feed dengan melampirkan foto ---
    print("🟢 Langkah 2: Membuat postingan di timeline...")
    feed_post_url = f"https://graph.facebook.com/v20.0/{page_id}/feed"
    feed_payload = {
        'message': pesan,
        'attached_media[0]': f'{{"media_fbid":"{photo_id}"}}',
        'access_token': access_token
    }

    r_feed = requests.post(feed_post_url, data=feed_payload)

    # --- TAMBAHAN DEBUGGING ---
    print("📢 Respons dari post ke feed:")
    print(r_feed.json()) # Kita print juga respons dari feed
    # -------------------------

    r_feed.raise_for_status()
    print("✅ Postingan berhasil dipublikasikan ke timeline!")
    
if __name__ == "__main__":
    try:
        print("🟢 Memulai proses autoposting...")
        start_date = date(2025, 7, 8)
        today_date = date.today()
        day_number = (today_date - start_date).days + 1

        nama_lagu, nama_artis, url_spotify, url_cover_album, genre_utama = dapatkan_lagu_dari_playlist()
        url_universal = dapatkan_songlink_dari_spotify(url_spotify)
        
        genre_lower = genre_utama.lower()
        if "lo-fi" in genre_lower or "chill" in genre_lower: mood, tags = "🌙 Chill vibes detected!", "#LoFi #ChillBeats"
        elif "rock" in genre_lower or "punk" in genre_lower: mood, tags = "⚡ Rock the day!", "#RockOn #AltRock"
        elif "pop" in genre_lower: mood, tags = "🎤 Catchy pop anthem!", "#PopHits"
        elif "r&b" in genre_lower or "soul" in genre_lower: mood, tags = "💜 Smooth and soulful", "#RnB #SoulMusic"
        elif "hip hop" in genre_lower or "rap" in genre_lower: mood, tags = "🔥 Drop the beat!", "#HipHop #RapDaily"
        elif "electronic" in genre_lower or "edm" in genre_lower or "bass" in genre_lower: mood, tags = "🎧 Electronic energy boost!", "#EDM #Electro"
        elif "sad" in genre_lower or "acoustic" in genre_lower or "piano" in genre_lower: mood, tags = "🌧️ Soft, emotional tune", "#SadSongs #AcousticVibes"
        else: mood, tags = "🎶 Your song of the day!", "#Vibes"
        tag_umum = "#MusicDiscovery #SongOfTheDay #NowPlaying"

        caption_template_1 = f"""/ᐠ - ˕ -マ ⛧°. ⋆༺☾༻⋆. °⛧
╭∪─∪────────── 𝄞⨾𓍢ִ໋,♫,♪
┊ {mood}
┊ Day {day_number} – Music Pick 🎧
┊
┊   🎵 {nama_lagu}
┊   🎤 {nama_artis}
┊   🎼 Genre: {genre_utama.title()}
┊
┊ Listen Now:
┊ {url_universal}
╰─────────────  𝄞⨾𓍢ִ໋,♫,♪

{tags} {tag_umum}"""

        caption_template_2 = f"""⊹ ࣪ ﹏𓊝﹏𓂁﹏⊹ ࣪ ˖

╭───────── 𝄞⨾𓍢ִ໋,♫,♪
┊ {mood}
┊ Day {day_number} – Music Pick 🎧
┊
┊   🎵 {nama_lagu}
┊   🎤 {nama_artis}
┊   🎼 Genre: {genre_utama.title()}
┊
┊ Listen Now:
┊ {url_universal}
╰─────────  𝄞⨾𓍢ִ໋,♫,♪

{tags} {tag_umum}"""

        list_of_captions = [caption_template_1, caption_template_2]
        pesan_post = random.choice(list_of_captions)
        print(f"Template caption yang terpilih: \n{pesan_post}")

        # Memanggil fungsi posting yang sudah diperbaiki
        posting_ke_facebook(pesan_post, url_cover_album)

        print(f"✅ Proses 'Day {day_number}' selesai.")
    except Exception as e:
        print(f"❌ Error terdeteksi: {e}")
