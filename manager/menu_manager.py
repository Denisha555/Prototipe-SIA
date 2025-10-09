import tkinter as tk
from tkinter import ttk

class MenuManagerPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ttk.Label(self, text="Menu Utama").grid(column=0, row=0, padx=10, pady=10)

        ttk.Button(self, text="Laporan", command=lambda: controller.show_frame("Input Produk")).grid(column=0, row=1, padx=50, pady=60, sticky="nsew")

        ttk.Button(self, text="Pembelian", command=lambda: controller.show_frame("Input Transaksi")).grid(column=1, row=1, padx=50, pady=60, sticky="nsew")

        ttk.Button(self, text="Pengeluaran Kas", command=lambda: controller.show_frame("Input Transaksi")).grid(column=0, row=2, padx=50, pady=60, sticky="nsew")

        ttk.Button(self, text="Pemasukkan Kas", command=lambda: controller.show_frame("Input Transaksi")).grid(column=1, row=2, padx=50, pady=60, sticky="nsew")

        ttk.Button(self, text="Grafik", command=lambda: controller.show_frame("Input Transaksi")).grid(column=1, row=1, padx=50, pady=60, sticky="nsew")




        