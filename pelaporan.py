import tkinter as tk
from tkinter import ttk

class PelaporanPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        ttk.Label(self, text="Halaman Pelaporan", font=("Helvetica", 18)).pack(pady=20)

        ttk.Button(self, text="Kembali ke Menu", 
                   command=lambda: controller.show_frame("Menu")).pack(pady=10)
