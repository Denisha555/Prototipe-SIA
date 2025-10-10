import tkinter as tk
import sqlite3
from tkinter import ttk

class JurnalUmumPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Jurnal Umum", font=("Helvetica", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=15)

        ttk.Label(self, text="Bulan: ").grid(row=1, column=0)
        self.combo_bulan = ttk.Combobox()

        ttk.Label(self, text="Tahun: ").grid(row=2, column=0)
        self.entry_tahun = ttk.Entry(self, width=30)
        self.entry_tahun.grid(row=2, column=1)

        self.tree = ttk.Treeview(self, columns=("tanggal", "keterangan", "debit", "kredit"), show="headings")
        self.tree.grid(row=3, column=0, columnspan=2)

        self.tree.heading("tanggal", text="Tanggal")
        self.tree.heading("keterangan", text="Keterangan")
        self.tree.heading("debit", text="Debit (Rp)")
        self.tree.heading("kredit", text="Kredit (Rp)")

        self.load_laporan()

    def load_laporan(self):
        bulan = self.combo_bulan.get()
        tahun = self.entry_tahun.get()

        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()
        c.execute("SELECT ")

    






        