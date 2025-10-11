import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class JurnalUmumPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(self, text="📘 Jurnal Umum", font=("Helvetica", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=15)

        bulan_list = [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]

        ttk.Label(self, text="Bulan: ").grid(row=1, column=0, sticky="e", pady=5)
        self.combo_bulan = ttk.Combobox(self, width=27, state="readonly", values=bulan_list)
        self.combo_bulan.grid(row=1, column=1, sticky="w", pady=5)

        ttk.Label(self, text="Tahun: ").grid(row=2, column=0, sticky="e", pady=5)
        self.entry_tahun = ttk.Entry(self, width=30)
        self.entry_tahun.grid(row=2, column=1, sticky="w", pady=5)

        ttk.Button(self, text="Tampilkan", command=self.load_laporan).grid(row=3, column=0, columnspan=2, pady=10)

        # Treeview untuk jurnal umum
        self.tree = ttk.Treeview(self, columns=("tanggal", "keterangan", "debit", "kredit"), show="headings", height=15)
        self.tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.tree.heading("tanggal", text="Tanggal")
        self.tree.heading("keterangan", text="Keterangan")
        self.tree.heading("debit", text="Debit (Rp)")
        self.tree.heading("kredit", text="Kredit (Rp)")

        for col in ("tanggal", "keterangan", "debit", "kredit"):
            self.tree.column(col, width=150, anchor="center")

        ttk.Button(self, text="Kembali Ke Menu Utama", command=lambda: controller.show_frame("Menu Utama Manager")
                   ).grid(row=6, column=0, columnspan=2, pady=5)

    def load_laporan(self):
        bulan = self.combo_bulan.get().strip()
        tahun = self.entry_tahun.get().strip()

        nama_ke_angka = {
            "Januari": "01", "Februari": "02", "Maret": "03", "April": "04",
            "Mei": "05", "Juni": "06", "Juli": "07", "Agustus": "08",
            "September": "09", "Oktober": "10", "November": "11", "Desember": "12"
        }
        bulan_angka = nama_ke_angka.get(bulan)

        if not bulan_angka or not tahun:
            messagebox.showerror("Error", "Silakan pilih bulan dan isi tahun terlebih dahulu!")
            return

        for i in self.tree.get_children():
            self.tree.delete(i)

        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()

        # --- Kas Masuk (Penjualan) ---
        c.execute("""
            SELECT tanggal, kategori, total
            FROM transaksi_penjualan
            WHERE strftime('%m', tanggal) = ? AND strftime('%Y', tanggal) = ?
        """, (bulan_angka, tahun))
        kas_masuk = c.fetchall()

        # --- Kas Keluar (Pembelian) ---
        c.execute("""
            SELECT tanggal, kategori, total
            FROM transaksi_pembelian
            WHERE strftime('%m', tanggal) = ? AND strftime('%Y', tanggal) = ?
        """, (bulan_angka, tahun))
        kas_keluar = c.fetchall()

        conn.close()

        # --- Masukkan data ke Treeview ---
        for tanggal, kategori, total in kas_masuk:
            self.tree.insert("", "end", values=(tanggal, "Kas", total, ""))
            self.tree.insert("", "end", values=(tanggal, kategori, "", total))

        for tanggal, kategori, total in kas_keluar:
            self.tree.insert("", "end", values=(tanggal, kategori, "", total))
            self.tree.insert("", "end", values=(tanggal, "Kas", total, ""))

        if not kas_masuk and not kas_keluar:
            messagebox.showinfo("Info", "Tidak ada transaksi untuk bulan dan tahun ini.")

