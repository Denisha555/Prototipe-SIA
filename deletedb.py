# import sqlite3
# import sys
# from tkinter import messagebox

# DB_NAME = 'data_keuangan.db'
# # ID_HAPUS diubah menjadi ID Transaksi Penjualan yang spesifik
# ID_HAPUS = 'PJ20251009001' 

# # Nama kolom ID di tabel transaksi_penjualan
# NAMA_KOLOM_ID = 'transaksi_penjualan_id'
# NAMA_TABEL_UTAMA = 'transaksi_penjualan'
# NAMA_TABEL_DETAIL = 'detail_transaksi_penjualan'


# def _connect_db():
#     return sqlite3.connect(DB_NAME)

# def hapus_transaksi_penjualan_agresif():
    
#     conn = _connect_db()
#     c = conn.cursor()
    
#     total_transaksi_deleted = 0
#     total_detail_deleted = 0
#     total_jurnal_deleted = 0
    
#     # Karena ID_HAPUS adalah ID lengkap, kita hapus yang persis sama.
#     # Jika ingin menghapus semua transaksi di tgl 15, gunakan 'PJ20251015' dan hapus [001].
#     print(f"\nMemulai penghapusan data Penjualan {NAMA_KOLOM_ID} = {ID_HAPUS}...")
        
#     try:
#         # 1. Mendapatkan daftar ID Penjualan yang akan dihapus (hanya satu ID spesifik)
#         query_select = f"SELECT {NAMA_KOLOM_ID} FROM {NAMA_TABEL_UTAMA} WHERE {NAMA_KOLOM_ID} = ?"
#         c.execute(query_select, (ID_HAPUS,))
#         ids_penjualan = [row[0] for row in c.fetchall()]
        
#         count_jurnal_pjl = 0
#         count_detail_pjl = 0
        
#         if not ids_penjualan:
#             messagebox.showinfo("Informasi", f"Transaksi Penjualan dengan ID {ID_HAPUS} tidak ditemukan.")
#             conn.close()
#             return
            
#         for pjl_id in ids_penjualan:
#             ref_id_str = str(pjl_id)
            
#             # 2. HAPUS DARI DETAIL TRANSAKSI PENJUALAN
#             c.execute(f"DELETE FROM {NAMA_TABEL_DETAIL} WHERE transaksi_penjualan_id=?", (ref_id_str,))
#             count_detail_pjl += c.rowcount
            
#             # 3. HAPUS DARI JURNAL UMUM (menggunakan ID transaksi penjualan sebagai referensi)
#             c.execute("DELETE FROM jurnal_umum_detail WHERE transaksi_ref_id=?", (ref_id_str,))
#             count_jurnal_pjl += c.rowcount
            
#         # 4. HAPUS DARI TRANSAKSI PENJUALAN UTAMA (hanya ID spesifik)
#         c.execute(f"DELETE FROM {NAMA_TABEL_UTAMA} WHERE {NAMA_KOLOM_ID} = ?", (ID_HAPUS,))
#         count_pjl = c.rowcount
        
#         total_transaksi_deleted += count_pjl
#         total_detail_deleted += count_detail_pjl
#         total_jurnal_deleted += count_jurnal_pjl
        
#         print(f"Penjualan: {count_pjl} transaksi dihapus.")
#         print(f"Detail Penjualan: {total_detail_deleted} entri dihapus.")
#         print(f"Jurnal Terkait: {total_jurnal_deleted} entri dihapus.")

#     except sqlite3.OperationalError as e:
#         conn.rollback()
#         print(f"FATAL ERROR: Gagal mengakses kolom. Detail: {e}")
#         messagebox.showerror("Error FATAL", f"Gagal menghapus data Penjualan. Detail: {e}")
#         sys.exit(1)
#     except sqlite3.Error as e:
#         conn.rollback()
#         print(f"ERROR Database: {e}")
#         messagebox.showerror("Error Database", f"Gagal menghapus data: {e}")
#         raise e
    
#     conn.commit()
#     conn.close()
    
#     print(f"\n=======================================================")
#     print(f"✅ Penghapusan Penjualan {ID_HAPUS} Selesai!")
#     print(f"   - Total Transaksi Penjualan Dihapus: {total_transaksi_deleted}")
#     print(f"   - Total Detail Penjualan Dihapus: {total_detail_deleted}")
#     print(f"   - Total Entri Jurnal Dihapus: {total_jurnal_deleted}")
#     print(f"=======================================================")
    
#     messagebox.showinfo("Sukses Penghapusan", 
#                         f"Transaksi Penjualan {ID_HAPUS} dan jurnal terkait telah berhasil dihapus.\n\n"
#                         f"Total {total_transaksi_deleted} baris Penjualan, {total_detail_deleted} baris detail, dan {total_jurnal_deleted} baris jurnal dihapus.")


# if __name__ == "__main__":
#     if messagebox.askyesno("Konfirmasi Penghapusan", f"Anda YAKIN ingin menghapus transaksi Penjualan {ID_HAPUS} beserta semua detail dan entri jurnal terkait?"):
#         hapus_transaksi_penjualan_agresif()

import sqlite3
import sys
from tkinter import messagebox

DB_NAME = 'data_keuangan.db'

# --- TANGGAL YANG AKAN DIHAPUS ---
TANGGAL_HAPUS = '2025-10-23' 

# --- Tabel yang ditargetkan ---
# Prefix ID Kas Keluar di skema Anda biasanya adalah 'PB' diikuti tanggal.
ID_PREFIX_HAPUS = f'PB{TANGGAL_HAPUS.replace("-", "")}' 
NAMA_TABEL_UTAMA = 'transaksi_kas_keluar'
NAMA_KOLOM_ID = 'transaksi_kas_keluar_id'

def _connect_db():
    return sqlite3.connect(DB_NAME)

def hapus_transaksi_kas_keluar_berdasarkan_tanggal():
    
    conn = _connect_db()
    c = conn.cursor()
    
    total_transaksi_deleted = 0
    total_jurnal_deleted = 0
    
    print(f"\nMemulai penghapusan data Kas Keluar pada tanggal {TANGGAL_HAPUS}...")
        
    try:
        # 1. Mendapatkan daftar SEMUA ID Kas Keluar yang akan dihapus pada tanggal tersebut
        # Kita menggunakan ID PREFIX (misal: PB20251023) DAN tanggal (untuk double check)
        query_select = f"SELECT {NAMA_KOLOM_ID} FROM {NAMA_TABEL_UTAMA} WHERE {NAMA_KOLOM_ID} LIKE ? AND tanggal = ?"
        c.execute(query_select, (f"{ID_PREFIX_HAPUS}%", TANGGAL_HAPUS))
        ids_kas_keluar = [row[0] for row in c.fetchall()]
        
        count_jurnal_kk = 0
        
        if not ids_kas_keluar:
            messagebox.showinfo("Informasi", f"Tidak ada transaksi Kas Keluar yang ditemukan pada tanggal {TANGGAL_HAPUS}.")
            conn.close()
            return
            
        # 2. HAPUS DARI JURNAL UMUM (menggunakan ID transaksi Kas Keluar sebagai referensi)
        placeholders = ','.join('?' for _ in ids_kas_keluar)
        
        c.execute(f"DELETE FROM jurnal_umum_detail WHERE transaksi_ref_id IN ({placeholders})", ids_kas_keluar)
        count_jurnal_kk = c.rowcount
        
        # 3. HAPUS DARI TRANSAKSI KAS KELUAR UTAMA
        c.execute(f"DELETE FROM {NAMA_TABEL_UTAMA} WHERE {NAMA_KOLOM_ID} LIKE ? AND tanggal = ?", (f"{ID_PREFIX_HAPUS}%", TANGGAL_HAPUS))
        count_kk = c.rowcount
        
        total_transaksi_deleted += count_kk
        total_jurnal_deleted += count_jurnal_kk
        
        print(f"Kas Keluar: {count_kk} transaksi dihapus.")
        print(f"Jurnal Terkait: {total_jurnal_deleted} entri dihapus.")

    except sqlite3.OperationalError as e:
        conn.rollback()
        print(f"FATAL ERROR: Gagal mengakses tabel. Detail: {e}")
        messagebox.showerror("Error FATAL", f"Gagal menghapus data Kas Keluar. Detail: {e}")
        sys.exit(1)
    except sqlite3.Error as e:
        conn.rollback()
        print(f"ERROR Database: {e}")
        messagebox.showerror("Error Database", f"Gagal menghapus data: {e}")
        raise e
    
    conn.commit()
    conn.close()
    
    print(f"\n=======================================================")
    print(f"✅ Penghapusan Transaksi Kas Keluar Tgl {TANGGAL_HAPUS} Selesai!")
    print(f"   - Total Transaksi Kas Keluar Dihapus: {total_transaksi_deleted}")
    print(f"   - Total Entri Jurnal Dihapus: {total_jurnal_deleted}")
    print(f"=======================================================")
    
    messagebox.showinfo("Sukses Penghapusan", 
                        f"SEMUA transaksi Kas Keluar tanggal {TANGGAL_HAPUS} dan jurnal terkait telah berhasil dihapus.\n\n"
                        f"Total {total_transaksi_deleted} baris Kas Keluar dan {total_jurnal_deleted} baris jurnal dihapus.")


if __name__ == "__main__":
    if messagebox.askyesno("Konfirmasi Penghapusan", f"Anda YAKIN ingin menghapus SEMUA data Kas Keluar pada tanggal {TANGGAL_HAPUS} beserta entri jurnal terkait?"):
        hapus_transaksi_kas_keluar_berdasarkan_tanggal()