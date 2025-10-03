import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


class ProdukPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(self, text="📦 Input Produk", font=("Helvetica", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=20)

        # Input nama produk
        ttk.Label(self, text="Nama Produk:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.entry_nama = ttk.Entry(self, width=30)
        self.entry_nama.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Input harga
        ttk.Label(self, text="Harga:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.entry_harga = ttk.Entry(self, width=30)
        self.entry_harga.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Input stok
        ttk.Label(self, text="Stok:").grid(row=3, column=0, sticky="e", padx=10, pady=5)
        self.entry_stok = ttk.Entry(self, width=30)
        self.entry_stok.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # Tombol simpan
        ttk.Button(self, text="Simpan", command=self.simpan_produk).grid(row=4, column=0, columnspan=2, pady=15)

    def simpan_produk(self):
        nama = self.entry_nama.get()
        harga = self.entry_harga.get()
        stok = self.entry_stok.get()
        

        if not nama or not harga or not stok:
            messagebox.showerror("Error", "Semua field harus diisi!")
            return

        try:
            harga = float(harga)
            stok = int(stok)
        except ValueError:
            messagebox.showerror("Error", "Harga harus angka, stok harus bilangan bulat!")
            return

        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()
        c.execute("INSERT INTO produk (nama, harga, stok) VALUES (?, ?, ?)", (nama, harga, stok))
        conn.commit()
        conn.close()

        messagebox.showinfo("Sukses", "Produk berhasil ditambahkan.")
        self.entry_nama.delete(0, tk.END)
        self.entry_harga.delete(0, tk.END)
        self.entry_stok.delete(0, tk.END)
