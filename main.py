import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Prototipe SIA")
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.geometry(f"{width}x{height}")

ttk.Label(root, text="Menu Utama", font=("Helvetica", 24)).pack(pady=20)

ttk.Button(root, text="Pencatatan", width=20).pack(pady=10)
ttk.Button(root, text="Laporan", width=20).pack(pady=10)
ttk.Button(root, text="Grafik", width=20).pack(pady=10)

root.mainloop()