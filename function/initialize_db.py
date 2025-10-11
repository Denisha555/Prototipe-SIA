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
        
        c.execute('''CREATE TABLE IF NOT EXISTS transaksi_pembelian (
                  transaksi_pembelian_id TEXT PRIMARY KEY,
                  tanggal DATE,
                  kategori TEXT,
                  total INTEGER,
                  keterangan TEXT)
                  ''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS detail_transaksi_pembelian (
                  detail_pembelian_id TEXT PRIMARY KEY,
                  transaksi_pembelian_id TEXT,
                  keterangan TEXT,
                  harga INTEGER,
                  jumlah INTEGER,
                  FOREIGN KEY(transaksi_pembelian_id) REFERENCES TRANSAKSI_PEMBELIAN (transaksi_pembelian_id))
                  ''')

        conn.commit()
        conn.close()