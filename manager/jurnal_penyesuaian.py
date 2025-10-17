import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from function.bulan_map import bulan_map
from datetime import datetime

def _format_rupiah(amount):
    try:
        amount = int(amount)
        if amount == 0:
            return ""
        return f"{amount:,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return "-"


class JurnalPenyesuaianPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(
            self, text="📘 Jurnal Penyesuaian", font=("Helvetica", 18, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=15)

        bulan_list = list(bulan_map.keys())

        ttk.Label(self, text="Bulan: ").grid(row=1, column=0, sticky="e", pady=5)
        self.combo_bulan = ttk.Combobox(
            self, width=27, state="readonly", values=bulan_list
        )
        self.combo_bulan.grid(row=1, column=1, sticky="w", pady=5)

        bulan_ini = datetime.now().month
        bulan_nama_default = list(bulan_map.keys())[bulan_ini - 1]
        self.combo_bulan.set(bulan_nama_default)

        ttk.Label(self, text="Tahun: ").grid(row=2, column=0, sticky="e", pady=5)
        self.entry_tahun = ttk.Entry(self, width=30)
        self.entry_tahun.grid(row=2, column=1, sticky="w", pady=5)
        self.entry_tahun.insert(0, datetime.now().year)

        ttk.Button(
            self, text="Tampilkan", command=self.load_laporan
        ).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(self, text="Kembali ke Menu Utama", command=lambda: controller.show_frame("Menu Utama Manager")
                    ).grid(row=6, column=0, columnspan=2, pady=5)

        # === Treeview untuk menampilkan data ===
        self.tree = ttk.Treeview(
            self,
            columns=("tanggal", "kode_akun", "nama_akun", "debit", "kredit"),
            show="headings",
            height=15,
        )
        self.tree.grid(row=4, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

        self.tree.heading("tanggal", text="Tanggal")
        self.tree.heading("kode_akun", text="Kode Akun")
        self.tree.heading("nama_akun", text="Nama Akun")
        self.tree.heading("debit", text="Debit (Rp)")
        self.tree.heading("kredit", text="Kredit (Rp)")

        self.tree.column("tanggal", width=150, anchor="center")
        self.tree.column("kode_akun", width=150, anchor="center")
        self.tree.column("nama_akun", width=150, anchor="w")
        self.tree.column("debit", width=130, anchor="e")
        self.tree.column("kredit", width=130, anchor="e")

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=4, column=2, sticky="ns")

    def load_laporan(self):
        bulan_nama = self.combo_bulan.get().strip()
        tahun = self.entry_tahun.get().strip()

        if not bulan_nama or not tahun:
            messagebox.showerror("Error", "Silakan pilih bulan dan isi tahun terlebih dahulu.")
            return
        
        try:
            bulan = bulan_map.get(bulan_nama)
            conn = sqlite3.connect("data_keuangan.db")
            c = conn.cursor()
            query = """
                SELECT t.tanggal, t.kode_akun, a.nama_akun, t.debit, t.kredit
                FROM transaksi_penyesuaian t
                JOIN akun a ON t.kode_akun = a.kode_akun
                WHERE strftime('%m', t.tanggal) = ? AND strftime('%Y', t.tanggal) = ?
                ORDER BY t.tanggal ASC
            """
            c.execute(query, (bulan, tahun))
            rows = c.fetchall()
            conn.close()

            # Hapus data lama
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            total_debit = 0
            total_kredit = 0
            last_ref_id = None

            if not rows:
                messagebox.showinfo("Info", "Tidak ada data penyesuaian untuk bulan ini.")
                return

            # Tambah data baru
            for row in rows:
                tanggal, kode_akun, nama_akun, debit, kredit = row
                debit = debit if debit is not None else 0
                kredit = kredit if kredit is not None else 0

                if kredit > 0:
                    nama_akun = f"        {nama_akun}"
                
                debit_str = _format_rupiah(debit)
                kredit_str = _format_rupiah(kredit)

                self.tree.insert(
                    "", "end", values=(tanggal, kode_akun, nama_akun, debit_str, kredit_str)
                )

                total_debit += debit
                total_kredit += kredit

            # Baris Total
            self.tree.insert("", "end", values=(
                "", "", "TOTAL", _format_rupiah(total_debit), _format_rupiah(total_kredit)
            ), tags=('total',))
            self.tree.tag_configure('total', font=('Helvetica', 10, 'bold'), background='#E0F7FA')
            
            if total_debit != total_kredit:
                 messagebox.showwarning("Peringatan", "Jurnal Penyesuaian TIDAK SEIMBANG! Mohon cek transaksi Anda.")


        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat data: {e}")
            print(e)
            