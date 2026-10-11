import sqlite3

DB_NAME = "kopi_nusantara.db"


def koneksi():
    return sqlite3.connect(DB_NAME)


def buat_database():
    conn = koneksi()
    cursor = conn.cursor()

    # Tabel pengguna
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pengguna (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            no_hp TEXT
        )
    """)

    # Tabel menu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            harga INTEGER NOT NULL,
            gambar TEXT
        )
    """)

    # Tabel pesanan
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pesanan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_pelanggan TEXT,
            layanan TEXT,
            nama_menu TEXT,
            ukuran TEXT,
            jumlah INTEGER,
            subtotal INTEGER,
            tanggal DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def isi_menu_awal():
    conn = koneksi()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM menu")
    jumlah = cursor.fetchone()[0]

    if jumlah == 0:
        menu = [
            ("Cappuccino", 25000, "foto/cappuccino.png"),
            ("Caffe Latte", 25000, "foto/latte.png"),
            ("Americano", 20000, "foto/americano.png"),
            ("Kopi Susu Gula Aren", 23000, "foto/kopi_susu.png")
        ]

        cursor.executemany("""
            INSERT INTO menu (nama, harga, gambar)
            VALUES (?, ?, ?)
        """, menu)

    conn.commit()
    conn.close()


def simpan_pengguna(nama, email, no_hp):
    conn = koneksi()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO pengguna (nama, email, no_hp)
        VALUES (?, ?, ?)
    """, (nama, email, no_hp))

    conn.commit()
    conn.close()


def simpan_pesanan(nama_pelanggan, layanan, nama_menu,
                   ukuran, jumlah, subtotal):

    conn = koneksi()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pesanan
        (nama_pelanggan, layanan, nama_menu, ukuran, jumlah, subtotal)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        nama_pelanggan,
        layanan,
        nama_menu,
        ukuran,
        jumlah,
        subtotal
    ))

    conn.commit()
    conn.close()


def ambil_riwayat(nama_pelanggan):
    conn = koneksi()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nama_menu, ukuran, jumlah, subtotal, tanggal
        FROM pesanan
        WHERE nama_pelanggan = ?
        ORDER BY id DESC
    """, (nama_pelanggan,))

    data = cursor.fetchall()

    conn.close()

    return data