import os
import requests
import random
# Final test!
def dapatkan_lagu_dari_playlist():
    """Mengambil satu lagu acak beserta cover albumnya dari playlist Spotify."""
    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
    playlist_id = os.environ.get('SPOTIFY_PLAYLIST_ID')
    
    print("Mendapatkan token dari Spotify...")
    auth_response = requests.post("https://accounts.spotify.com/api/token", {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    auth_response.raise_for_status() # Berhenti jika ada error
    access_token = auth_response.json()['access_token']
    
    print(f"Mengambil lagu dari playlist ID: {playlist_id}")
    headers = {'Authorization': f'Bearer {access_token}'}
    playlist_response = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", headers=headers)
    playlist_response.raise_for_status()
    
    items = playlist_response.json().get('items', [])
    if not items:
        raise ValueError("Playlist kosong atau tidak bisa diakses.")
        
    lagu_terpilih = random.choice(items)['track']
    
    nama_lagu = lagu_terpilih['name']
    nama_artis = lagu_terpilih['artists'][0]['name']
    url_spotify = lagu_terpilih['external_urls']['spotify']
    
    # --- BARIS BARU: Mengambil URL cover album ---
    # Spotify menyediakan beberapa ukuran, kita ambil yang paling besar (pertama di daftar)
    url_cover_album = lagu_terpilih['album']['images'][0]['url']
    
    print(f"Lagu terpilih: {nama_lagu} oleh {nama_artis}")
    # --- DIUBAH: Mengembalikan URL cover album juga ---
    return nama_lagu, nama_artis, url_spotify, url_cover_album

def dapatkan_songlink_dari_spotify(spotify_url: str) -> str:
    """Mengonversi URL Spotify menjadi URL song.link universal."""
    print(f"Mengonversi link Spotify: {spotify_url}")
    api_endpoint = "https://api.song.link/v1-alpha.1/links"
    try:
        response = requests.get(api_endpoint, params={'url': spotify_url}, timeout=10)
        if response.status_code == 200:
            return response.json().get('pageUrl', spotify_url)
    except requests.RequestException as e:
        print(f"Gagal mengonversi link, error: {e}")
    return spotify_url

# --- FUNGSI DIUBAH: Untuk memposting FOTO dengan CAPTION ---
def posting_ke_facebook(pesan: str, url_gambar: str):
    """Mengirim FOTO dengan caption ke Halaman Facebook."""
    page_id = os.environ.get('FACEBOOK_PAGE_ID')
    access_token = os.environ.get('FACEBOOK_ACCESS_TOKEN')
    
    print("Mempersiapkan untuk posting foto ke Facebook...")
    # --- DIUBAH: Endpoint diubah dari /feed menjadi /photos ---
    url = f"https://graph.facebook.com/v20.0/{page_id}/photos"
    params = {
        # --- DIUBAH: 'message' menjadi 'caption' untuk post foto ---
        'caption': pesan,
        # --- BARIS BARU: Menambahkan URL gambar yang akan diposting ---
        'url': url_gambar,
        'access_token': access_token
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    print("Berhasil memposting foto ke Facebook!")

if __name__ == "__main__":
    try:
        print("Memulai proses autoposter...")
        # --- DIUBAH: Menerima 4 nilai dari fungsi ---
        nama_lagu, nama_artis, url_spotify, url_cover_album = dapatkan_lagu_dari_playlist()
        url_universal = dapatkan_songlink_dari_spotify(url_spotify)
        
        pesan_post = f"""🎧 Song of the Day 🎶

🎵 Title: {nama_lagu}
🎤 Artist: {nama_artis}

Listen on your favorite platform:
{url_universal}

#SongoftheDay #MusicDiscovery #NowPlaying"""
        
        # --- DIUBAH: Mengirim pesan dan URL gambar ke fungsi posting ---
        posting_ke_facebook(pesan_post, url_cover_album)
        print("Proses selesai dengan sukses.")
    except Exception as e:
        print(f"Terjadi error: {e}")
        # exit(1) # Memberi sinyal error ke GitHub Actions
