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
        
        c.execute('''CREATE TABLE IF NOT EXISTS produk (
                  product_id TEXT,
                  nama_produk TEXT,
                  deskripsi TEXT,
                  kategori TEXT,
                  harga INTEGER,
                  stok INTEGER)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS transaksi (
                  transaction_id TEXT,
                  tanggal DATE,
                  kategori TEXT
                  keterangan TEXT)
                  ''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS detail_transaksi (
                  detail_id TEXT,
                  transaction_id TEXT,
                  product_id TEXT,
                  jumlah INTEGER,
                  FOREIGN KEY(product_id) REFERENCES PRODUK (product_id),
                  FOREIGN KEY(transaction_id) REFERENCES TRANSAKSI (transaction_id))''')

        conn.commit()
        conn.close()