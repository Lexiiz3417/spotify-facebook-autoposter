import os
import requests
import random
from datetime import date
from typing import Tuple, Optional

# --- SEMUA FUNGSI DI ATAS INI TETAP SAMA ---
def dapatkan_lagu_dari_playlist() -> Tuple[str, str, str, str, str]:
    # ... (tidak ada perubahan di sini)
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
    # ... (tidak ada perubahan di sini)
    print(f"🟢 Mengonversi link Spotify...")
    api_endpoint = "https://api.song.link/v1-alpha.1/links"
    try:
        response = requests.get(api_endpoint, params={'url': spotify_url}, timeout=10)
        if response.status_code == 200:
            return response.json().get('pageUrl', spotify_url)
    except requests.RequestException as e:
        print(f"❌ Gagal mengonversi link, error: {e}")
    return spotify_url
# ---------------------------------------------


# --- FUNGSI POSTING "JALAN PINTAS" ---
def posting_ke_facebook(pesan: str, url_gambar: str) -> Optional[str]:
    page_id = os.environ.get('FACEBOOK_PAGE_ID')
    album_id = os.environ.get('FACEBOOK_ALBUM_ID') # Kita coba pakai album_id di sini
    access_token = os.environ.get('FACEBOOK_ACCESS_TOKEN')
    
    print("🟢 Mencoba metode 'Jalan Pintas'...")
    # Kita tembak langsung ke endpoint album untuk upload dan publish
    # Ini cara yang lebih 'tua' tapi kita coba lagi dengan token baru
    # Jika album_id ada, targetkan ke album. Jika tidak, ke page.
    target_id = album_id if album_id else page_id
    
    print(f"🟢 Menargetkan ID: {target_id} untuk posting foto...")
    photo_upload_url = f"https://graph.facebook.com/v20.0/{target_id}/photos"
    
    payload = {
        'url': url_gambar,
        'caption': pesan, # 'caption' adalah parameter resmi untuk endpoint ini
        'published': 'true',
        'access_token': access_token
    }
    
    r_photo = requests.post(photo_upload_url, data=payload)

    print(f"📢 Respons dari 'Jalan Pintas': {r_photo.json()}")

    if r_photo.status_code != 200:
        print(f"❌ Gagal dengan metode 'Jalan Pintas': {r_photo.text}")
        r_photo.raise_for_status()

    response_data = r_photo.json()
    # Endpoint ini mengembalikan 'post_id' jika berhasil dipublikasikan ke timeline
    post_id = response_data.get('post_id')

    if post_id:
        print(f"✅ SUKSES! Postingan muncul di timeline dengan post_id: {post_id}")
    else:
        print("⚠️ Postingan berhasil di-upload tapi mungkin tidak muncul di timeline.")
        # Kita ambil id foto sebagai fallback untuk komentar
        post_id = response_data.get('id')
    
    return post_id

# --- FUNGSI KOMENTAR TETAP SAMA ---
def posting_komentar(post_id: str, pesan_komentar: str):
    # ... (tidak ada perubahan di sini)
    access_token = os.environ.get('FACEBOOK_ACCESS_TOKEN')
    print(f"🟢 Langkah 3: Memposting komentar ke post ID: {post_id}...")
    comment_url = f"https://graph.facebook.com/v20.0/{post_id}/comments"
    comment_payload = {
        'message': pesan_komentar,
        'access_token': access_token
    }
    r_comment = requests.post(comment_url, data=comment_payload)
    if r_comment.status_code != 200:
        print(f"❌ Gagal posting komentar: {r_comment.text}")
        r_comment.raise_for_status()
        
    print("✅ Komentar berhasil ditambahkan!")
# ---------------------------------------------


# --- BAGIAN BAWAH (MAIN) JUGA TETAP SAMA ---
if __name__ == "__main__":
    try:
        # ... (tidak ada perubahan di sini)
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
        
        genre_caption = f"   🎼 Genre: {genre_utama.title()}" if genre_utama != "Music" else ""

        caption_template_1 = f"""/ᐠ - ˕ -マ ⛧°. ⋆༺☾༻⋆. °⛧
╭∪─∪────────── 𝄞⨾𓍢ִ໋,♫,♪
┊ {mood}
┊ Day {day_number} – Music Pick 🎧
┊
┊   🎵 {nama_lagu}
┊   🎤 {nama_artis}
{genre_caption}
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
{genre_caption}
┊
┊ Listen Now:
┊ {url_universal}
╰─────────  𝄞⨾𓍢ִ໋,♫,♪

{tags} {tag_umum}"""

        caption_template_1 = os.linesep.join([s for s in caption_template_1.splitlines() if s.strip() != ""])
        caption_template_2 = os.linesep.join([s for s in caption_template_2.splitlines() if s.strip() != ""])

        list_of_captions = [caption_template_1, caption_template_2]
        pesan_post = random.choice(list_of_captions)
        print(f"Template caption yang terpilih: \n{pesan_post}")

        post_id = posting_ke_facebook(pesan_post, url_cover_album)

        if post_id:
            pesan_komentar = f"Hey guys! Di Day {day_number}, aku share lagu dari {nama_artis}. Menurut kalian gimana lagunya? Ada vibe yang sama di playlist kalian nggak? 🎧"
            posting_komentar(post_id, pesan_komentar)

        print(f"✅ Proses 'Day {day_number}' selesai dengan sukses.")
    except Exception as e:
        print(f"❌ Error terdeteksi: {e}")
# ---------------------------------------------
