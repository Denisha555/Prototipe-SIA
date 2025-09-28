import sqlite3

def get_data(bulan, tahun, kategori):
            conn = sqlite3.connect('data_keuangan.db')
            c = conn.cursor()
            if kategori != "Semua":
                query = "SELECT tanggal, jumlah, kategori, keterangan FROM transaksi WHERE strftime('%m', tanggal)=? AND strftime('%Y', tanggal)=? AND kategori=?"
                params = [bulan, tahun, kategori]
            elif kategori == "Semua":
                query = "SELECT tanggal, jumlah, kategori, keterangan FROM transaksi WHERE strftime('%m', tanggal)=? AND strftime('%Y', tanggal)=?"
                params = [bulan, tahun]
            c.execute(query, params)
            results = c.fetchall()
            conn.close()
            return results