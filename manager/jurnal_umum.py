import tkinter as tk
import sqlite3
from tkinter import ttk

class JurnalUmumPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(self, text="Jurnal Umum", font=("Helvetica", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=15)

        bulan_list = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

        ttk.Label(self, text="Bulan: ").grid(row=1, column=0, sticky="e", pady=5)
        self.combo_bulan = ttk.Combobox(self, width=27, state="readonly")
        self.combo_bulan.grid(row=1, column=1, sticky="w", pady=5)
        self.combo_bulan['values'] = bulan_list

        ttk.Label(self, text="Tahun: ").grid(row=2, column=0, sticky="e", pady=5)
        self.entry_tahun = ttk.Entry(self, width=30)
        self.entry_tahun.grid(row=2, column=1, sticky="w", pady=5)

        self.tree = ttk.Treeview(self, columns=("tanggal", "keterangan", "debit", "kredit"), show="headings")
        self.tree.grid(row=3, column=0, columnspan=2, pady=5)

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
        c.execute("""
            SELECT transaksi_penjualan_id, kategori, tanggal, total
            FROM transaksi_penjualan
            WHERE strftime('%m', tanggal) = ? AND strftime('%Y', tanggal) = ?
        """, (bulan, tahun))

        kas_masuk = c.fetchall()

        c.execute("""
            SELECT transaksi_pembelian_id, kategori, tanggal, total
            FROM transaksi_pembelian
            WHERE strftime('%m', tanggal) = ? AND strftime('%Y', tanggal) = ?
        """), (bulan, tahun)

        kas_keluar = c.fetchall()

        conn.close()

        


if __name__ == "__main__":
    root = tk.Tk()
    class DummyController:
        def show_frame(self, page_name):
            pass

    app = JurnalUmumPage(root, DummyController)
    app.pack(fill="both", expand=True)
    root.mainloop()
    






        