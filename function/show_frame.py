import tkinter as tk
from pencatatan import PencatatanPage
from pelaporan import PelaporanPage
from grafik import GrafikPage
from pajak import PajakPage
from penggajian import PenggajianPage
from staff.menu_staff import MenuStaffPage
from manager.menu_manager import MenuManagerPage


def show_frame(self, name):
        if name not in self.frames:
            PageClass = {
                "Menu Utama Staff": MenuStaffPage,
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