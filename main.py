import tkinter as tk
from tkinter import ttk
from function.initialize_db import initialize_db

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
                   command=lambda: show_frame(self, "Pencatatan")).pack(pady=10)
        
        ttk.Separator(menu_frame, orient='horizontal').pack(fill='x', padx=50, pady=10)

        ttk.Button(menu_frame, text="📊 Laporan Keuangan", width=30,
                   command=lambda: show_frame(self, "Pelaporan")).pack(pady=10)
        ttk.Button(menu_frame, text="📈 Analisis Keuangan", width=30,
                   command=lambda: show_frame(self, "Grafik")).pack(pady=10)

        ttk.Separator(menu_frame, orient='horizontal').pack(fill='x', padx=50, pady=10)

        ttk.Button(menu_frame, text="🧾 Manajemen Pajak", width=30,
                   command=lambda: show_frame(self, "Pajak")).pack(pady=10)
        ttk.Button(menu_frame, text="💵 Manajemen Penggajian", width=30,
                   command=lambda: show_frame(self, "Penggajian")).pack(pady=10)
        
        ttk.Separator(menu_frame, orient='horizontal').pack(fill='x', padx=50, pady=10)

        ttk.Button(menu_frame, text="Keluar", width=30,
                   command=self.quit).pack(pady=20)

        # # Tampilkan menu pertama kali
        # self.show_frame("Menu")


if __name__ == "__main__":
    app = App()
    app.mainloop()
