import sqlite3
import sys
from tkinter import messagebox

DB_NAME = 'data_keuangan.db'
# ID_HAPUS saat ini adalah PB20251012001. 
# Jika ingin menghapus transaksi lain, ganti nilai variabel ini.
ID_HAPUS = 'PB20251012001' 

# Nama kolom ID di tabel transaksi_pembelian
NAMA_KOLOM_ID = 'transaksi_pembelian_id'

def _connect_db():
    return sqlite3.connect(DB_NAME)

def hapus_transaksi_pembelian_agresif():
    
    conn = _connect_db()
    c = conn.cursor()
    
    total_transaksi_deleted = 0
    total_detail_deleted = 0 # Tambah penghitung untuk detail
    total_jurnal_deleted = 0
    
    print(f"\nMemulai penghapusan data Pembelian transaksi_pembelian_id {ID_HAPUS}...")
        
    try:
        # 1. Mendapatkan daftar ID Pembelian yang akan dihapus (Fix: Tambah LIKE)
        # Jika ID_HAPUS adalah 'PB20251012001', ini akan mencari yang persis sama.
        # Jika Anda hanya ingin menghapus berdasarkan tanggal ('PB20251012'), hapus 001.
        query_select = f"SELECT {NAMA_KOLOM_ID} FROM transaksi_pembelian WHERE transaksi_pembelian_id LIKE ?"
        c.execute(query_select, (f"{ID_HAPUS}%",))
        ids_pembelian = [row[0] for row in c.fetchall()]
        
        count_jurnal_pbl = 0
        count_detail_pbl = 0
        
        for pbl_id in ids_pembelian:
            ref_id_str = str(pbl_id)
            
            # 2. HAPUS DARI DETAIL TRANSAKSI PEMBELIAN (FIX BARU)
            c.execute("DELETE FROM detail_transaksi_pembelian WHERE transaksi_pembelian_id=?", (ref_id_str,))
            count_detail_pbl += c.rowcount
            
            # 3. HAPUS DARI JURNAL UMUM (menggunakan ID transaksi pembelian sebagai referensi)
            c.execute("DELETE FROM jurnal_umum_detail WHERE transaksi_ref_id=?", (ref_id_str,))
            count_jurnal_pbl += c.rowcount
            
            # 4. Hapus baris yang tidak relevan (PBL_) karena ID referensi transaksi pembelian harus PB...
            # Baris berikut dihapus/diabaikan karena ID pembelian yang benar adalah 'PB...'
            # c.execute("DELETE FROM jurnal_umum_detail WHERE transaksi_ref_id=?", (f"PBL_{ref_id_str}",))
            # count_jurnal_pbl += c.rowcount
            
        # 5. HAPUS DARI TRANSAKSI PEMBELIAN UTAMA (Fix: Tambah LIKE)
        c.execute(f"DELETE FROM transaksi_pembelian WHERE {NAMA_KOLOM_ID} LIKE ?", (f"{ID_HAPUS}%",))
        count_pbl = c.rowcount
        
        total_transaksi_deleted += count_pbl
        total_detail_deleted += count_detail_pbl
        total_jurnal_deleted += count_jurnal_pbl
        
        print(f"Pembelian: {count_pbl} transaksi dihapus.")
        print(f"Detail Pembelian: {total_detail_deleted} entri dihapus.")
        print(f"Jurnal Terkait: {total_jurnal_deleted} entri dihapus.")

    except sqlite3.OperationalError as e:
        conn.rollback()
        print(f"FATAL ERROR: Gagal mengakses kolom. Detail: {e}")
        messagebox.showerror("Error FATAL", f"Gagal menghapus data Pembelian. Detail: {e}")
        sys.exit(1)
    except sqlite3.Error as e:
        conn.rollback()
        print(f"ERROR Database: {e}")
        messagebox.showerror("Error Database", f"Gagal menghapus data: {e}")
        raise e
    
    conn.commit()
    conn.close()
    
    print(f"\n=======================================================")
    print(f"✅ Penghapusan Pembelian transaksi_pembelian_id {ID_HAPUS} Selesai!")
    print(f"   - Total Transaksi Pembelian Dihapus: {total_transaksi_deleted}")
    print(f"   - Total Detail Pembelian Dihapus: {total_detail_deleted}")
    print(f"   - Total Entri Jurnal Dihapus: {total_jurnal_deleted}")
    print(f"=======================================================")
    
    messagebox.showinfo("Sukses Penghapusan", 
                         f"Transaksi Pembelian transaksi_pembelian_id {ID_HAPUS} dan jurnal terkait telah berhasil dihapus.\n\n"
                         f"Total {total_transaksi_deleted} baris Pembelian, {total_detail_deleted} baris detail, dan {total_jurnal_deleted} baris jurnal dihapus.")


if __name__ == "__main__":
    if ID_HAPUS.startswith("YYYY"):
        messagebox.showerror("Error", "Mohon ganti variabel ID_HAPUS di dalam script dengan transaksi_pembelian_id yang benar.")
        sys.exit(1)
        
    if messagebox.askyesno("Konfirmasi Penghapusan", f"Anda YAKIN ingin menghapus SEMUA transaksi Pembelian dan jurnal transaksi_pembelian_id {ID_HAPUS}?"):
        hapus_transaksi_pembelian_agresif()