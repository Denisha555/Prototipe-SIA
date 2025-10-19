import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re 

# --- DATABASE HELPER ---
def _connect_db():
    return sqlite3.connect('data_keuangan.db')

def _unformat_rupiah_int(formatted_string):
    """Fungsi helper untuk membersihkan string RpX,XXX menjadi integer."""
    # Menghapus 'Rp', spasi, dan koma (separator ribuan)
    return int(str(formatted_string).replace("Rp", "").replace(",", "").strip())

class KasKeluarPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Map akun yang akan digunakan untuk Combo Box
        self.debit_accounts_map = self._get_debit_accounts()
        akun_list = list(self.debit_accounts_map.keys())

        ttk.Label(self, text="💸 Input  Pengeluaran", font=("Helvetica", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=20)

        # ❗ KOREKSI: Pilihan Akun (Ganti Kategori)
        ttk.Label(self, text="Akun: ").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.combo_akun = ttk.Combobox(self, width=27, state="readonly", values=akun_list)
        self.combo_akun.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Set default value ke akun pertama (jika ada)
        if akun_list:
            self.combo_akun.current(0)
            
        # Baris Keterangan
        ttk.Label(self, text="Keterangan Detail: ").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.entry_keterangan = ttk.Entry(self, width=30)
        self.entry_keterangan.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Baris Harga
        ttk.Label(self, text="Nominal (Rp): ").grid(row=3, column=0, sticky="e", padx=10, pady=5)
        self.entry_harga = ttk.Entry(self, width=30)
        self.entry_harga.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        ttk.Button(self, text="Simpan", command=self.simpan_transaksi).grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(self, text="Kembali Ke Menu Utama", command=lambda: controller.show_frame("Menu Utama Staff")
                   ).grid(row=6, column=0, columnspan=2, pady=5)
        
    def _get_debit_accounts(self):
        """Mengambil akun yang relevan untuk pembelian (Aset Debit dan Semua Beban)."""
        conn = _connect_db()
        c = conn.cursor()
        
        # Akun yang diabaikan: 111 Kas (Kredit untuk Pembelian), 112 Piutang, Utang, Modal, Pendapatan
        # Kita ingin semua akun Aset (kecuali 111, 112) dan semua akun Beban.
        query = """
            SELECT kode_akun, nama_akun, kategori 
            FROM akun 
            WHERE (kategori = 'Aset' AND kode_akun NOT IN ('111', '112')) 
               OR kategori = 'Beban'
            ORDER BY kode_akun ASC
        """
        
        akun_map = {}
        try:
            c.execute(query)
            for kode, nama, kategori in c.fetchall():
                key = f"{kode} - {nama}"
                akun_map[key] = {'kode': kode, 'nama': nama, 'kategori': kategori}
        except sqlite3.Error as e:
            messagebox.showerror("Error Database", f"Gagal memuat daftar akun: {e}")
        finally:
            conn.close()
            
        return akun_map

    def simpan_transaksi(self):
        """
        Menyimpan data transaksi ke dalam sistem
        Mengambil nilai dari input field dan melakukan validasi sebelum disimpan
        """
        # Ambil nilai dari entry
        akun = self.combo_akun.get()
        keterangan = self.entry_keterangan.get()
        nominal = self.entry_harga.get()

        # Validasi input
        if not akun or not keterangan or not nominal:
            messagebox.showwarning("Peringatan", "Mohon isi semua kolom input.")

        conn = _connect_db()
        c = conn.cursor()

        today = datetime.date.today()
        datestr = today.strftime("%Y%m%d")

        try:
            c.execute("""
                SELECT transaksi_kas_keluar_id 
                FROM transaksi_kas_keluar 
                WHERE transaksi_kas_keluar_id LIKE ?
                ORDER BY transaksi_kas_keluar_id DESC LIMIT 1
            """, (f"PB{datestr}%",))
            last_id = c.fetchone()

            if last_id:
                # Ambil 3 digit terakhir dari ID terakhir hari itu
                last_num = int(last_id[0][-3:])
                antrian = last_num + 1
            else:
                antrian = 1

            antrian_str = str(antrian).zfill(3)
            transaksi_id = f"PB{datestr}{antrian_str}"
        except sqlite3.OperationalError:
            messagebox.showerror("Error Database", "Tabel transaksi_kas_keluar tidak ditemukan.")
            conn.close()
            return
        
        c.execute("INSERT INTO transaksi_kas_keluar (transaksi_kas_keluar_id, kategori, tanggal, nominal) VALUES (?, ?, ?, ?)", 
                  (transaksi_id, akun, today, nominal))
            
        # --- PENENTUAN AKUN DEBIT (JURNAL) ---
        match = re.match(r"(\d+)", akun)
        kode_akun_debit = match.group(1) if match else '520' # Fallback Beban Lain-lain
        
        # Ambil nama akun dari map untuk keterangan
        nama_akun = self.debit_accounts_map.get(akun, {}).get('nama', 'Akun Tidak Dikenal')
        
        keterangan_ju = f"Pembelian: {nama_akun} - {keterangan}"

        # --- INSERT JURNAL DEBIT (ASET/BEBAN) ---
        c.execute("""
            INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit)
            VALUES (?, ?, ?, ?, ?)
        """, (transaksi_id, today, kode_akun_debit, keterangan_ju, nominal))

        # 5. INSERT FINAL JURNAL CREDIT (KAS, '111') - HANYA SATU KALI
        keterangan_ju_utama = f"Kas keluar untuk Pembelian Transaksi {transaksi_id}"
        c.execute("""
            INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, kredit)
            VALUES (?, ?, ?, ?, ?)
        """, (transaksi_id, today, '111', keterangan_ju_utama, nominal))

        conn.commit()
        conn.close()

        messagebox.showinfo("Sukses", f"Transaksi {transaksi_id} berhasil disimpan!")

        self.entry_keterangan.delete(0, tk.END)
        self.entry_harga.delete(0, tk.END)