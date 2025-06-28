import os
import requests
import random
from datetime import datetime
from zoneinfo import ZoneInfo
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def tambahkan_watermark(image_url: str, day_text: str, code_text: str) -> bytes:
    """Mendownload gambar, menambahkan dua baris watermark, dan mengembalikannya sebagai data bytes."""
    print("Mendownload gambar untuk watermark...")
    response = requests.get(image_url)
    response.raise_for_status()
    
    image = Image.open(BytesIO(response.content)).convert("RGBA")
    draw = ImageDraw.Draw(image)
    
    # Memuat font. Pastikan file arial.ttf ada di repositori.
    try:
        font_besar = ImageFont.truetype("arial.ttf", 40)
        font_kecil = ImageFont.truetype("arial.ttf", 25)
    except IOError:
        print("File font 'arial.ttf' tidak ditemukan! Menggunakan font default.")
        font_besar = ImageFont.load_default()
        font_kecil = ImageFont.load_default()

    # Membuat latar belakang semi-transparan untuk teks agar mudah dibaca
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    rect_height = 100
    draw_overlay.rectangle(
        (0, image.height - rect_height, image.width, image.height),
        fill=(0, 0, 0, 100)
    )
    image = Image.alpha_composite(image, overlay)
    draw = ImageDraw.Draw(image)

    # Menambahkan teks watermark di pojok kanan bawah
    pos_x = image.width - 20
    pos_y_code = image.height - 40
    pos_y_day = image.height - 75
    draw.text((pos_x, pos_y_day), day_text, font=font_besar, fill=(255, 255, 255), anchor="ra")
    draw.text((pos_x, pos_y_code), code_text, font=font_kecil, fill=(200, 200, 200), anchor="ra")
    
    output_buffer = BytesIO()
    image.convert("RGB").save(output_buffer, format="JPEG")
    print("Watermark berhasil ditambahkan.")
    return output_buffer.getvalue()

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

def posting_ke_facebook(pesan: str, image_data: bytes):
    page_id, access_token = os.environ.get('FACEBOOK_PAGE_ID'), os.environ.get('FACEBOOK_ACCESS_TOKEN')
    print("Mempersiapkan untuk upload foto ke Facebook...")
    url = f"https://graph.facebook.com/v20.0/{page_id}/photos"
    params = {'caption': pesan,'access_token': access_token}
    files = {'source': image_data}
    response = requests.post(url, params=params, files=files)
    response.raise_for_status()
    print("Berhasil memposting foto ke Facebook!")

if __name__ == "__main__":
    try:
        print("Memulai proses autoposter...")
        day_number = os.environ.get('DAY_NUMBER', '1')
        wib_tz = ZoneInfo("Asia/Jakarta")
        now_wib = datetime.now(wib_tz)
        day = now_wib.strftime("%d")
        month = now_wib.strftime("%m")
        month_digits = '2' if now_wib.month >= 10 else '1'
        year = now_wib.strftime("%y")
        hour = str(int(now_wib.strftime("%I")))
        minute = now_wib.strftime("%M")
        ampm_code = '2' if now_wib.strftime("%p") == "PM" else '1'
        custom_code = f"/M{day}{month.lstrip('0')}{month_digits}{year}{hour}{minute}{ampm_code}"
        
        nama_lagu, nama_artis, url_spotify, url_cover_album = dapatkan_lagu_dari_playlist()
        
        watermark_day_text = f"Daily Music (Day {day_number})"
        image_data_with_watermark = tambahkan_watermark(url_cover_album, watermark_day_text, custom_code)
        
        url_universal = dapatkan_songlink_dari_spotify(url_spotify)
        pesan_post = f"""{watermark_day_text}

🎵 Title: {nama_lagu}
🎤 Artist: {nama_artis}

Listen on your favorite platform:
{url_universal}

#SongoftheDay #MusicDiscovery #NowPlaying

{custom_code}"""
        
        posting_ke_facebook(pesan_post, image_data_with_watermark)
        print("Proses selesai dengan sukses.")
        
    except Exception as e:
        print(f"Terjadi error: {e}")
