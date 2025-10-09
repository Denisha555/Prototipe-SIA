import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


class PenjualanPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Layout dua kolom utama
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        # TITLE
        ttk.Label(self, text="Manajemen Penjualan", font=("Arial", 16)).grid(row=0, column=0, columnspan=2)

        # === FRAME KIRI (Input Transaksi) ===
        self.frame_kiri = ttk.LabelFrame(self, text="Input / Edit Transaksi Penjualan")
        self.frame_kiri.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        ttk.Label(self.frame_kiri, text="Produk:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.combo_produk = ttk.Combobox(self.frame_kiri, width=25, state="readonly")
        self.combo_produk.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(self.frame_kiri, text="Jumlah:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_jumlah = ttk.Entry(self.frame_kiri, width=28)
        self.entry_jumlah.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Button(self.frame_kiri, text="Tambah", command=self.tambah_transaksi).grid(row=3, column=0, columnspan=2, pady=10)

        self.tree_input = ttk.Treeview(self.frame_kiri, columns=("id", "nama", "jumlah", "harga", "total"), show="headings", height=6)
        self.tree_input.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        for col in ("id", "nama", "jumlah", "harga", "total"):
            self.tree_input.heading(col, text=col.capitalize())

        ttk.Button(self.frame_kiri, text="Simpan Transaksi", command=self.simpan_transaksi).grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(self.frame_kiri, text="Kembali", command=lambda: controller.show_frame("Menu Utama Staff")).grid(row=6, column=0, columnspan=2, pady=5)

        # === FRAME KANAN (Daftar Transaksi) ===
        self.frame_kanan = ttk.LabelFrame(self, text="Daftar Transaksi Penjualan", padding=10)
        self.frame_kanan.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.tree_daftar = ttk.Treeview(self.frame_kanan, columns=("id", "tanggal", "total"), show="headings", height=15)
        self.tree_daftar.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        self.tree_daftar.heading("id", text="ID Transaksi")
        self.tree_daftar.heading("tanggal", text="Tanggal")
        self.tree_daftar.heading("total", text="Total (Rp)")

        self.tree_daftar.bind("<Double-1>", self.edit_transaksi)

        ttk.Button(self.frame_kanan, text="Hapus Transaksi", command=self.hapus_transaksi).grid(row=1, column=0, pady=5)
        ttk.Button(self.frame_kanan, text="Refresh", command=self.load_daftar_transaksi).grid(row=1, column=1, pady=5)

        # Inisialisasi data
        self.load_produk()
        self.load_daftar_transaksi()

    # ========================== BAGIAN INPUT ===============================
    def load_produk(self):
        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()
        c.execute("SELECT id, nama_produk, harga, stok FROM produk")
        self.produk_data = c.fetchall()
        conn.close()

        self.combo_produk["values"] = [f"{p[1]} - Rp{p[2]}" for p in self.produk_data]

    def tambah_transaksi(self):
        produk_index = self.combo_produk.current()
        jumlah = self.entry_jumlah.get()

        if produk_index == -1 or not jumlah:
            messagebox.showerror("Error", "Pilih produk dan isi jumlah!")
            return
        
        try:
            jumlah = int(jumlah)
        except ValueError:
            messagebox.showerror("Error", "Jumlah harus angka!")
            return
        
        produk_id, nama, harga, stok = self.produk_data[produk_index]
        if jumlah <= 0 or jumlah > stok:
            messagebox.showerror("Error", "Jumlah tidak valid atau melebihi stok!")
            return
        
        total = harga * jumlah
        self.tree_input.insert("", "end", values=(produk_id, nama, jumlah, harga, total))
        self.combo_produk.set("")
        self.entry_jumlah.delete(0, tk.END)

    def simpan_transaksi(self):
        transaksi_data = [self.tree_input.item(i)["values"] for i in self.tree_input.get_children()]
        if not transaksi_data:
            messagebox.showerror("Error", "Belum ada produk yang ditambahkan!")
            return

        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()

        today = datetime.date.today()
        c.execute("SELECT transaksi_penjualan_id FROM transaksi_penjualan WHERE tanggal = ?", (today,))
        existing = c.fetchall()
        antrian_str = str(len(existing) + 1).zfill(3)
        datestr = today.strftime("%Y%m%d")
        transaksi_id = f"PJ{datestr}{antrian_str}"

        total_semua = sum([int(row[4]) for row in transaksi_data])

        c.execute("INSERT INTO transaksi_penjualan (transaksi_penjualan_id, tanggal, total) VALUES (?, ?, ?)", 
                  (transaksi_id, today, total_semua))

        count = 1
        for data in transaksi_data:
            detail_id = f"{transaksi_id}{str(count).zfill(3)}"
            c.execute("INSERT INTO detail_transaksi_penjualan (detail_penjualan_id, transaksi_penjualan_id, produk_id, jumlah) VALUES (?, ?, ?, ?)",
                      (detail_id, transaksi_id, data[0], data[2]))
            c.execute("UPDATE produk SET stok = stok - ? WHERE id = ?", (data[2], data[0]))
            count += 1

        conn.commit()
        conn.close()

        messagebox.showinfo("Sukses", "Transaksi berhasil disimpan!")
        for i in self.tree_input.get_children():
            self.tree_input.delete(i)
        self.load_daftar_transaksi()

    # ========================== BAGIAN KANAN (DAFTAR TRANSAKSI) ===============================
    def load_daftar_transaksi(self):
        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()
        c.execute("SELECT transaksi_penjualan_id, tanggal, total FROM transaksi_penjualan ORDER BY tanggal DESC")
        rows = c.fetchall()
        conn.close()

        for i in self.tree_daftar.get_children():
            self.tree_daftar.delete(i)
        for row in rows:
            self.tree_daftar.insert("", "end", values=row)

    def hapus_transaksi(self):
        selected = self.tree_daftar.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih transaksi yang ingin dihapus!")
            return
        transaksi_id = self.tree_daftar.item(selected[0])["values"][0]

        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()
        c.execute("DELETE FROM detail_transaksi_penjualan WHERE transaksi_penjualan_id = ?", (transaksi_id,))
        c.execute("DELETE FROM transaksi_penjualan WHERE transaksi_penjualan_id = ?", (transaksi_id,))
        conn.commit()
        conn.close()

        self.load_daftar_transaksi()
        messagebox.showinfo("Sukses", "Transaksi berhasil dihapus.")

    def edit_transaksi(self, event):
        """Double-click untuk load data ke form kiri"""
        selected = self.tree_daftar.selection()
        if not selected:
            return
        transaksi_id = self.tree_daftar.item(selected[0])["values"][0]

        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()
        c.execute("""
            SELECT p.id, p.nama_produk, d.jumlah, p.harga, (d.jumlah * p.harga)
            FROM detail_transaksi_penjualan d
            JOIN produk p ON p.id = d.produk_id
            WHERE d.transaksi_penjualan_id = ?
        """, (transaksi_id,))
        rows = c.fetchall()
        conn.close()

        for i in self.tree_input.get_children():
            self.tree_input.delete(i)
        for row in rows:
            self.tree_input.insert("", "end", values=row)

        messagebox.showinfo("Edit Mode", f"Data transaksi {transaksi_id} dimuat untuk diedit.")
