import sqlite3

def initialize_db(self):
        conn = sqlite3.connect('data_keuangan.db')
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS transaksi (
                            id TEXT PRIMARY KEY,
                            tanggal TEXT,
                            kategori TEXT,
                            keterangan TEXT,
                            jumlah INTEGER)''')
                            
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
                    username TEXT UNIQUE,
                    password TEXT,
                    role TEXT)''')

        conn.commit()
        conn.close()