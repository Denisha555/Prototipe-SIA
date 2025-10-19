import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

from function.initialize_db import initialize_db
from manager.grafik_komposisi_aset import GrafikKomposisiAsetPage
from manager.grafik_pengeluaran import GrafikPengeluaranPage
from manager.grafik_perubahan_modal import GrafikModalPage
from manager.jurnal_umum import JurnalUmumPage
from manager.buku_besar import BukuBesarPage
from manager.laporan_arus_kas import LaporanArusKasPage
from manager.neraca import NeracaPage
from manager.neraca_saldo import NeracaSaldoPage
from manager.neraca_saldo_setelah_penutupan import NeracaSaldoSetelahPenutupanPage
from manager.worksheet import WorksheetPage
from manager.laba_rugi import LabaRugiPage
from manager.jurnal_penutup import JurnalPenutupPage
from manager.jurnal_penyesuaian import JurnalPenyesuaianPage
from manager.penyesuaian import PenyesuaianPage as PenyesuaianPageManager
from manager.grafik_pendapatan import GrafikPendapatanPage
from staff.penyesuaian import PenyesuaianPage as PenyesuaianPageStaff
from manager.laporan_perubahan_modal import LaporanPerubahanModalPage
from pencatatan import PencatatanPage
from pelaporan import PelaporanPage
from grafik import GrafikPage
from pajak import PajakPage
from penggajian import PenggajianPage
from staff.menu_staff import MenuStaffPage
from manager.menu_manager import MenuManagerPage
from staff.kas_keluar import KasKeluarPage as KasKeluarPageStaff
from manager.kas_keluar import KasKeluarPage as KasKeluarPageManager
from staff.jasa import JasaPage as JasaPageStaff
from manager.jasa import JasaPage as JasaPageManager
from staff.penjualan import PenjualanPage as PenjualanPageStaff
from manager.penjualan import PenjualanPage as PenjualanPageManager
from manager.grafik_pendapatan_dan_beban import GrafikPendapatanDanBebanPage



class LoginPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Prototype SIA")

        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry(f"{width}x{height}")

        initialize_db(self)

        # Container utama untuk frame-frame
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Tampilkan login frame dulu
        login_frame = tk.Frame(self.container)
        self.frames["Login"] = login_frame
        login_frame.grid(row=0, column=0, sticky="nsew")

        login_frame.grid_columnconfigure(0, weight=1)
        login_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(login_frame, text="🔑 Login", font=("Helvetica", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=15)

        ttk.Label(login_frame, text="Username:").grid(row=1, column=0, pady=5, padx=5, sticky="e")
        self.entry_username = ttk.Entry(login_frame, width=25)
        self.entry_username.grid(row=1, column=1, pady=5, sticky="w")
        ttk.Label(login_frame, text="Password:").grid(row=2, column=0, pady=5, padx=5, sticky="e")
        self.entry_password = ttk.Entry(login_frame, show="*", width=25)
        self.entry_password.grid(row=2, column=1, pady=5, sticky="w")

        ttk.Button(login_frame, text="Login", command=self.login).grid(row=3, columnspan=2, pady=15)

        self.show_frame("Login")

    def show_frame(self, name):
        if name not in self.frames:
            PageClass = {
                "Menu Utama Staff": MenuStaffPage,
                "Input Jasa Staff": JasaPageStaff,
                "Input Penjualan": PenjualanPageStaff,
                "Input Kas Keluar": KasKeluarPageStaff,
                "Penyesuaian Staff": PenyesuaianPageStaff,
                "Menu Utama Manager": MenuManagerPage,
                "Input Edit Penjualan": PenjualanPageManager,
                "Input Edit Kas Keluar": KasKeluarPageManager,
                "Input Jasa Manager": JasaPageManager,
                "Jurnal Umum": JurnalUmumPage,
                "Buku Besar": BukuBesarPage,
                "Neraca Saldo": NeracaSaldoPage,
                "Neraca Saldo Setelah Penutupan": NeracaSaldoSetelahPenutupanPage,
                "Worksheet": WorksheetPage,
                "Laba Rugi": LabaRugiPage,
                "Laporan Perubahan Modal": LaporanPerubahanModalPage,
                "Neraca": NeracaPage,
                "Laporan Arus Kas": LaporanArusKasPage,
                "Jurnal Penutup": JurnalPenutupPage,
                "Penyesuaian Manager": PenyesuaianPageManager,
                "Jurnal Penyesuaian": JurnalPenyesuaianPage,
                "Grafik Pendapatan": GrafikPendapatanPage,
                "Grafik Komposisi Aset": GrafikKomposisiAsetPage,
                "Grafik Pengeluaran": GrafikPengeluaranPage,
                "Grafik Perubahan Modal": GrafikModalPage,
                "Grafik Pendapatan dan Beban": GrafikPendapatanDanBebanPage
                # "Pencatatan": PencatatanPage,
                # "Pelaporan": PelaporanPage,
                # "Grafik": GrafikPage,
                # "Pajak": PajakPage,        
                # "Penggajian": PenggajianPage, 
            }[name]
            frame = PageClass(self.container, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        frame = self.frames[name]
        frame.tkraise()

        if hasattr(frame, 'load_transaksi_data'):
            frame.load_transaksi_data()

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        conn = sqlite3.connect('data_keuangan.db')
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
        result = c.fetchone()
    
        if result:
            role = result[0]
            if role == "staff":
                self.show_frame("Menu Utama Staff")
            elif role == "manager":
                self.show_frame("Menu Utama Manager")
            messagebox.showinfo("Sukses", f"Login berhasil sebagai {role}.")
        else:
            messagebox.showerror("Gagal", "Username atau password salah.")

        self.entry_username.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)

        conn.close()


if __name__ == "__main__":
    app = LoginPage()
    app.mainloop()
