import os
import requests
import random
from datetime import date

def dapatkan_lagu_dari_playlist():
    client_id, client_secret, playlist_id = os.environ.get('SPOTIFY_CLIENT_ID'), os.environ.get('SPOTIFY_CLIENT_SECRET'), os.environ.get('SPOTIFY_PLAYLIST_ID')
    print("Mendapatkan token dari Spotify...")
    auth_response = requests.post("https://accounts.spotify.com/api/token", {'grant_type': 'client_credentials','client_id': client_id,'client_secret': client_secret,})
    auth_response.raise_for_status()
    access_token = auth_response.json()['access_token']
    print(f"Mengambil lagu dari playlist ID: {playlist_id}")
    headers = {'Authorization': f'Bearer {access_token}'}
    playlist_response = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", headers=headers)
    playlist_response.raise_for_status()
    items = playlist_response.json().get('items', [])
    if not items: raise ValueError("Playlist kosong atau tidak bisa diakses.")
    lagu_terpilih = random.choice(items)['track']
    nama_lagu, nama_artis = lagu_terpilih['name'], lagu_terpilih['artists'][0]['name']
    url_spotify, url_cover_album = lagu_terpilih['external_urls']['spotify'], lagu_terpilih['album']['images'][0]['url']
    print(f"Lagu terpilih: {nama_lagu} oleh {nama_artis}")
    return nama_lagu, nama_artis, url_spotify, url_cover_album

def dapatkan_songlink_dari_spotify(spotify_url: str) -> str:
    print(f"Mengonversi link Spotify: {spotify_url}")
    api_endpoint = "https://api.song.link/v1-alpha.1/links"
    try:
        response = requests.get(api_endpoint, params={'url': spotify_url}, timeout=10)
        if response.status_code == 200: return response.json().get('pageUrl', spotify_url)
    except requests.RequestException as e: print(f"Gagal mengonversi link, error: {e}")
    return spotify_url

def posting_ke_facebook(pesan: str, url_gambar: str):
    page_id, access_token = os.environ.get('FACEBOOK_PAGE_ID'), os.environ.get('FACEBOOK_ACCESS_TOKEN')
    print("Mempersiapkan untuk posting foto ke Facebook...")
    url = f"https://graph.facebook.com/v20.0/{page_id}/photos"
    params = {'caption': pesan, 'url': url_gambar, 'access_token': access_token}
    response = requests.post(url, params=params)
    response.raise_for_status()
    print("Berhasil memposting foto ke Facebook!")

if __name__ == "__main__":
    try:
        print("Memulai proses autoposter...")

        # Logika baru untuk menghitung hari berdasarkan tanggal mulai
        start_date = date(2025, 6, 28) # Format: TAHUN, BULAN, TANGGAL
        today_date = date.today()
        day_number = (today_date - start_date).days + 1

        nama_lagu, nama_artis, url_spotify, url_cover_album = dapatkan_lagu_dari_playlist()
        url_universal = dapatkan_songlink_dari_spotify(url_spotify)

        pesan_post = f"""Daily Music (Day {day_number})
