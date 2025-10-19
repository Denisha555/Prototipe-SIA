import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from function.bulan_map import bulan_map

class GrafikPendapatanPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="📊 Grafik Pendapatan", font=("Helvetica", 18, "bold")).pack(pady=15)

        # Frame filter (bulan & tahun)
        filter_frame = ttk.Frame(self)
        filter_frame.pack(pady=5)

        ttk.Label(filter_frame, text="Bulan:").grid(row=0, column=0, padx=5)
        self.combo_bulan = ttk.Combobox(filter_frame, state="readonly", values=list(bulan_map.keys()), width=15)
        self.combo_bulan.grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Tahun:").grid(row=0, column=2, padx=5)
        self.entry_tahun = ttk.Entry(filter_frame, width=10)
        self.entry_tahun.grid(row=0, column=3, padx=5)

        ttk.Button(filter_frame, text="Tampilkan Grafik", command=self.tampilkan_grafik).grid(row=0, column=4, padx=10)

        ttk.Button(self, text="Kembali ke Menu Utama",
                   command=lambda: controller.show_frame("Menu Utama Manager")).pack(pady=10)

        # Canvas untuk grafik
        self.figure = plt.Figure(figsize=(8, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Default bulan & tahun
        today = datetime.now()
        current_year = today.strftime("%Y")
        current_month_num = today.strftime("%m")

        for name, num in bulan_map.items():
            if num == current_month_num:
                self.combo_bulan.set(name)
                break
        self.entry_tahun.insert(0, current_year)

    def tampilkan_grafik(self):
        bulan = self.combo_bulan.get()
        tahun = self.entry_tahun.get()

        if not bulan or not tahun.isdigit():
            messagebox.showerror("Error", "Pilih bulan dan tahun yang valid!")
            return

        bulan_angka = bulan_map.get(bulan)
        if not bulan_angka:
            messagebox.showerror("Error", "Nama bulan tidak valid.")
            return

        try:
            conn = sqlite3.connect("data_keuangan.db")
            c = conn.cursor()

            # Query sesuai tabelmu
            c.execute("""
                SELECT tanggal, SUM(total) AS total_harian
                FROM transaksi_penjualan
                WHERE strftime('%m', tanggal) = ? AND strftime('%Y', tanggal) = ?
                GROUP BY tanggal
                ORDER BY tanggal ASC
            """, (bulan_angka, tahun))

            data = c.fetchall()
            conn.close()

            if not data:
                messagebox.showinfo("Info", f"Tidak ada data penjualan untuk {bulan} {tahun}.")
                self.ax.clear()
                self.canvas.draw()
                return

            # Ekstrak tanggal & total
            tanggal = [int(d[0][-2:]) for d in data]  # ambil tanggal (1-31)
            total = [d[1] for d in data]

            # Gambar grafik batang
            self.ax.clear()
            self.ax.bar(tanggal, total, color="#007ACC")
            self.ax.set_title(f"Grafik Penjualan per Tanggal ({bulan} {tahun})", fontsize=12, fontweight="bold")
            self.ax.set_xlabel("Tanggal")
            self.ax.set_ylabel("Total Penjualan (Rp)")
            self.ax.grid(axis='y', linestyle='--', alpha=0.7)
            self.canvas.draw()

        except sqlite3.Error as e:
            messagebox.showerror("Error Database", f"Gagal mengambil data: {e}")
