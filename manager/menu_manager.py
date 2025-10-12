import tkinter as tk
from tkinter import ttk

class MenuManagerPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        style = ttk.Style()
        style.configure("Menu.TButton", 
                        font=("Helvetica", 13, "bold"), 
                        padding=15, 
                        background="#007BFF",
                        foreground="black")
                        
        style.configure("Title.TLabel", font=("Helvetica", 20, "bold"))
        
        # Style untuk tombol yang kembali
        style.configure("Danger.TButton", 
                        font=("Helvetica", 12, "bold"), 
                        padding=10, 
                        background="#DC3545",
                        foreground="black") 
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        ttk.Label(self, text="🏛️ Menu Utama Manager", style="Title.TLabel").grid(
            column=0, row=0, padx=10, pady=20, columnspan=3
        )

        # FRAME MANAJEMEN DATA
        data_frame = ttk.LabelFrame(self, text="Manajemen Data", padding=15)
        data_frame.grid(column=0, row=1, padx=20, pady=10, sticky="nsew")
        data_frame.grid_columnconfigure(0, weight=1)
        
        row_data = 0
        ttk.Button(data_frame, text="✅ Jasa (Kelola Jasa)", style="Menu.TButton",
                   command=lambda: controller.show_frame("Input Jasa Manager")).grid(
                       column=0, row=row_data, padx=10, pady=10, sticky="ew"
                   )
        row_data += 1
        ttk.Button(data_frame, text="🛒 Penjualan (Kelola Penjualan)", style="Menu.TButton",
                   command=lambda: controller.show_frame("Input Edit Penjualan")).grid(
                       column=0, row=row_data, padx=10, pady=10, sticky="ew"
                   )
        
        row_data += 1
        ttk.Button(data_frame, text="🛒 Pembelian (Kelola Pembelian)", style="Menu.TButton",
                   command=lambda: controller.show_frame("Input Edit Pembelian")).grid(
                       column=0, row=row_data, padx=10, pady=10, sticky="ew"
                   )
        # Gaji & Pajak kalau ada

        # FRAME SIKLUS AKUNTANSI??
        siklus_frame = ttk.LabelFrame(self, text="Siklus Akuntansi", padding=15)
        siklus_frame.grid(column=1, row=1, padx=20, pady=10, sticky="nsew")
        siklus_frame.grid_columnconfigure(0, weight=1)
        
        row_siklus = 0
        ttk.Button(siklus_frame, text="📘 Jurnal Umum", style="Menu.TButton",
                   command=lambda: controller.show_frame("Jurnal Umum")).grid(
                       column=0, row=row_siklus, padx=10, pady=10, sticky="ew"
                   )
        row_siklus += 1
        ttk.Button(siklus_frame, text="📚 Buku Besar", style="Menu.TButton",
                   command=lambda: controller.show_frame("Buku Besar")).grid(
                       column=0, row=row_siklus, padx=10, pady=10, sticky="ew"
                   )
        row_siklus += 1
        ttk.Button(siklus_frame, text="📊 Neraca Saldo", style="Menu.TButton",
                   command=lambda: controller.show_frame("Neraca Saldo")).grid(
                       column=0, row=row_siklus, padx=10, pady=10, sticky="ew"
                   )
        row_siklus += 1
        ttk.Button(siklus_frame, text="📝 Jurnal Penyesuaian", style="Menu.TButton",
                   command=lambda: controller.show_frame("Jurnal Penyesuaian")).grid(
                       column=0, row=row_siklus, padx=10, pady=10, sticky="ew"
                   )
        row_siklus += 1
        ttk.Button(siklus_frame, text="🗂️ Kertas Kerja (Worksheet)", style="Menu.TButton",
                   command=lambda: controller.show_frame("Worksheet")).grid(
                       column=0, row=row_siklus, padx=10, pady=10, sticky="ew"
                   )

        # FRAME LAPORAN & PENUTUP
        laporan_frame = ttk.LabelFrame(self, text="Laporan & Penutupan", padding=15)
        laporan_frame.grid(column=2, row=1, padx=20, pady=10, sticky="nsew")
        laporan_frame.grid_columnconfigure(0, weight=1)
        
        row_laporan = 0
        ttk.Button(laporan_frame, text="📈 Laporan Laba Rugi", style="Menu.TButton",
                   command=lambda: controller.show_frame("Laba Rugi")).grid(
                       column=0, row=row_laporan, padx=10, pady=10, sticky="ew"
                   )
        row_laporan += 1
        ttk.Button(laporan_frame, text="💼 Neraca", style="Menu.TButton",
                   command=lambda: controller.show_frame("Neraca")).grid(
                       column=0, row=row_laporan, padx=10, pady=10, sticky="ew"
                   )
        row_laporan += 1
        ttk.Button(laporan_frame, text="🔄 Jurnal Penutup", style="Menu.TButton",
                   command=lambda: controller.show_frame("Jurnal Penutup")).grid(
                       column=0, row=row_laporan, padx=10, pady=10, sticky="ew"
                   )
        row_laporan += 1
        ttk.Button(laporan_frame, text="🔒 Neraca Saldo Setelah Penutupan", style="Menu.TButton",
                   command=lambda: controller.show_frame("Neraca Saldo Setelah Penutupan")).grid(
                       column=0, row=row_laporan, padx=10, pady=10, sticky="ew"
                   )
        
        # KEMBALI
        ttk.Button(self, text="◀️ Kembali ke Login", 
                   command=lambda: controller.show_frame("Login"), style="Danger.TButton").grid(
                       column=0, row=2, padx=20, pady=20, columnspan=3
                   )