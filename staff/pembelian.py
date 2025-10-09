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

        ttk.Label(self, text="Produk:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.entry_produk = ttk.Entry(self, width=30)
        self.entry_produk.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(self, text="Harga:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.entry_harga = ttk.Entry(self, width=30)
        self.entry_harga.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(self, text="Jumlah:").grid(row=3, column=0, sticky="e", padx=10, pady=5)
        self.entry_jumlah = ttk.Entry(self, width=30)
        self.entry_jumlah.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        ttk.Button(self, text="Tambah", command=self.tambah_transaksi).grid(row=4, column=0, columnspan=2, pady=15)

        self.tree = ttk.Treeview(self, columns=("nama", "jumlah", "harga", "total"), show="headings", height=8)
        self.tree.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.tree.heading("nama", text="Produk")
        self.tree.heading("jumlah", text="Jumlah")
        self.tree.heading("harga", text="Harga (Rp)")  
        self.tree.heading("total", text="Total (Rp)") 

        ttk.Button(self, text="Simpan", command=self.simpan_transaksi).grid(row=6, column=0, columnspan=2, pady=15)

        ttk.Button(self, text="Kembali ke menu utama", command=lambda: controller.show_frame("Menu Utama Staff")).grid(row=7, column=0, columnspan=2, pady=5)

    def tambah_transaksi(self):
        produk = self.entry_produk.get()
        harga = self.entry_harga.get()
        jumlah = self.entry_jumlah.get()
        
        try:
            jumlah = int(jumlah)
        except ValueError:
            messagebox.showerror("Error", "Jumlah harus angka!")
            return
        
        try:
            harga = int(harga)
        except ValueError:
            messagebox.showerror("Error", "Harga harus angka!")
        
        if jumlah <= 0:
            messagebox.showerror("Error", "Jumlah harus lebih besar dari 0!")
            return
        
        if harga <= 0:
            messagebox.showerror("Error", "Harga harus lebih besar dari 0!")
            return
        
        
        total = harga * jumlah

        self.tree.insert("", "end", values=(produk, jumlah, harga, total))
        self.combo_produk.set("")
        self.entry_jumlah.delete(0, tk.END)

    def simpan_transaksi(self):
        transaksi_data = [self.tree.item(i)["values"] for i in self.tree.get_children()]
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
        transaksi_id = f"PJ{datestr}{antrian_str}"

        total_semua = sum([int(row[4]) for row in transaksi_data])

        c.execute("INSERT INTO transaksi_pembelian (transaksi_pembelian_id, tanggal, total) VALUES (?, ?, ?)", (transaksi_id, today, total_semua))

        count = 1
        for data in transaksi_data:
            count_str = str(count).zfill(3)
            detail_id = f"PJ{datestr}{antrian_str}{count_str}"
            c.execute(
                "INSERT INTO detail_transaksi_pembelian (detail_pembelian_id, transaksi_pembelian_id, produk_id, jumlah) VALUES (?, ?, ?, ?)",
                (detail_id, transaksi_id, data[0], data[2])
            )
            count+=1

        conn.commit()
        conn.close()

        messagebox.showinfo("Sukses", "Transaksi berhasil disimpan!")

        for i in self.tree.get_children():
            self.tree.delete(i)
        self.combo_produk.set("")
        self.entry_jumlah.delete(0, tk.END)
