import tkinter as tk
from tkinter import ttk


class MenuStaffPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(self, text="Menu Utama").grid(column=0, row=0, padx=10, pady=10, columnspan=2)

        ttk.Button(self, text="Produk").grid(column=0, row=1, padx=10, pady=10)

        ttk.Button(self, text="Transaksi").grid(column=1, row=1, padx=10, pady=10)


        