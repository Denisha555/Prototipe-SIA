import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry

class PencatatanPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        ttk.Label(self, text="Halaman Pencatatan", font=("Helvetica", 18)).pack(pady=20)

        ttk.Label(self, text="Tanggal").pack()
        self.entry_tanggal = DateEntry(self, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.entry_tanggal.pack()

        ttk.Label(self, text="Kategori").pack()
        # menggunakan combobox untuk kategori
        self.entry_kategori = ttk.Combobox(self, values=["Pemasukan", "Pengeluaran"])
        self.entry_kategori.pack()

        ttk.Label(self, text="Jumlah").pack()
        self.entry_jumlah = ttk.Entry(self)
        self.entry_jumlah.pack()

        ttk.Button(self, text="Kembali ke Menu", 
                   command=lambda: controller.show_frame("Menu")).pack(pady=10)
