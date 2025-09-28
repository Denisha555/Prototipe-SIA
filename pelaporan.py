import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from get_data import get_data
from bulan_map import bulan_map

class PelaporanPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Styling
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 11), padding=6)
        style.configure("Title.TLabel", font=("Helvetica", 18, "bold"))


        # Judul
        ttk.Label(self, text="📊 Laporan Keuangan", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, pady=20
        )

        # Input Bulan
        ttk.Label(self, text="Bulan").grid(row=1, column=0, sticky="e", pady=5, padx=20)
        self.combo_bulan = ttk.Combobox(
            self,
            values=[
                "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                "Juli", "Agustus", "September", "Oktober", "November", "Desember"
            ],
            state="readonly",
            width=15
        )
        self.combo_bulan.grid(row=1, column=1, pady=5, sticky="w")

        # Input Tahun
        ttk.Label(self, text="Tahun").grid(row=2, column=0, sticky="e", pady=5, padx=20)
        self.entry_tahun = ttk.Entry(self, width=18)
        self.entry_tahun.grid(row=2, column=1, pady=5, sticky="w")

        # Input Kategori
        ttk.Label(self, text="Kategori").grid(row=3, column=0, sticky="e", pady=5, padx=20)
        self.combo_kategori = ttk.Combobox(
            self,
            values=["Semua", "Pemasukan", "Pengeluaran"],
            state="readonly",
            width=15
        )
        self.combo_kategori.grid(row=3, column=1, pady=10, sticky="w")

        def show_laporan():
            bulan = self.combo_bulan.get()
            bulan = bulan_map.get(bulan, "")
            tahun = self.entry_tahun.get()
            kategori = self.combo_kategori.get()

            if not (bulan and tahun.isdigit()):
                messagebox.showerror("Error", "Tahun harus diisi dengan benar!")
                return

            if not kategori:
                messagebox.showerror("Error", "Kategori harus dipilih!")
                return
            
            data = get_data(bulan, tahun, kategori)

            if not data:
                messagebox.showerror("Error", "Tidak ada data untuk periode ini!")
                return
            
            # Tampilkan data di bawah
            laporan_window = tk.Toplevel(self)
            laporan_window.title("Laporan Keuangan")
            width = self.winfo_screenwidth()
            height = self.winfo_screenheight()
            laporan_window.geometry(f"{width}x{height}")
            laporan_window.grab_set()
            laporan_window.transient(self)
            laporan_window.focus_set()
            laporan_window.rowconfigure(0, weight=1)
            laporan_window.columnconfigure(0, weight=1)
            tree = ttk.Treeview(laporan_window, columns=("Tanggal", "Jumlah", "Kategori", "Keterangan"), show="headings")
            tree.heading("Tanggal", text="Tanggal")
            tree.heading("Jumlah", text="Jumlah")
            tree.heading("Kategori", text="Kategori")
            tree.heading("Keterangan", text="Keterangan")
            tree.grid(row=0, column=0, sticky="nsew")
            for row in data:
                tree.insert("", tk.END, values=row)
            scrollbar = ttk.Scrollbar(laporan_window, orient="vertical", command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            scrollbar.grid(row=0, column=1, sticky="ns")
            ttk.Button(laporan_window, text="Tutup", command=laporan_window.destroy).grid(row=1, column=0, columnspan=2, pady=10)
            laporan_window.grid_rowconfigure(0, weight=1)
            laporan_window.grid_columnconfigure(0, weight=1)
            laporan_window.focus_set()
            laporan_window.transient(self)
            laporan_window.grab_set()
            laporan_window.wait_window()
            laporan_window.destroy()  

            # Reset Form
            self.combo_bulan.set('')
            self.entry_tahun.delete(0, tk.END)
            self.combo_kategori.set('')

        # Tombol
        ttk.Button(self, text="📑 Tampilkan Laporan", command=show_laporan).grid(row=4, column=0, padx=10, pady=20, sticky="e")
        ttk.Button(self, text="⬅️ Kembali ke Menu Utama",
                   command=lambda: controller.show_frame("Menu")).grid(row=4, column=1, padx=10, pady=20, sticky="w")

        # Biar grid lebih rata
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)  
