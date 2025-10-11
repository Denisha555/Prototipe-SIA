import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class PembelianPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(self, text="🛒 Input Transaksi Pembelian", font=("Helvetica", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=20)

        ttk.Label(self, text="Kategori: ").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.combo_kategori = ttk.Combobox(self, width=27, state="readonly")
        self.combo_kategori.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.combo_kategori["values"] = ["Peralatan", "Perlengkapan", "Biaya", "Beban"]
        
        ttk.Label(self, text="Keterangan: ").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.entry_keterangan = ttk.Entry(self, width=30)
        self.entry_keterangan.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(self, text="Harga: ").grid(row=3, column=0, sticky="e", padx=10, pady=5)
        self.entry_harga = ttk.Entry(self, width=30)
        self.entry_harga.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(self, text="Jumlah: ").grid(row=4, column=0, sticky="e", padx=10, pady=5)
        self.entry_jumlah = ttk.Entry(self, width=30)
        self.entry_jumlah.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        ttk.Button(self, text="Tambah", command=self.tambah_transaksi).grid(row=5, column=0, columnspan=2, pady=15)

        # ✅ Tambahkan kolom "id" di tabel tree
        self.tree = ttk.Treeview(self, columns=("id", "kategori", "keterangan", "jumlah", "harga", "total"), show="headings", height=8)
        self.tree.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        for col, text in [
            ("id", "ID"),
            ("kategori", "Kategori"),
            ("keterangan", "Keterangan"),
            ("jumlah", "Jumlah"),
            ("harga", "Harga (Rp)"),
            ("total", "Total (Rp)")
        ]:
            self.tree.heading(col, text=text, anchor="center")
            self.tree.column(col, anchor="center", width=120)

        ttk.Button(self, text="Simpan", command=self.simpan_transaksi).grid(row=7, column=0, columnspan=2, pady=15)

        ttk.Button(self, text="Kembali ke menu utama", command=lambda: controller.show_frame("Menu Utama Staff")).grid(row=8, column=0, columnspan=2, pady=5)

        # counter untuk id item sementara
        self.item_count = 1

    def tambah_transaksi(self):
        kategori = self.combo_kategori.get()
        keterangan = self.entry_keterangan.get().strip()
        harga = self.entry_harga.get().strip()
        jumlah = self.entry_jumlah.get().strip()

        if not kategori:
            messagebox.showerror("Error", "Pilih kategori terlebih dahulu!")
            return

        if not keterangan:
            messagebox.showerror("Error", "Keterangan tidak boleh kosong!")
            return

        try:
            jumlah = int(jumlah)
            harga = int(harga)
        except ValueError:
            messagebox.showerror("Error", "Harga dan Jumlah harus berupa angka!")
            return
        
        if jumlah <= 0 or harga <= 0:
            messagebox.showerror("Error", "Harga dan Jumlah harus lebih besar dari 0!")
            return

        total = harga * jumlah
        item_id = self.item_count

        # masukkan ke tabel
        self.tree.insert("", "end", values=(item_id, kategori, keterangan, jumlah, f"Rp{harga:,.0f}", f"Rp{total:,.0f}"))
        self.item_count += 1

        # reset input
        self.combo_kategori.set("")
        self.entry_keterangan.delete(0, tk.END)
        self.entry_harga.delete(0, tk.END)
        self.entry_jumlah.delete(0, tk.END)

    def simpan_transaksi(self):
        transaksi_data = [self.tree.item(i)["values"] for i in self.tree.get_children()]
        kategori = self.combo_kategori.get()

        if not transaksi_data:
            messagebox.showerror("Error", "Tidak ada transaksi untuk disimpan!")
            return

        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()

        today = datetime.date.today()
        c.execute("SELECT transaksi_pembelian_id FROM transaksi_pembelian WHERE tanggal = ?", (today,))
        existing = c.fetchall()
        antrian = len(existing) + 1
        antrian_str = str(antrian).zfill(3)

        datestr = today.strftime("%Y%m%d")
        transaksi_id = f"PB{datestr}{antrian_str}"

        total_semua = sum([int(str(row[5]).replace("Rp", "").replace(",", "")) for row in transaksi_data])

        c.execute("INSERT INTO transaksi_pembelian (transaksi_pembelian_id, kategori, tanggal, total) VALUES (?, ?, ?, ?)", 
                  (transaksi_id, kategori, today, total_semua))

        count = 1
        for data in transaksi_data:
            count_str = str(count).zfill(3)
            detail_id = f"DPB{datestr}{antrian_str}{count_str}"
            keterangan = data[2]
            jumlah = data[3]
            harga = int(str(data[4]).replace("Rp", "").replace(",", ""))

            c.execute(
                "INSERT INTO detail_transaksi_pembelian (detail_pembelian_id, transaksi_pembelian_id, keterangan, jumlah, harga) VALUES (?, ?, ?, ?, ?)",
                (detail_id, transaksi_id, keterangan, jumlah, harga)
            )
            count += 1

        conn.commit()
        conn.close()

        messagebox.showinfo("Sukses", f"Transaksi {transaksi_id} berhasil disimpan!\nTotal: Rp{total_semua:,.0f}")

        # bersihkan tabel
        for i in self.tree.get_children():
            self.tree.delete(i)

        self.item_count = 1
