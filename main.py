import tkinter as tk
from tkinter import ttk
import sqlite3
from tkinter import messagebox
from datetime import date

from pencatatan import PencatatanPage 
from pelaporan import PelaporanPage
from grafik import GrafikPage
from pajak import PajakPage       
from penggajian import PenggajianPage 

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Prototipe SIA")
        
        # Inisialisasi Database
        self.initialize_db()

        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry(f"{width}x{height}")

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self.frames = {}

        for F, PageClass in {
            "Menu": tk.Frame,
            "Pencatatan": PencatatanPage,
            "Pelaporan": PelaporanPage,
            "Grafik": GrafikPage,
            "Pajak": PajakPage,        
            "Penggajian": PenggajianPage, 
        }.items():
            if F == "Menu":
                menu_frame = tk.Frame(container)
                self.frames[F] = menu_frame
            else:
                frame = PageClass(container, self)
                self.frames[F] = frame

            self.frames[F].grid(row=0, column=0, sticky="nsew")

        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 15), padding=10)

        # Frame Menu 
        menu_frame = self.frames["Menu"]
        menu_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Label(menu_frame, text="Menu Utama", font=("Helvetica", 30)).pack(pady=25)
        ttk.Button(menu_frame, text="📒 Pencatatan Transaksi", width=30,
                   command=lambda: self.show_frame("Pencatatan")).pack(pady=10)
        ttk.Separator(menu_frame, orient='horizontal').pack(fill='x', padx=50, pady=10)
        ttk.Button(menu_frame, text="📊 Laporan Keuangan", width=30,
                   command=lambda: self.show_frame("Pelaporan")).pack(pady=10)
        ttk.Button(menu_frame, text="📈 Analisis Keuangan", width=30,
                   command=lambda: self.show_frame("Grafik")).pack(pady=10)
        ttk.Separator(menu_frame, orient='horizontal').pack(fill='x', padx=50, pady=10)
        ttk.Button(menu_frame, text="🧾 Manajemen Pajak", width=30,
                   command=lambda: self.show_frame("Pajak")).pack(pady=10)
        ttk.Button(menu_frame, text="💵 Manajemen Penggajian", width=30,
                   command=lambda: self.show_frame("Penggajian")).pack(pady=10)
        ttk.Separator(menu_frame, orient='horizontal').pack(fill='x', padx=50, pady=10)
        ttk.Button(menu_frame, text="Keluar", width=30,
                   command=self.quit).pack(pady=20)

        self.show_frame("Menu")

    def initialize_db(self):
        conn = sqlite3.connect('data_keuangan.db')
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS transaksi (
                            id TEXT PRIMARY KEY,
                            tanggal TEXT,
                            kategori TEXT,
                            keterangan TEXT,
                            jumlah INTEGER)''')
                            
        c.execute('''CREATE TABLE IF NOT EXISTS pajak (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tanggal TEXT,
                    jenis_pajak TEXT,
                    jumlah INTEGER)''')
                    
        c.execute('''CREATE TABLE IF NOT EXISTS penggajian (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tanggal TEXT,
                    nama_karyawan TEXT,
                    gaji_bersih INTEGER)''')

        conn.commit()
        conn.close()

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        if hasattr(frame, 'load_transaksi_data'):
            frame.load_transaksi_data()

if __name__ == "__main__":
    app = App()
    app.mainloop()
