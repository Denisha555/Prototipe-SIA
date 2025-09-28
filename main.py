import tkinter as tk
from tkinter import ttk

from pencatatan import PencatatanPage 
from pelaporan import PelaporanPage
from grafik import GrafikPage

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Prototipe SIA")
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry(f"{width}x{height}")

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        self.frames = {}

        for F, PageClass in {
            "Menu": tk.Frame,
            "Pencatatan": PencatatanPage,
            "Pelaporan": PelaporanPage,
            "Grafik": GrafikPage,
        }.items():
            frame = PageClass(container, self) if F != "Menu" else PageClass(container)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 15), padding=10)

        # Frame Menu
        ttk.Label(self.frames["Menu"], text="Menu Utama", font=("Helvetica", 30)).pack(pady=25)
        ttk.Button(self.frames["Menu"], text="Pencatatan Transaksi",
                   command=lambda: self.show_frame("Pencatatan")).pack(pady=10)
        ttk.Button(self.frames["Menu"], text="Laporan Keuangan",
                   command=lambda: self.show_frame("Pelaporan")).pack(pady=10)
        ttk.Button(self.frames["Menu"], text="Analisis Keuangan",
                   command=lambda: self.show_frame("Grafik")).pack(pady=10)
        ttk.Button(self.frames["Menu"], text="Keluar", command=self.quit).pack(pady=10)

        self.show_frame("Menu")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

if __name__ == "__main__":
    app = App()
    app.mainloop()
