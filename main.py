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

    # --- PERBAIKAN DI SINI ---
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

def posting_ke_facebook(pesan: str, url_gambar: str, day_number: int, artist_name: str):
    album_id, page_id, access_token = os.environ.get('FACEBOOK_ALBUM_ID'), os.environ.get('FACEBOOK_PAGE_ID'), os.environ.get('FACEBOOK_ACCESS_TOKEN')
    
    print(f"🟢 Langkah A: Mengunggah foto ke album ID: {album_id}...")
    upload_url = f"https://graph.facebook.com/v20.0/{album_id}/photos"
    upload_params = {'url': url_gambar, 'published': 'false', 'access_token': access_token}
    upload_response = requests.post(upload_url, params=upload_params)
    upload_response.raise_for_status()
    photo_id = upload_response.json()['id']
    print(f"Foto berhasil diunggah: {photo_id}")

    print("🟢 Langkah B: Posting ke feed...")
    feed_url = f"https://graph.facebook.com/v20.0/{page_id}/feed"
    feed_params = {'message': pesan, 'attached_media[0]': f'{{"media_fbid":"{photo_id}"}}', 'access_token': access_token}
    feed_response = requests.post(feed_url, params=feed_params)
    feed_response.raise_for_status()
    post_id = feed_response.json()['id']
    print(f"Berhasil posting di feed: {post_id}")

    print(f"🟢 Langkah C: Auto-komen...")
    comment_url = f"https://graph.facebook.com/v20.0/{post_id}/comments"
    comment_message = f"Hey guys! Di Day {day_number}, aku share lagu dari {artist_name}. Menurut kalian gimana lagunya? Ada vibe yang sama di playlist kalian nggak? 🎧"
    comment_params = {'message': comment_message, 'access_token': access_token}
    comment_response = requests.post(comment_url, params=comment_params)
    comment_response.raise_for_status()
    print("Komentar berhasil dikirim.")


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
┊ {mood.upper()}
┊ DAY {day_number}
┊
┊ Now Playing:
┊ {nama_lagu} — {nama_artis}
┊ ({genre_utama.title()})
┊
┊ {url_universal}
╰─────────  𝄞⨾𓍢ִ໋,♫,♪

{tags} {tag_umum}"""

        list_of_captions = [caption_template_1, caption_template_2]
        pesan_post = random.choice(list_of_captions)
        print(f"Template caption yang terpilih: \n{pesan_post}")

        posting_ke_facebook(pesan_post, url_cover_album, day_number, nama_artis)

        print(f"✅ Postingan 'Day {day_number}' berhasil dipublikasikan.")
    except Exception as e:
        print(f"❌ Error terdeteksi: {e}")
