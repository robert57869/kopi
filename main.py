import os
import re
import random
import datetime

from kivy.utils import platform

# Posisi jendela tepat di TENGAH layar monitor laptop/PC (hanya jika di Desktop)
if platform not in ('android', 'ios'):
    os.environ['SDL_VIDEO_CENTERED'] = '1'

from kivy.core.window import Window

# Set ukuran tampilan mobile hanya di PC/Laptop, biarkan fullscreen otomatis di Android
if platform not in ('android', 'ios'):
    Window.size = (430, 700)

Window.set_title("Kopi Nusantara")

import database
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.text import LabelBase

# Pendaftaran font emoji agar emoji terbaca dan tidak menjadi kotak silang
base_dir = os.path.dirname(os.path.abspath(__file__))
font_emoji_path = os.path.join(base_dir, "emoji.ttf")
if not os.path.exists(font_emoji_path):
    if os.path.exists(r"C:\Windows\Fonts\seguiemj.ttf"):
        font_emoji_path = r"C:\Windows\Fonts\seguiemj.ttf"
    elif os.path.exists("/system/fonts/NotoColorEmoji.ttf"):
        font_emoji_path = "/system/fonts/NotoColorEmoji.ttf"

if os.path.exists(font_emoji_path):
    try:
        LabelBase.register(name="EmojiFont", fn_regular=font_emoji_path)
    except Exception:
        pass

# ==============================================================================
# STATE & DATA APLIKASI
# ==============================================================================

user_session = {
    "is_logged_in": False,
    "nama": "Pelanggan",
    "email": "",
    "no_hp": "",
    "poin": 0,
    "stamp": 0
}

keranjang_global = []
layanan_terpilih = "Dine In"
item_terpilih = {}
ukuran_terpilih = "M"
gula_terpilih = "Normal"
es_terpilih = "Normal"
jumlah_terpilih = 1
meja_terpilih = "-"
catatan_terpilih = "-"
metode_terpilih = "QRIS"
last_order_info = {}

def validasi_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))

def validasi_no_hp(hp):
    return hp.isdigit() and hp.startswith("08") and len(hp) in (10, 11, 12, 13)

def hitung_total_keranjang():
    subtotal = sum(item["subtotal"] for item in keranjang_global)
    diskon = (subtotal * 20 // 100) if layanan_terpilih == "Take Away" else 0
    biaya_layanan = 2000 if keranjang_global else 0
    total = max(0, subtotal - diskon + biaya_layanan)
    return subtotal, diskon, biaya_layanan, total


# ==============================================================================
# SCREENS IMPLEMENTATION
# ==============================================================================

class MyScreenManager(ScreenManager):
    pass


class SplashScreen(Screen):
    pass


class WelcomeScreen(Screen):
    def lanjut_sebagai_tamu(self):
        user_session["is_logged_in"] = False
        user_session["nama"] = "Tamu (Guest)"
        user_session["email"] = "guest@kopinusantara.com"
        user_session["no_hp"] = "-"
        user_session["poin"] = 0
        user_session["stamp"] = 0
        self.manager.transition.direction = 'left'
        self.manager.get_screen('beranda').setup_view()
        self.manager.current = 'beranda'


class LoginScreen(Screen):
    def toggle_password(self):
        pwd_input = self.ids.password_input
        pwd_input.password = not pwd_input.password
        self.ids.btn_eye_login.text = "🙈" if not pwd_input.password else "👁"
        self.ids.btn_eye_login.color = (1, 0.75, 0.3, 1) if not pwd_input.password else (0.83, 0.61, 0.36, 1)

    def do_login(self):
        email_or_hp = self.ids.email_input.text.strip()
        pwd = self.ids.password_input.text.strip()

        if not email_or_hp or not pwd:
            self.ids.error_label.text = "Email/No HP dan Password wajib diisi!"
            return

        # Cek autentikasi ke database SQLite
        user = database.cek_login(email_or_hp, pwd)

        if user:
            # user: (id, nama, email, no_hp)
            user_session["is_logged_in"] = True
            user_session["nama"] = user[1]
            user_session["email"] = user[2]
            user_session["no_hp"] = user[3]
            user_session["poin"] = 50
            user_session["stamp"] = 1

            self.ids.error_label.text = ""
            self.ids.password_input.text = ""
            self.manager.transition.direction = 'left'
            self.manager.get_screen('beranda').setup_view()
            self.manager.current = 'beranda'
        else:
            self.ids.error_label.text = "Email/No. HP atau Password salah!"


class RegisterScreen(Screen):
    def toggle_reg_password(self):
        pwd_input = self.ids.reg_password
        pwd_input.password = not pwd_input.password
        self.ids.btn_eye_reg1.text = "🙈" if not pwd_input.password else "👁"
        self.ids.btn_eye_reg1.color = (1, 0.75, 0.3, 1) if not pwd_input.password else (0.83, 0.61, 0.36, 1)

    def toggle_reg_confirm_password(self):
        pwd_input = self.ids.reg_password_confirm
        pwd_input.password = not pwd_input.password
        self.ids.btn_eye_reg2.text = "🙈" if not pwd_input.password else "👁"
        self.ids.btn_eye_reg2.color = (1, 0.75, 0.3, 1) if not pwd_input.password else (0.83, 0.61, 0.36, 1)

    def do_register(self):
        nama = self.ids.reg_nama.text.strip()
        email = self.ids.reg_email.text.strip()
        hp = self.ids.reg_hp.text.strip()
        pwd = self.ids.reg_password.text.strip()
        pwd_confirm = self.ids.reg_password_confirm.text.strip()

        if not nama:
            self.ids.reg_error.text = "Nama lengkap tidak boleh kosong!"
            return

        if not validasi_email(email):
            self.ids.reg_error.text = "Format email tidak valid (contoh: user@gmail.com)!"
            return

        if not validasi_no_hp(hp):
            self.ids.reg_error.text = "No. HP harus diawali 08 (10-13 angka)!"
            return

        if len(pwd) < 4:
            self.ids.reg_error.text = "Password minimal 4 karakter!"
            return

        if pwd != pwd_confirm:
            self.ids.reg_error.text = "Konfirmasi password tidak cocok!"
            return

        if database.cek_terdaftar(email, hp):
            self.ids.reg_error.text = "Email atau No. HP sudah terdaftar! Silakan login."
            return

        # Simpan ke database dengan password
        database.simpan_pengguna(nama, email, hp, pwd)

        # Set session sesuai data pengguna yang baru didaftarkan
        user_session["is_logged_in"] = True
        user_session["nama"] = nama
        user_session["email"] = email
        user_session["no_hp"] = hp
        user_session["poin"] = 50  # Bonus pendaftaran member baru
        user_session["stamp"] = 1

        self.ids.reg_error.text = ""
        self.ids.reg_password.text = ""
        self.ids.reg_password_confirm.text = ""
        self.manager.transition.direction = 'left'
        self.manager.get_screen('beranda').setup_view()
        self.manager.current = 'beranda'


class BerandaScreen(Screen):
    def on_pre_enter(self):
        self.setup_view()

    def setup_view(self):
        self.ids.welcome_msg.text = f"Hai, {user_session['nama']}"
        self.ids.points_info.text = f"Poin: {user_session['poin']} | Stamp: {user_session['stamp']}/10"
        total_items = sum(item["jumlah"] for item in keranjang_global)
        self.ids.cart_badge.text = f"Keranjang ({total_items})"

    def ke_layanan(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'layanan'

    def open_keranjang(self):
        self.manager.transition.direction = 'left'
        self.manager.get_screen('keranjang').update_view()
        self.manager.current = 'keranjang'

    def buka_menu_langsung(self, nama, harga, gambar):
        global layanan_terpilih
        layanan_terpilih = "Dine In"
        self.manager.get_screen('detail').setup_item(nama, harga, gambar)
        self.manager.transition.direction = 'left'
        self.manager.current = 'detail'


class LayananScreen(Screen):
    def pilih(self, jenis):
        global layanan_terpilih
        layanan_terpilih = jenis
        self.manager.transition.direction = 'left'
        self.manager.get_screen('menu').setup_menu(jenis)
        self.manager.current = 'menu'


class MenuScreen(Screen):
    def setup_menu(self, jenis="Dine In"):
        self.ids.menu_title.text = f"Menu Kopi ({jenis})"
        if jenis == "Take Away":
            self.ids.promo_badge.text = "[Promo] Diskon 20% untuk semua menu Take Away!"
        else:
            self.ids.promo_badge.text = "Nikmati racikan kopi barista fresh di tempat"

    def pilih_menu(self, nama, harga, path_gambar=""):
        self.manager.get_screen('detail').setup_item(nama, harga, path_gambar)
        self.manager.transition.direction = 'left'
        self.manager.current = 'detail'


class DetailProdukScreen(Screen):
    def setup_item(self, nama, harga, path_gambar=""):
        global item_terpilih, ukuran_terpilih, gula_terpilih, es_terpilih, jumlah_terpilih
        item_terpilih = {
            "nama": nama,
            "harga_dasar": harga,
            "gambar": path_gambar
        }
        ukuran_terpilih = "M"
        gula_terpilih = "Normal"
        es_terpilih = "Normal"
        jumlah_terpilih = 1

        self.ids.detail_title.text = nama
        if path_gambar:
            self.ids.detail_image.source = path_gambar

        self.reset_tombol_opsi()
        self.update_harga_total()

    def reset_tombol_opsi(self):
        self.ids.btn_ukuran_s.text = "S"
        self.ids.btn_ukuran_m.text = "[b]M ✓[/b]"
        self.ids.btn_ukuran_l.text = "L (+4k)"

        self.ids.btn_gula_normal.text = "[b]Normal ✓[/b]"
        self.ids.btn_gula_less.text = "Less 50%"
        self.ids.btn_gula_no.text = "0% Gula"

        self.ids.btn_es_normal.text = "[b]Normal ✓[/b]"
        self.ids.btn_es_less.text = "Less Ice"
        self.ids.btn_es_hot.text = "Hangat (Hot)"

        self.ids.qty_label.text = "1"

    def set_ukuran(self, uk):
        global ukuran_terpilih
        ukuran_terpilih = uk
        self.ids.btn_ukuran_s.text = "[b]S ✓[/b]" if uk == 'S' else "S"
        self.ids.btn_ukuran_m.text = "[b]M ✓[/b]" if uk == 'M' else "M"
        self.ids.btn_ukuran_l.text = "[b]L (+4k) ✓[/b]" if uk == 'L' else "L (+4k)"
        self.update_harga_total()

    def set_gula(self, gula):
        global gula_terpilih
        gula_terpilih = gula
        self.ids.btn_gula_normal.text = "[b]Normal ✓[/b]" if gula == 'Normal' else "Normal"
        self.ids.btn_gula_less.text = "[b]Less 50% ✓[/b]" if gula == 'Less' else "Less 50%"
        self.ids.btn_gula_no.text = "[b]0% Gula ✓[/b]" if gula == 'No' else "0% Gula"

    def set_es(self, es):
        global es_terpilih
        es_terpilih = es
        self.ids.btn_es_normal.text = "[b]Normal ✓[/b]" if es == 'Normal' else "Normal"
        self.ids.btn_es_less.text = "[b]Less Ice ✓[/b]" if es == 'Less' else "Less Ice"
        self.ids.btn_es_hot.text = "[b]Hangat (Hot) ✓[/b]" if es == 'Hot' else "Hangat (Hot)"

    def ubah_qty(self, delta):
        global jumlah_terpilih
        jumlah_terpilih = max(1, jumlah_terpilih + delta)
        self.ids.qty_label.text = str(jumlah_terpilih)
        self.update_harga_total()

    def update_harga_total(self):
        biaya_ukuran = 4000 if ukuran_terpilih == 'L' else 0
        harga_satuan = item_terpilih.get("harga_dasar", 20000) + biaya_ukuran
        total = harga_satuan * jumlah_terpilih
        self.ids.detail_price_btn.text = f"Tambah ke Keranjang - Rp {total:,}"

    def tambah_ke_keranjang(self):
        biaya_ukuran = 4000 if ukuran_terpilih == 'L' else 0
        harga_satuan = item_terpilih.get("harga_dasar", 20000) + biaya_ukuran
        subtotal = harga_satuan * jumlah_terpilih

        gula_label = "Normal Sugar" if gula_terpilih == "Normal" else ("Less 50% Sugar" if gula_terpilih == "Less" else "Tanpa Gula")
        es_label = "Normal Ice" if es_terpilih == "Normal" else ("Less Ice" if es_terpilih == "Less" else "Hot / Hangat")

        keranjang_global.append({
            "nama": item_terpilih["nama"],
            "ukuran": ukuran_terpilih,
            "gula": gula_label,
            "es": es_label,
            "harga_satuan": harga_satuan,
            "jumlah": jumlah_terpilih,
            "subtotal": subtotal,
            "gambar": item_terpilih.get("gambar", "")
        })

        self.manager.transition.direction = 'left'
        self.manager.get_screen('keranjang').update_view()
        self.manager.current = 'keranjang'


class KeranjangScreen(Screen):
    def update_view(self):
        if not keranjang_global:
            self.ids.isi_keranjang.text = "Keranjang pesanan masih kosong.\nYuk pilih menu kopi favoritmu sekarang!"
            self.ids.ringkasan_biaya.text = ""
            self.ids.btn_checkout.disabled = True
            return

        self.ids.btn_checkout.disabled = False
        teks = f"[b]Layanan:[/b] {layanan_terpilih}\n\n"

        for idx, item in enumerate(keranjang_global, 1):
            teks += (
                f"[b]{idx}. {item['nama']}[/b] ({item['ukuran']}) x{item['jumlah']}\n"
                f"   [size=12sp]- {item['gula']} | {item['es']}[/size]\n"
                f"   [color=d49b5b]Subtotal: Rp {item['subtotal']:,}[/color]\n\n"
            )

        self.ids.isi_keranjang.text = teks

        subtotal, diskon, biaya_layanan, total = hitung_total_keranjang()
        ringkasan = (
            f"Subtotal: Rp {subtotal:,}\n"
            f"Diskon Promo ({'Take Away 20%' if diskon > 0 else '0%'}): -Rp {diskon:,}\n"
            f"Biaya Kemasan & Layanan: Rp {biaya_layanan:,}\n"
            f"[b][size=16sp]Total Bayar: Rp {total:,}[/size][/b]"
        )
        self.ids.ringkasan_biaya.text = ringkasan

    def kosongkan(self):
        keranjang_global.clear()
        self.update_view()

    def hapus_item_terakhir(self):
        if keranjang_global:
            keranjang_global.pop()
            self.update_view()

    def lanjut_konfirmasi(self):
        if keranjang_global:
            self.manager.transition.direction = 'left'
            self.manager.get_screen('konfirmasi').setup_view()
            self.manager.current = 'konfirmasi'


class KonfirmasiScreen(Screen):
    def setup_view(self):
        subtotal, diskon, biaya_layanan, total = hitung_total_keranjang()
        self.ids.konfirmasi_layanan.text = f"Tipe Layanan: [b]{layanan_terpilih}[/b]"
        if layanan_terpilih == "Dine In":
            self.ids.input_meja.hint_text = "Nomor Meja (Wajib untuk Dine In, contoh: Meja 05)"
        else:
            self.ids.input_meja.hint_text = "Nama / Nomor Antrian Bawa Pulang"

        self.ids.ringkasan_text.text = (
            f"Total Pesanan: {len(keranjang_global)} Jenis Item\n"
            f"Diskon Terpasang: Rp {diskon:,}\n"
            f"[b][color=d49b5b]Total Tagihan: Rp {total:,}[/color][/b]"
        )

    def lanjut_pembayaran(self):
        global meja_terpilih, catatan_terpilih
        meja_terpilih = self.ids.input_meja.text.strip() or ("Meja 01" if layanan_terpilih == "Dine In" else "Take Away")
        catatan_terpilih = self.ids.input_catatan.text.strip() or "Tidak ada catatan khusus"

        self.manager.transition.direction = 'left'
        self.manager.get_screen('pembayaran').setup_view()
        self.manager.current = 'pembayaran'


class PembayaranScreen(Screen):
    def setup_view(self):
        global metode_terpilih
        metode_terpilih = "QRIS"
        subtotal, diskon, biaya_layanan, total = hitung_total_keranjang()
        self.ids.total_bayar_label.text = f"Total Pembayaran:\n[size=22sp][b]Rp {total:,}[/b][/size]"
        self.pilih_metode("QRIS")

    def pilih_metode(self, metode):
        global metode_terpilih
        metode_terpilih = metode
        self.ids.btn_qris.text = "[b]QRIS (BCA, GoPay, OVO) ✓[/b]" if metode == "QRIS" else "QRIS (BCA, GoPay, OVO)"
        self.ids.btn_debit.text = "[b]Kartu Debit / EDC ✓[/b]" if metode == "Debit" else "Kartu Debit / EDC"
        self.ids.btn_tunai.text = "[b]Tunai di Kasir ✓[/b]" if metode == "Tunai" else "Tunai di Kasir"

        if metode == "QRIS":
            self.ids.info_metode.text = "Scan QRIS di kasir atau simpan kode QR ini.\nTransaksi akan otomatis terverifikasi."
        elif metode == "Debit":
            self.ids.info_metode.text = "Siapkan kartu debit Anda untuk diproses di mesin EDC kasir."
        else:
            self.ids.info_metode.text = "Silakan bayar dengan uang tunai saat pesanan diserahkan di kasir."

    def bayar(self):
        global last_order_info
        kode_unik = f"KP-{random.randint(1000, 9999)}"
        subtotal, diskon, biaya_layanan, total = hitung_total_keranjang()
        waktu_sekarang = datetime.datetime.now().strftime("%d %b %Y, %H:%M")

        for item in keranjang_global:
            database.simpan_pesanan(
                kode_pesanan=kode_unik,
                nama_pelanggan=user_session["nama"],
                layanan=layanan_terpilih,
                nama_menu=item["nama"],
                ukuran=item["ukuran"],
                gula=item["gula"],
                es=item["es"],
                jumlah=item["jumlah"],
                subtotal=item["subtotal"],
                nomor_meja=meja_terpilih,
                catatan=catatan_terpilih,
                metode_bayar=metode_terpilih
            )

        # Update poin loyalitas
        user_session["poin"] += (total // 1000)
        user_session["stamp"] = min(10, user_session["stamp"] + 1)

        last_order_info = {
            "kode": kode_unik,
            "waktu": waktu_sekarang,
            "layanan": layanan_terpilih,
            "meja": meja_terpilih,
            "catatan": catatan_terpilih,
            "metode": metode_terpilih,
            "total": total,
            "items": list(keranjang_global)
        }

        keranjang_global.clear()
        self.manager.transition.direction = 'left'
        self.manager.get_screen('berhasil').setup_view()
        self.manager.current = 'berhasil'


class PesananBerhasilScreen(Screen):
    def setup_view(self):
        info = last_order_info
        self.ids.order_code_label.text = f"KODE PESANAN: {info.get('kode', '#KP-1001')}"

        ringkasan = (
            f"Waktu: {info.get('waktu', '-')}\n"
            f"Pelanggan: {user_session['nama']}\n"
            f"Layanan: {info.get('layanan', '-')} | {info.get('meja', '-')}\n"
            f"Pembayaran: {info.get('metode', '-')}\n"
            f"Catatan: {info.get('catatan', '-')}\n"
            f"----------------------------------------\n"
            f"[b]Total Dibayar: Rp {info.get('total', 0):,}[/b]"
        )
        self.ids.order_detail_label.text = ringkasan

    def ke_beranda(self):
        self.manager.transition.direction = 'right'
        self.manager.get_screen('beranda').setup_view()
        self.manager.current = 'beranda'

    def ke_riwayat(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'riwayat'


class RiwayatScreen(Screen):
    def on_pre_enter(self):
        self.setup_view()

    def setup_view(self):
        data = database.ambil_riwayat(user_session["nama"])

        if not data:
            self.ids.riwayat_text.text = "Belum ada riwayat transaksi pesanan.\nYuk pesan kopi sekarang dan kumpulkan poinmu!"
            return

        teks = ""
        for item in data:
            # item: kode_pesanan, nama_menu, ukuran, jumlah, subtotal, tanggal, layanan, nomor_meja, metode_bayar
            kode = item[0] or "KP-ORDER"
            nama = item[1]
            ukuran = item[2]
            jumlah = item[3]
            subtotal = item[4]
            tgl = item[5] or "-"
            layanan = item[6] or "-"
            meja = item[7] or "-"
            metode = item[8] or "QRIS"

            teks += (
                f"[b]#{kode} - {layanan}[/b] ({meja})\n"
                f"{tgl} | [color=88d49e]{metode}[/color]\n"
                f"- {nama} ({ukuran}) x{jumlah} = [b]Rp {subtotal:,}[/b]\n"
                f"----------------------------------------\n\n"
            )

        self.ids.riwayat_text.text = teks


class NotifikasiScreen(Screen):
    pass


class AkunScreen(Screen):
    def on_pre_enter(self):
        self.ids.akun_info.text = (
            f"[b]{user_session['nama']}[/b]\n"
            f"[color=c2b69d]{user_session['email']} | {user_session['no_hp']}[/color]"
        )
        self.ids.loyalty_info.text = (
            f"[b]Gold Member Rewards[/b]\n"
            f"Poin Terkumpul: [b]{user_session['poin']} Poin[/b]\n"
            f"Stamp Card: [b]{user_session['stamp']}/10 Stamp[/b]\n"
            f"(Kumpulkan 3 stamp lagi untuk 1 Cup Kopi Gratis!)"
        )

    def do_logout(self):
        user_session["is_logged_in"] = False
        user_session["nama"] = "Pelanggan"
        user_session["email"] = ""
        user_session["no_hp"] = ""
        user_session["poin"] = 0
        user_session["stamp"] = 0
        self.manager.transition.direction = 'right'
        self.manager.current = 'welcome'


# =========================================================
# MAIN APP ENTRY
# =========================================================

class KopiNusantaraApp(App):
    def build(self):
        database.buat_database()
        database.isi_menu_awal()

        self.logo_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "logo.png"
        )

        Builder.load_file('kopi.kv')

        sm = MyScreenManager(transition=SlideTransition())
        return sm


if __name__ == '__main__':
    KopiNusantaraApp().run()