📦 Panduan Transfer Project & Upload GitHub
Project: Kopi Nusantara (Kivy App)
🖥️ CARA 1 — Kirim via GitHub (Direkomendasikan)
A. Upload ke GitHub (dari laptop asal)
IMPORTANT

Pastikan sudah install Git di laptop asal. Cek: git --version

Langkah-langkah:

1. Buat akun GitHub (kalau belum)
Buka https://github.com → Sign Up
2. Buat repository baru di GitHub
Klik tombol "+" → New repository
Isi nama repo, misal: kopi-nusantara
Pilih Public atau Private
JANGAN centang "Add README" (biarkan kosong)
Klik Create repository
3. Inisialisasi Git di folder project (jika belum)
powershell

# Masuk ke folder project dulu
cd "c:\laragon\www\reyna vscode"
# Inisialisasi git (skip jika sudah ada folder .git)
git init
# Set identitas (isi nama & email kamu)
git config user.name "Nama Kamu"
git config user.email "email@kamu.com"
4. Tambahkan semua file & commit
powershell

# Tambah semua file
git add .
# Commit pertama
git commit -m "Initial commit: Kopi Nusantara App"
5. Hubungkan ke GitHub & push
powershell

# Ganti URL dengan repo GitHub kamu
git remote add origin https://github.com/USERNAME/kopi-nusantara.git
# Push ke GitHub
git branch -M main
git push -u origin main
TIP

Jika diminta login, masukkan username dan Personal Access Token (bukan password). Buat token di: GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic) → Generate new token → centang repo → Generate

B. Download & Jalankan di Laptop Lain (dari GitHub)
1. Install software yang dibutuhkan
Software	Download
Python 3.10+	https://www.python.org/downloads/
Git	https://git-scm.com/downloads
IMPORTANT

Saat install Python, centang "Add Python to PATH"!

2. Clone project dari GitHub
powershell

# Pilih folder tujuan, misal di C:\Projects
cd C:\Projects
# Clone repo (ganti URL dengan repo kamu)
git clone https://github.com/USERNAME/kopi-nusantara.git
# Masuk ke folder project
cd kopi-nusantara
3. Install dependencies
powershell

# Install semua library yang dibutuhkan
pip install kivy[full] pillow
4. Jalankan app
powershell

python main.py
💾 CARA 2 — Kirim via Flash Disk / Copy Manual
1. Copy folder project
Copy seluruh folder reyna vscode ke flash disk
Paste ke laptop tujuan, misal di C:\Projects\reyna vscode
2. Install Python & dependencies di laptop baru
powershell

# Install Python dulu dari https://www.python.org/downloads/
# Lalu install library
pip install kivy[full] pillow
3. Jalankan
powershell

cd "C:\Projects\reyna vscode"
python main.py
🔄 Update Project (Setelah Ada Perubahan)
Push perubahan ke GitHub
powershell

cd "c:\laragon\www\reyna vscode"
# Tambah file yang berubah
git add .
# Commit dengan pesan perubahan
git commit -m "Update: deskripsi perubahan kamu"
# Push ke GitHub
git push origin main
Pull update di laptop lain
powershell

cd "C:\Projects\kopi-nusantara"
# Ambil update terbaru dari GitHub
git pull origin main
📋 Ringkasan Command Penting
Aksi	Command
Cek versi Python	python --version
Install library	pip install kivy[full] pillow
Jalankan app	python main.py
Clone dari GitHub	git clone <URL>
Ambil update terbaru	git pull origin main
Simpan perubahan	git add . ; git commit -m "pesan" ; git push origin main
❓ Troubleshooting
Error: kivy not found

powershell

pip install kivy[full]
Error: ModuleNotFoundError: No module named 'PIL'

powershell

pip install pillow
Error: font/gambar tidak muncul

Pastikan file emoji.ttf dan semua gambar (.png) ikut ter-copy/ter-clone
Error saat git push (authentication failed)

Gunakan Personal Access Token, bukan password biasa
Buat di: GitHub → Settings → Developer Settings → Personal Access Tokens