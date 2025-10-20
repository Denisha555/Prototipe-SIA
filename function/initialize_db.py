import sqlite3
import datetime
import random


def initialize_db(self):
        conn = sqlite3.connect('data_keuangan.db')
        c = conn.cursor()
                            
        # c.execute('''CREATE TABLE IF NOT EXISTS pajak (
        #             id INTEGER PRIMARY KEY AUTOINCREMENT,
        #             tanggal TEXT,
        #             jenis_pajak TEXT,
        #             jumlah INTEGER)''')
                    
        # c.execute('''CREATE TABLE IF NOT EXISTS penggajian (
        #             id INTEGER PRIMARY KEY AUTOINCREMENT,
        #             tanggal TEXT,
        #             nama_karyawan TEXT,
        #             gaji_bersih INTEGER)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    password TEXT,
                    role TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS jasa (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  nama_jasa TEXT,
                  detail_jasa TEXT,
                  gambar BLOB,
                  harga INTEGER)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS transaksi_penjualan (
                  transaksi_penjualan_id TEXT PRIMARY KEY,
                  tanggal DATE,
                  total INTEGER,
                  kategori TEXT,
                  keterangan TEXT)
                  ''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS detail_transaksi_penjualan (
                  detail_penjualan_id TEXT PRIMARY KEY,
                  transaksi_penjualan_id TEXT,
                  jasa_id TEXT,
                  jumlah INTEGER,
                  FOREIGN KEY(jasa_id) REFERENCES jasa (id),
                  FOREIGN KEY(transaksi_penjualan_id) REFERENCES TRANSAKSI_PENJUALAN (transaksi_penjualan_id))''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS transaksi_kas_keluar (
                  transaksi_kas_keluar_id TEXT PRIMARY KEY,
                  tanggal DATE,
                  kategori TEXT,
                  nominal INTEGER,
                  keterangan TEXT)
                  ''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS akun (
                    kode_akun TEXT PRIMARY KEY,
                    nama_akun TEXT NOT NULL,
                    kategori TEXT NOT NULL,
                    saldo_normal TEXT NOT NULL
                )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS jurnal_umum_detail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaksi_ref_id TEXT, -- ID dari Penjualan, Pembelian, Gaji, dll.
                    tanggal DATE NOT NULL,
                    kode_akun TEXT NOT NULL,
                    keterangan TEXT,
                    debit REAL DEFAULT 0,
                    kredit REAL DEFAULT 0,
                    jenis_jurnal TEXT DEFAULT "UMUM",
                    FOREIGN KEY (kode_akun) REFERENCES akun(kode_akun)
                )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS transaksi_penyesuaian (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tanggal DATE NOT NULL,
                    kode_akun TEXT NOT NULL,
                    keterangan TEXT,
                    debit REAL DEFAULT 0,
                    kredit REAL DEFAULT 0,
                    FOREIGN KEY (kode_akun) REFERENCES akun(kode_akun))
                ''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS rekap_modal(
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  tanggal DATE,
                  modal_awal INTEGER,
                  modal_akhir INTEGER)
                ''')
        
        initial_coa = [
            ('111', 'Kas', 'Aset', 'Debit'),
            ('112', 'Piutang Usaha', 'Aset', 'Debit'),
            ('113', 'Perlengkapan', 'Aset', 'Debit'), 
            ('121', 'Peralatan', 'Aset', 'Debit'),
            ('122', 'Akumulasi Penyusutan Peralatan', 'Aset', 'Debit'),
            ('211', 'Utang Usaha', 'Liabilitas', 'Kredit'),
            ('212', 'Utang Gaji', 'Liabilitas', 'Kredit'),
            ('311', 'Modal Pemilik', 'Ekuitas', 'Kredit'),
            ('312', 'Prive', 'Ekuitas', 'Debit'),
            ('313', 'Ikhtisar Laba/Rugi', 'Nominal', 'Debit'),
            ('401', 'Pendapatan Jasa', 'Pendapatan', 'Kredit'), 
            ('511', 'Beban Gaji', 'Beban', 'Debit'), 
            ('512', 'Beban Pajak', 'Beban', 'Debit'), 
            ('513', 'Beban Perlengkapan', 'Beban', 'Debit'),
            ('514', 'Beban Penyusutan Peralatan', 'Beban', 'Debit'),
            ('520', 'Beban Lain-lain', 'Beban', 'Debit')
        ]

        c.execute("SELECT COUNT(*) FROM akun")
        if c.fetchone()[0] == 0:
            c.executemany("INSERT INTO akun (kode_akun, nama_akun, kategori, saldo_normal) VALUES (?, ?, ?, ?)", initial_coa)

        conn.commit()
        conn.close()

        # # Koneksi ke database
        # conn = sqlite3.connect("data_keuangan.db")
        # c = conn.cursor()

        # def generate_dummy_data():
        #     # Hapus dulu data lama biar bersih
        #     c.execute("DELETE FROM transaksi_penjualan")
        #     c.execute("DELETE FROM transaksi_kas_keluar")
        #     c.execute("DELETE FROM jurnal_umum_detail")
        #     c.execute("DELETE FROM transaksi_penyesuaian")
        #     c.execute("DELETE FROM rekap_modal")
        #     conn.commit()

        #     start_date = datetime.date(2025, 8, 1)
        #     end_date = datetime.date(2025, 10, 31)
        #     delta = datetime.timedelta(days=1)

        #     # =========  PENJUALAN =========
        #     while start_date <= end_date:
        #         if start_date.weekday() < 6:  # 0-5 Senin-Sabtu, Minggu libur
        #             total = random.randint(500000, 2000000)
        #             datestr = start_date.strftime("%Y%m%d")
        #             transaksi_id = f"PJ{datestr}001"

        #             c.execute("""
        #                 INSERT INTO transaksi_penjualan (transaksi_penjualan_id, tanggal, total, kategori, keterangan)
        #                 VALUES (?, ?, ?, ?, ?)
        #             """, (transaksi_id, start_date, total, "Pendapatan Jasa", "Penjualan jasa harian"))

        #             # Masuk jurnal umum
        #             c.execute("""
        #                 INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit)
        #                 VALUES (?, ?, ?, ?, ?, ?)
        #             """, (transaksi_id, start_date, "111", "Kas dari penjualan", total, 0))
        #             c.execute("""
        #                 INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit)
        #                 VALUES (?, ?, ?, ?, ?, ?)
        #             """, (transaksi_id, start_date, "401", "Pendapatan jasa", 0, total))
        #         start_date += delta

        #     # =========  KAS KELUAR =========
        #     start_date = datetime.date(2025, 8, 1)
        #     while start_date <= end_date:
        #         if random.random() < 0.3:  # sekitar 30% hari ada pengeluaran
        #             jenis = random.choice(["Gaji", "Listrik", "Perlengkapan"])
        #             nominal = random.randint(300000, 1500000)
        #             datestr = start_date.strftime("%Y%m%d")
        #             transaksi_id = f"PB{datestr}001"

        #             c.execute("""
        #                 INSERT INTO transaksi_kas_keluar (transaksi_kas_keluar_id, tanggal, kategori, nominal, keterangan)
        #                 VALUES (?, ?, ?, ?, ?)
        #             """, (transaksi_id, start_date, jenis, nominal, f"Pembayaran {jenis.lower()}"))

        #             # Jurnal umum
        #             if jenis == "Perlengkapan":
        #                 akun_debit = "113"  # Perlengkapan (Aset)
        #             elif jenis == "Gaji":
        #                 akun_debit = "511"
        #             else:
        #                 akun_debit = "520"

        #             c.execute("""
        #                 INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit)
        #                 VALUES (?, ?, ?, ?, ?, ?)
        #             """, (transaksi_id, start_date, akun_debit, f"Pengeluaran {jenis}", nominal, 0))
        #             c.execute("""
        #                 INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit)
        #                 VALUES (?, ?, ?, ?, ?, ?)
        #             """, (transaksi_id, start_date, "111", f"Kas keluar untuk {jenis}", 0, nominal))
        #         start_date += delta

        #     # ========= PENYESUAIAN AKHIR BULAN =========
        #     for bulan in [8, 9, 10]:
        #         tanggal_akhir = datetime.date(2025, bulan, 28)

        #         # --- Penyusutan peralatan ---
        #         depresiasi = random.randint(400000, 700000)
        #         c.execute("""
        #             INSERT INTO transaksi_penyesuaian (tanggal, kode_akun, keterangan, debit, kredit)
        #             VALUES (?, ?, ?, ?, ?)
        #         """, (tanggal_akhir, "514", "Beban penyusutan peralatan", depresiasi, 0))
        #         c.execute("""
        #             INSERT INTO transaksi_penyesuaian (tanggal, kode_akun, keterangan, debit, kredit)
        #             VALUES (?, ?, ?, ?, ?)
        #         """, (tanggal_akhir, "122", "Akumulasi penyusutan peralatan", 0, depresiasi))

        #         # Jurnal penyesuaian (jenis_jurnal = PENYESUAIAN)
        #         c.execute("""
        #             INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        #             VALUES (?, ?, ?, ?, ?, ?, ?)
        #         """, (f"ADJ{bulan}A", tanggal_akhir, "514", "Beban penyusutan peralatan", depresiasi, 0, "PENYESUAIAN"))
        #         c.execute("""
        #             INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        #             VALUES (?, ?, ?, ?, ?, ?, ?)
        #         """, (f"ADJ{bulan}A", tanggal_akhir, "122", "Akumulasi penyusutan peralatan", 0, depresiasi, "PENYESUAIAN"))

        #         # --- Penyesuaian perlengkapan (sebagian sudah terpakai) ---
        #         beban_perlengkapan = random.randint(500000, 1200000)
        #         c.execute("""
        #             INSERT INTO transaksi_penyesuaian (tanggal, kode_akun, keterangan, debit, kredit)
        #             VALUES (?, ?, ?, ?, ?)
        #         """, (tanggal_akhir, "513", "Beban perlengkapan", beban_perlengkapan, 0))
        #         c.execute("""
        #             INSERT INTO transaksi_penyesuaian (tanggal, kode_akun, keterangan, debit, kredit)
        #             VALUES (?, ?, ?, ?, ?)
        #         """, (tanggal_akhir, "113", "Pengurangan perlengkapan", 0, beban_perlengkapan))

        #         c.execute("""
        #             INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        #             VALUES (?, ?, ?, ?, ?, ?, ?)
        #         """, (f"ADJ{bulan}B", tanggal_akhir, "513", "Beban perlengkapan", beban_perlengkapan, 0, "PENYESUAIAN"))
        #         c.execute("""
        #             INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
        #             VALUES (?, ?, ?, ?, ?, ?, ?)
        #         """, (f"ADJ{bulan}B", tanggal_akhir, "113", "Pengurangan perlengkapan", 0, beban_perlengkapan, "PENYESUAIAN"))

        #     conn.commit()
        #     print("✅ Dummy data berhasil dibuat dari Agustus - Oktober 2025")

        # generate_dummy_data()
        # conn.close()

        