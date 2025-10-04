import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


class TransaksiPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(self, text="🛒 Input Transaksi", font=("Helvetica", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=20)

        # Pilih produk
        ttk.Label(self, text="Produk:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.combo_produk = ttk.Combobox(self, width=27, state="readonly")
        self.combo_produk.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Jumlah
        ttk.Label(self, text="Jumlah:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.entry_jumlah = ttk.Entry(self, width=30)
        self.entry_jumlah.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Tombol tambah
        ttk.Button(self, text="Tambah", command=self.simpan_transaksi).grid(row=3, column=0, columnspan=2, pady=15)

        # Tabel transaksi
        self.tree = ttk.Treeview(self, columns=("produk", "jumlah"), show="headings", height=8)
        self.tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.tree.heading("produk", text="Produk")
        self.tree.heading("jumlah", text="Jumlah")
        self.tree.heading("total", text="Total (Rp)")   

        # Load data produk untuk combobox
        self.load_produk()

    def load_produk(self):
        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()
        c.execute("SELECT product_id, nama_produk, harga FROM produk")
        self.produk_data = c.fetchall()
        conn.close()

        # isi combobox dengan nama produk
        self.combo_produk["values"] = [f"{p[1]} - Rp{p[2]}" for p in self.produk_data]

    def simpan_transaksi(self):
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

        produk_id, nama, harga = self.produk_data[produk_index]
        total = harga * jumlah

        # simpan ke database
        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()
        c.execute("INSERT INTO detail_transaksi (produk_id, jumlah) VALUES (?, ?, ?)", (produk_id, jumlah, total))
        conn.commit()
        conn.close()

        # tampilkan di treeview
        self.tree.insert("", "end", values=(nama, jumlah, total))

        # reset input
        self.combo_produk.set("")
        self.entry_jumlah.delete(0, tk.END)
