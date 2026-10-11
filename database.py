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
            no_hp TEXT,
            password TEXT DEFAULT '123456'
        )
    """)

    # Migrasi kolom password jika tabel lama belum memiliki password
    try:
        cursor.execute("ALTER TABLE pengguna ADD COLUMN password TEXT DEFAULT '123456'")
    except Exception:
        pass

    # Tabel menu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            harga INTEGER NOT NULL,
            gambar TEXT,
            kategori TEXT DEFAULT 'Kopi',
            deskripsi TEXT DEFAULT ''
        )
    """)

    # Tabel pesanan
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pesanan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kode_pesanan TEXT,
            nama_pelanggan TEXT,
            layanan TEXT,
            nama_menu TEXT,
            ukuran TEXT,
            gula TEXT DEFAULT 'Normal',
            es TEXT DEFAULT 'Normal',
            jumlah INTEGER,
            subtotal INTEGER,
            nomor_meja TEXT DEFAULT '-',
            catatan TEXT DEFAULT '-',
            metode_bayar TEXT DEFAULT 'QRIS',
            tanggal DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Migrasi kolom pesanan
    kolom_pesanan = [
        ("kode_pesanan", "TEXT DEFAULT 'KP-1001'"),
        ("gula", "TEXT DEFAULT 'Normal Sugar'"),
        ("es", "TEXT DEFAULT 'Normal Ice'"),
        ("nomor_meja", "TEXT DEFAULT '-'"),
        ("catatan", "TEXT DEFAULT '-'"),
        ("metode_bayar", "TEXT DEFAULT 'QRIS'")
    ]
    for nama_kolom, tipe_kolom in kolom_pesanan:
        try:
            cursor.execute(f"ALTER TABLE pesanan ADD COLUMN {nama_kolom} {tipe_kolom}")
        except Exception:
            pass

    # Migrasi kolom menu
    kolom_menu = [
        ("kategori", "TEXT DEFAULT 'Kopi'"),
        ("deskripsi", "TEXT DEFAULT ''")
    ]
    for nama_kolom, tipe_kolom in kolom_menu:
        try:
            cursor.execute(f"ALTER TABLE menu ADD COLUMN {nama_kolom} {tipe_kolom}")
        except Exception:
            pass

    # Akun demo awal jika belum ada data pengguna sama sekali
    cursor.execute("SELECT COUNT(*) FROM pengguna")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO pengguna (nama, email, no_hp, password)
            VALUES (?, ?, ?, ?)
        """, ("Reyna A. Putri", "reyna@gmail.com", "081234567890", "123456"))

    conn.commit()
    conn.close()


def isi_menu_awal():
    conn = koneksi()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM menu")
    jumlah = cursor.fetchone()[0]

    if jumlah == 0:
        menu = [
            ("Cappuccino", 25000, "cappuccino.png", "Kopi", "Espresso kaya rasa dengan busa susu lembut khas Italia."),
            ("Americano", 20000, "americano.png", "Kopi", "Espresso murni dipadukan dengan air mineral segar, aroma pekat."),
            ("Kopi Susu Gula Aren", 23000, "kopiaren.png", "Signature", "Perpaduan kopi nusantara, susu creamy, dan manis legit aren asli.")
        ]

        cursor.executemany("""
            INSERT INTO menu (nama, harga, gambar, kategori, deskripsi)
            VALUES (?, ?, ?, ?, ?)
        """, menu)
        conn.commit()
    conn.close()


def ambil_semua_menu():
    conn = koneksi()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nama, harga, gambar, kategori, deskripsi FROM menu ORDER BY id ASC")
    data = cursor.fetchall()
    conn.close()
    return data


def simpan_pengguna(nama, email, no_hp, password):
    conn = koneksi()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pengguna (nama, email, no_hp, password)
        VALUES (?, ?, ?, ?)
    """, (nama.strip(), email.strip().lower(), no_hp.strip(), password.strip()))

    conn.commit()
    conn.close()


def cek_login(identifier, password):
    conn = koneksi()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nama, email, no_hp
        FROM pengguna
        WHERE (LOWER(email) = LOWER(?) OR no_hp = ?) AND password = ?
    """, (identifier.strip(), identifier.strip(), password.strip()))

    data = cursor.fetchone()
    conn.close()
    return data


def cek_terdaftar(email, no_hp):
    conn = koneksi()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM pengguna
        WHERE LOWER(email) = LOWER(?) OR no_hp = ?
    """, (email.strip(), no_hp.strip()))

    ada = cursor.fetchone()
    conn.close()
    return ada is not None


def simpan_pesanan(kode_pesanan, nama_pelanggan, layanan, nama_menu,
                   ukuran, gula, es, jumlah, subtotal, nomor_meja="-", catatan="-", metode_bayar="QRIS"):

    conn = koneksi()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pesanan
        (kode_pesanan, nama_pelanggan, layanan, nama_menu, ukuran, gula, es, jumlah, subtotal, nomor_meja, catatan, metode_bayar)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        kode_pesanan,
        nama_pelanggan,
        layanan,
        nama_menu,
        ukuran,
        gula,
        es,
        jumlah,
        subtotal,
        nomor_meja,
        catatan,
        metode_bayar
    ))

    conn.commit()
    conn.close()


def ambil_riwayat(nama_pelanggan):
    conn = koneksi()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT kode_pesanan, nama_menu, ukuran, jumlah, subtotal, tanggal, layanan, nomor_meja, metode_bayar
        FROM pesanan
        WHERE nama_pelanggan = ?
        ORDER BY id DESC
    """, (nama_pelanggan,))

    data = cursor.fetchall()
    conn.close()
    return data