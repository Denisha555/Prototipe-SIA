import tkinter as tk
from tkinter import ttk


class MenuStaffPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # 🌈 Styling umum
        style = ttk.Style()
        style.configure("TFrame")
        style.configure("Title.TLabel", font=("Helvetica", 20, "bold"))
        style.configure("Menu.TButton",
                        font=("Helvetica", 13, "bold"),
                        padding=15)
        style.configure("Danger.TButton",
                        font=("Helvetica", 12, "bold"),
                        padding=12,
                        foreground="black",
                        background="#dc3545",)

        # 🔲 Layout utama
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=3)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 🏷️ Judul di atas
        ttk.Label(self, text="🏢 Menu Utama Staff", style="Title.TLabel").grid(
            column=0, row=0, columnspan=2, pady=(10, 5)
        )

        # 🔘 Tombol-tombol utama (di tengah)
        menu_frame = ttk.Frame(self)
        menu_frame.grid(column=0, row=1, columnspan=2, pady=20, padx=40, sticky="nsew")
        menu_frame.grid_columnconfigure((0, 1), weight=1)
        menu_frame.grid_rowconfigure((0, 1), weight=1)

        ttk.Button(menu_frame, text="🧾 Kelola Jasa", style="Menu.TButton",
                   command=lambda: controller.show_frame("Input Jasa Staff")).grid(
            column=0, row=0, padx=20, pady=20, sticky="nsew"
        )

        ttk.Button(menu_frame, text="🛒 Input Penjualan", style="Menu.TButton",
                   command=lambda: controller.show_frame("Input Penjualan")).grid(
            column=1, row=0, padx=20, pady=20, sticky="nsew"
        )

        ttk.Button(menu_frame, text="💰 Input Pengeluaran", style="Menu.TButton",
                   command=lambda: controller.show_frame("Input Kas Keluar")).grid(
            column=0, row=1, padx=20, pady=20, sticky="nsew"
        )

        ttk.Button(menu_frame, text="✔️ Input Penyesuaian", style="Menu.TButton",
                   command=lambda: controller.show_frame("Penyesuaian Staff")).grid(
            column=1, row=1, padx=20, pady=20, sticky="nsew"
        )

        ttk.Button(menu_frame, text="Kembali Ke Login", style="Danger.TButton",
                   command=lambda: controller.show_frame("Login")).grid(
            column=0, row=2, columnspan=2, padx=450, pady=20, sticky="nsew"
        )

        # ✨ Footer kosong untuk spasi bawah
        ttk.Label(self, text="").grid(column=0, row=2, columnspan=2, pady=20)


