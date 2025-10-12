import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re # Untuk mengekstrak kode akun

# --- DATABASE HELPER ---
def _connect_db():
    return sqlite3.connect('data_keuangan.db')

def _unformat_rupiah_int(formatted_string):
    """Fungsi helper untuk membersihkan string RpX,XXX menjadi integer."""
    # Menghapus 'Rp', spasi, dan koma (separator ribuan)
    return int(str(formatted_string).replace("Rp", "").replace(",", "").strip())

class PembelianPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Map akun yang akan digunakan untuk Combo Box
        self.debit_accounts_map = self._get_debit_accounts()
        akun_list = list(self.debit_accounts_map.keys())

        ttk.Label(self, text="🛒 Manajemen Transaksi Pembelian", font=("Helvetica", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=20)

        frame_kiri = ttk.LabelFrame(self, text="Input Edit Transaksi Pembelian")
        frame_kiri.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # ❗ KOREKSI: Pilihan Akun (Ganti Kategori)
        ttk.Label(frame_kiri, text="Akun Pembelian: ").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.combo_akun = ttk.Combobox(frame_kiri, width=27, state="readonly", values=akun_list)
        self.combo_akun.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Set default value ke akun pertama (jika ada)
        if akun_list:
            self.combo_akun.current(0)
            
        # Baris Keterangan
        ttk.Label(frame_kiri, text="Keterangan Detail: ").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.entry_keterangan = ttk.Entry(frame_kiri, width=30)
        self.entry_keterangan.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Baris Harga
        ttk.Label(frame_kiri, text="Harga Satuan: ").grid(row=3, column=0, sticky="e", padx=10, pady=5)
        self.entry_harga = ttk.Entry(frame_kiri, width=30)
        self.entry_harga.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # Baris Jumlah
        ttk.Label(frame_kiri, text="Kuantitas: ").grid(row=4, column=0, sticky="e", padx=10, pady=5)
        self.entry_jumlah = ttk.Entry(frame_kiri, width=30)
        self.entry_jumlah.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        ttk.Button(frame_kiri, text="Tambah", command=self.tambah_transaksi).grid(row=5, column=0, columnspan=2, pady=15)

        # Tabel Treeview
        # ❗ KOREKSI: Ganti 'kategori' menjadi 'akun' di header
        self.tree = ttk.Treeview(frame_kiri, columns=("id", "akun", "keterangan", "jumlah", "harga", "total"), show="headings", height=8)
        self.tree.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.tree.column("id", width=10, stretch=tk.YES) 
        self.tree.heading("id", text="ID")
        self.tree.column("akun", width=150, anchor="center", stretch=tk.YES)
        self.tree.heading("akun", text="Akun (Debit)")
        self.tree.column("keterangan", width=150, anchor="center", stretch=tk.YES)
        self.tree.heading("keterangan", text="Keterangan Detail")
        self.tree.column("jumlah", width=60, anchor="center", stretch=tk.YES)
        self.tree.heading("jumlah", text="Kuantitas")
        self.tree.column("harga", width=150, anchor="center", stretch=tk.YES)
        self.tree.heading("harga", text="Harga (Rp)")
        self.tree.column("total", width=150, anchor="center", stretch=tk.YES)
        self.tree.heading("total", text="Total (Rp)")
        
        # Scrollbar untuk Treeview
        vsb = ttk.Scrollbar(frame_kiri, orient="vertical", command=self.tree.yview)
        vsb.grid(row=6, column=1, sticky="nse", padx=(0, 10))
        self.tree.configure(yscrollcommand=vsb.set)
        
        ttk.Button(frame_kiri, text="Simpan", command=self.simpan_transaksi).grid(row=7, column=0, columnspan=2, pady=15)

        ttk.Button(frame_kiri, text="Kembali ke menu utama", command=lambda: controller.show_frame("Menu Utama Manager")).grid(row=8, column=0, columnspan=2, pady=5)

        self.item_count = 1

        frame_kanan = ttk.LabelFrame(self, text="Daftar Transaksi Pembelian")
        frame_kanan.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.tree_kanan = ttk.Treeview(frame_kanan, columns=("id", "tanggal", "keterangan", "total"), show="headings", height=10)
        self.tree_kanan.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.tree_kanan.column("id", width=0, stretch=tk.NO)
        self.tree_kanan.heading("id", text="ID")
        self.tree_kanan.column("tanggal", width=100, anchor="center")
        self.tree_kanan.heading("tanggal", text="Tanggal")
        self.tree_kanan.column("keterangan", width=200, anchor="center")
        self.tree_kanan.heading("keterangan", text="Keterangan")
        self.tree_kanan.column("total", width=150, anchor="center")
        self.tree_kanan.heading("total", text="Total (Rp)")

        # Scrollbar untuk Treeview
        vsb_kanan = ttk.Scrollbar(frame_kanan, orient="vertical", command=self.tree_kanan.yview)
        vsb_kanan.grid(row=0, column=2, sticky="nse", padx=(0, 10))
        self.tree_kanan.configure(yscrollcommand=vsb_kanan.set)

        self.load_daftar_transaksi()
        
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

    def tambah_transaksi(self):
        # ❗ KOREKSI: Ambil string akun
        akun_str = self.combo_akun.get()
        keterangan = self.entry_keterangan.get().strip()
        harga_str = self.entry_harga.get().strip()
        jumlah_str = self.entry_jumlah.get().strip()

        if not akun_str:
            messagebox.showerror("Error", "Pilih akun terlebih dahulu!")
            return

        if not keterangan:
            messagebox.showerror("Error", "Keterangan Detail tidak boleh kosong!")
            return

        try:
            jumlah = int(jumlah_str)
            harga = int(harga_str)
        except ValueError:
            messagebox.showerror("Error", "Harga Satuan dan Kuantitas harus berupa angka!")
            return
        
        if jumlah <= 0 or harga <= 0:
            messagebox.showerror("Error", "Harga dan Kuantitas harus lebih besar dari 0!")
            return

        total = harga * jumlah
        item_id = self.item_count

        # Masukkan ke tabel (gunakan string akun penuh)
        self.tree.insert("", "end", values=(
            item_id, 
            akun_str, # ❗ KOREKSI: Akun string
            keterangan, 
            jumlah, 
            f"Rp{harga:,.0f}", 
            f"Rp{total:,.0f}" 
        ))
        self.item_count += 1

        self.entry_keterangan.delete(0, tk.END)
        self.entry_harga.delete(0, tk.END)
        self.entry_jumlah.delete(0, tk.END)

    def simpan_transaksi(self):
        transaksi_data = [self.tree.item(i)["values"] for i in self.tree.get_children()]

        if not transaksi_data:
            messagebox.showerror("Error", "Tidak ada transaksi untuk disimpan!")
            return

        conn = _connect_db()
        c = conn.cursor()

        today = datetime.date.today()
        datestr = today.strftime("%Y%m%d")

        # 1. GENERATE TRANSACTION ID
        try:
            c.execute("""
                SELECT transaksi_pembelian_id 
                FROM transaksi_pembelian 
                WHERE transaksi_pembelian_id LIKE ?
                ORDER BY transaksi_pembelian_id DESC LIMIT 1
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
            messagebox.showerror("Error Database", "Tabel transaksi_pembelian tidak ditemukan.")
            conn.close()
            return

        # 2. CALCULATE TOTAL SEMUA DENGAN PARSING
        total_semua = 0
        try:
            for row in transaksi_data:
                total_item = _unformat_rupiah_int(row[5])
                total_semua += total_item
        except ValueError:
            messagebox.showerror("Error", "Gagal memproses nilai Rupiah. Pastikan harga dan total berupa angka.")
            conn.close()
            return
        
        # Ambil nama akun (kategori) dari item pertama sebagai kategori utama transaksi
        main_akun_str = transaksi_data[0][1]
        main_kategori = self.debit_accounts_map.get(main_akun_str, {}).get('kategori', 'Pembelian')

        # 3. INSERT INTO transaksi_pembelian (MAIN ENTRY)
        # Menggunakan 'kategori' di kolom kategori, bukan kode akun
        c.execute("INSERT INTO transaksi_pembelian (transaksi_pembelian_id, kategori, tanggal, total) VALUES (?, ?, ?, ?)", 
                  (transaksi_id, main_kategori, today, total_semua))

        # 4. LOOP UNTUK DETAIL DAN JURNAL DEBIT
        count = 1
        for data in transaksi_data:
            akun_str = data[1] 
            keterangan_detail = data[2]
            jumlah = data[3]
            harga = _unformat_rupiah_int(data[4])
            total_item = _unformat_rupiah_int(data[5])
            
            count_str = str(count).zfill(3)
            detail_id = f"DPB{datestr}{antrian_str}{count_str}"
            
            # --- INSERT DETAIL TRANSAKSI PEMBELIAN ---
            c.execute(
                "INSERT INTO detail_transaksi_pembelian (detail_pembelian_id, transaksi_pembelian_id, keterangan, jumlah, harga) VALUES (?, ?, ?, ?, ?)",
                (detail_id, transaksi_id, keterangan_detail, jumlah, harga)
            )
            
            # --- PENENTUAN AKUN DEBIT (JURNAL) ---
            # ❗ KOREKSI: Ambil kode akun dari string akun (e.g., "122 - Peralatan" -> "122")
            match = re.match(r"(\d+)", akun_str)
            kode_akun_debit = match.group(1) if match else '520' # Fallback Beban Lain-lain
            
            # Ambil nama akun dari map untuk keterangan
            nama_akun = self.debit_accounts_map.get(akun_str, {}).get('nama', 'Akun Tidak Dikenal')
            
            keterangan_ju = f"Pembelian: {nama_akun} - {keterangan_detail}"

            # --- INSERT JURNAL DEBIT (ASET/BEBAN) ---
            c.execute("""
                INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit)
                VALUES (?, ?, ?, ?, ?)
            """, (transaksi_id, today, kode_akun_debit, keterangan_ju, total_item))
            
            count += 1

        # 5. INSERT FINAL JURNAL CREDIT (KAS, '111') - HANYA SATU KALI
        keterangan_ju_utama = f"Kas keluar untuk Pembelian Transaksi {transaksi_id}"
        c.execute("""
            INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, kredit)
            VALUES (?, ?, ?, ?, ?)
        """, (transaksi_id, today, '111', keterangan_ju_utama, total_semua))

        conn.commit()
        conn.close()

        messagebox.showinfo("Sukses", f"Transaksi {transaksi_id} berhasil disimpan!\nTotal: Rp{total_semua:,.0f}")

        # bersihkan tabel dan reset hitungan
        for i in self.tree.get_children():
            self.tree.delete(i)
            self.item_count = 1

    def load_daftar_transaksi(self):
        conn = _connect_db()
        c = conn.cursor()

        c.execute("SELECT transaksi_pembelian_id, tanggal, total, kategori FROM transaksi_pembelian ORDER BY tanggal DESC")
        rows = c.fetchall()

        for row in rows:
            self.tree_kanan.insert("", tk.END, values=(row[0], row[1], row[3], row[2]))

        conn.close()

