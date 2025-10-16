import sqlite3

def initialize_db(self):
        conn = sqlite3.connect('data_keuangan.db')
        c = conn.cursor()
                            
        c.execute('''CREATE TABLE IF NOT EXISTS pajak (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tanggal TEXT,
                    jenis_pajak TEXT,
                    jumlah INTEGER)''')
                    
        c.execute('''CREATE TABLE IF NOT EXISTS penggajian (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tanggal TEXT,
                    nama_karyawan TEXT,
                    gaji_bersih INTEGER)''')
        
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
            ('401', 'Pendapatan Jasa', 'Pendapatan', 'Kredit'), 
            ('511', 'Beban Gaji', 'Beban', 'Debit'), 
            ('512', 'Beban Pajak', 'Beban', 'Debit'), 
            ('513', 'Beban Perlengkapan', 'Beban', 'Debit'),
            ('514', 'Beban Penyusutan Peralatan', 'Beban', 'Debit'),
            ('520', 'Beban Lain-lain', 'Beban', 'Debit'),
            ('600', 'Ikhtisar Laba/Rugi', 'Nominal', 'Debit')
        ]

        c.execute("SELECT COUNT(*) FROM akun")
        if c.fetchone()[0] == 0:
            c.executemany("INSERT INTO akun (kode_akun, nama_akun, kategori, saldo_normal) VALUES (?, ?, ?, ?)", initial_coa)

        conn.commit()
        conn.close()