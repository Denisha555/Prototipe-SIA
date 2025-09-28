import sqlite3

def get_data(bulan, tahun, kategori, include_id=False):
    conn = sqlite3.connect('data_keuangan.db')
    c = conn.cursor()
    
    select_cols = "id, tanggal, jumlah, kategori, keterangan" if include_id else "tanggal, jumlah, kategori, keterangan"
    
    where_clause = "strftime('%m', tanggal)=? AND strftime('%Y', tanggal)=?"
    params = [bulan, tahun]

    if kategori != "Semua":
        query = f"SELECT {select_cols} FROM transaksi WHERE {where_clause} AND kategori=?"
        params.append(kategori)
    else:
        query = f"SELECT {select_cols} FROM transaksi WHERE {where_clause}"
        
    try:
        c.execute(query, params)
        results = c.fetchall()
    except sqlite3.Error as e:
        print(f"Database Error during query: {e}")
        results = []
    finally:
        conn.close()
        
    return results
