import os
import re 
import database
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

# ==============================================================================
# LOGIKA LOGIS & STATE APLIKASI
# ==============================================================================

user_session = {
    "is_logged_in": False,
    "nama": "Reyna A. Putri",
    "email": "reyna@gmail.com",
    "no_hp": "081234567890"
}

keranjang_global = []
layanan_terpilih = "Dine In"
item_terpilih = {}
ukuran_terpilih = "M"

def validasi_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
    return bool(re.match(pattern, email.strip()))
def validasi_no_hp(hp):
    return hp.isdigit() and hp.startswith("08") and len(hp) in (12, 13)

# ==============================================================================
# SCREENS IMPLEMENTATION
# ==============================================================================

class MyScreenManager(ScreenManager):
    pass

class SplashScreen(Screen):
    pass

class WelcomeScreen(Screen):
    pass

class LoginScreen(Screen):
    def do_login(self):
        email_or_hp = self.ids.email_input.text.strip()
        
        if email_or_hp.isdigit():
            if len(email_or_hp) >= 10:
                user_session["is_logged_in"] = True
                self.ids.error_label.text = ""
                self.manager.get_screen('beranda').on_pre_enter()
                self.manager.current = 'beranda'
            else:
                self.ids.error_label.text = "Nomor HP tidak valid (minimal 10 digit)."
        else:
            if validasi_email(email_or_hp):
                user_session["email"] = email_or_hp
                user_session["is_logged_in"] = True
                self.ids.error_label.text = ""
                self.manager.get_screen('beranda').on_pre_enter()
                self.manager.current = 'beranda'
            else:
                self.ids.error_label.text = "Format email salah!"

class RegisterScreen(Screen):
    def do_register(self):
        nama = self.ids.reg_nama.text.strip()
        email = self.ids.reg_email.text.strip()
        hp = self.ids.reg_hp.text.strip()
        
        if not nama:
            self.ids.reg_error.text = "Nama tidak boleh kosong."
            return
        
        if not validasi_email(email):
            self.ids.reg_error.text = "Format email salah!"
            return

        if not validasi_no_hp(hp):
            self.ids.reg_error.text = "No. HP harus diawali 08 dan terdiri dari 12-13 angka."
            return

        if validasi_email(email):
            user_session["nama"] = nama
            user_session["email"] = email
            user_session["no_hp"] = hp
            user_session["is_logged_in"] = True
            database.simpan_pengguna(nama, email, hp)
            self.ids.reg_error.text = ""
            self.manager.get_screen('beranda').on_pre_enter()
            self.manager.current = 'beranda'
        else:
            self.ids.reg_error.text = "Format email salah!"

class BerandaScreen(Screen):
    def on_pre_enter(self):
        self.ids.welcome_msg.text = f"Hai, {user_session['nama']}!"

    def open_keranjang(self):
        self.manager.get_screen('keranjang').update_view()
        self.manager.current = 'keranjang'

class LayananScreen(Screen):
    def pilih(self, jenis):
        global layanan_terpilih
        layanan_terpilih = jenis
        self.manager.get_screen('menu').ids.menu_title.text = f"Daftar Menu ({jenis})"
        self.manager.current = 'menu'

class MenuScreen(Screen):
    def pilih_menu(self, nama, harga, path_gambar=""):
        global item_terpilih
        item_terpilih = {"nama": nama, "harga": harga}
        self.manager.get_screen('detail').ids.detail_title.text = f"{nama}\nHarga: Rp {harga:,}"
        if path_gambar:
            self.manager.get_screen('detail').ids.detail_image.source = path_gambar
        self.manager.current = 'detail'

class DetailProdukScreen(Screen):
    def set_ukuran(self, uk):
        global ukuran_terpilih
        ukuran_terpilih = uk
        self.ids.info_pilihan.text = f"Ukuran terpilih: {uk}"

    def tambah_ke_keranjang(self):
        biaya = 4000 if ukuran_terpilih == 'L' else 0
        harga_total = item_terpilih['harga'] + biaya
        keranjang_global.append({
            "nama": item_terpilih['nama'],
            "ukuran": ukuran_terpilih,
            "harga": harga_total,
            "jumlah": 1,
            "subtotal": harga_total
        })
        self.manager.get_screen('keranjang').update_view()
        self.manager.current = 'keranjang'

class KeranjangScreen(Screen):
    def update_view(self):
        if not keranjang_global:
            self.ids.isi_keranjang.text = "Keranjang Anda kosong."
            return
        
        teks = ""
        subtotal = 0
        for item in keranjang_global:
            nama = item["nama"]
            ukuran = item["ukuran"]
            jumlah = item["jumlah"]
            harga = item["harga"]
            
            total_item = harga * jumlah
            subtotal += total_item

            teks += (
                f"{nama} ({ukuran}) x{jumlah} = "
                f"Rp {total_item:,}\n"
            )

        # Diskon 20% khusus Take Away
        diskon = 0

        if layanan_terpilih == "Take Away":
            diskon = subtotal * 20 // 100

        total_bayar = subtotal - diskon

        teks += f"\nLayanan: {layanan_terpilih}"
        teks += f"\nSubtotal: Rp {subtotal:,}"

        if diskon > 0:
            teks += f"\nDiskon 20%: -Rp {diskon:,}"

        teks += f"\nTotal Bayar: Rp {total_bayar:,}"

        self.ids.isi_keranjang.text = teks

    def kosongkan(self):
        keranjang_global.clear()
        self.update_view()

    def lanjut_konfirmasi(self):
        if keranjang_global:
            self.manager.get_screen('konfirmasi').setup_view()
            self.manager.current = 'konfirmasi'

class KonfirmasiScreen(Screen):
    def setup_view(self):
        subtotal = sum(i['subtotal'] for i in keranjang_global)
        total = subtotal + 2000
        self.ids.ringkasan_text.text = f"Layanan: {layanan_terpilih}\nTotal Bayar: Rp {total:,}"

    def lanjut_pembayaran(self):
        self.manager.current = 'pembayaran'

class PembayaranScreen(Screen):
    def bayar(self):
        for item in keranjang_global:
            database.simpan_pesanan(
                user_session["nama"],
                layanan_terpilih,
                item["nama"],
                item["ukuran"],
                item["jumlah"],
                item["subtotal"]
            )
        keranjang_global.clear()
        self.manager.current = 'berhasil'

class PesananBerhasilScreen(Screen):
    pass

class RiwayatScreen(Screen):
    pass

class NotifikasiScreen(Screen):
    pass

class RiwayatScreen(Screen):

    def on_pre_enter(self):
        data = database.ambil_riwayat(
            user_session["nama"]
        )

        if not data:
            self.ids.riwayat_text.text = "Belum ada riwayat pesanan."
            return

        teks = ""

        for item in data:
            nama = item[0]
            ukuran = item[1]
            jumlah = item[2]
            subtotal = item[3]

            teks += (
                f"{nama} ({ukuran}) x{jumlah}\n"
                f"Rp {subtotal:,}\n\n"
            )

        self.ids.riwayat_text.text = teks


class AkunScreen(Screen):

    def on_pre_enter(self):
        self.ids.akun_info.text = (
            f"Profil Saya\n"
            f"Nama: {user_session['nama']}\n"
            f"Email: {user_session['email']}"
        )

# ==============================================================================
# MAIN APP ENTRY
# ==============================================================================

class KopiNusantaraApp(App):

    def build(self):
        database.buat_database()
        database.isi_menu_awal()

        self.logo_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "logo.png"
        )

        Builder.load_file('kopi.kv')

        return MyScreenManager()

if __name__ == '__main__':
    KopiNusantaraApp().run()