import tkinter as tk
from tkinter import ttk
from function.initialize_db import initialize_db
from pencatatan import PencatatanPage
from pelaporan import PelaporanPage
from grafik import GrafikPage
from pajak import PajakPage
from penggajian import PenggajianPage
from staff.menu_staff import MenuStaffPage
from manager.menu_manager import MenuManagerPage
from staff.jasa import ProdukPage
from staff.penjualan import TransaksiPage

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Prototype SIA")

        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry(f"{width}x{height}")

        # Container utama
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.frames = {}

        # Frame Menu (dibuat langsung)
        menu_frame = tk.Frame(self.container)
        self.frames["Menu"] = menu_frame
        menu_frame.grid(row=0, column=0, sticky="nsew")

        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 15), padding=10)

        # Isi menu
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

        # Tampilkan menu pertama kali
        self.show_frame("Menu")

    def show_frame(self, name):
        if name not in self.frames:
            PageClass = {
                "Menu Utama Staff": MenuStaffPage,
                "Input Produk": ProdukPage,
                "Input Transaksi": TransaksiPage,
                "Menu Utama Manger": MenuManagerPage,
                "Pencatatan": PencatatanPage,
                "Pelaporan": PelaporanPage,
                "Grafik": GrafikPage,
                "Pajak": PajakPage,        
                "Penggajian": PenggajianPage, 
            }[name]
            frame = PageClass(self.container, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        frame = self.frames[name]
        frame.tkraise()

        if hasattr(frame, 'load_transaksi_data'):
            frame.load_transaksi_data()


if __name__ == "__main__":
    app = App()
    app.mainloop()
