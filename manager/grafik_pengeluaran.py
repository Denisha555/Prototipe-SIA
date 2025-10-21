import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from function.bulan_map import bulan_map


class GrafikPengeluaranPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # ===============================
        # STYLE
        # ===============================
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Helvetica", 18, "bold"))
        style.configure("Primary.TButton", font=("Helvetica", 11, "bold"), padding=8)
        style.configure("Danger.TButton", font=("Helvetica", 11, "bold"), padding=8)
        style.configure("Filter.TLabel", font=("Helvetica", 10))

        # ===============================
        # JUDUL
        # ===============================
        ttk.Label(self, text="📊 Grafik Pengeluaran", style="Title.TLabel").pack(pady=(20, 10))

        # ===============================
        # FILTER BULAN & TAHUN
        # ===============================
        filter_frame = ttk.Frame(self)
        filter_frame.pack(pady=5)

        ttk.Label(filter_frame, text="Bulan:", style="Filter.TLabel").grid(row=0, column=0, padx=5)
        self.combo_bulan = ttk.Combobox(filter_frame, state="readonly", values=list(bulan_map.keys()), width=15)
        self.combo_bulan.grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Tahun:", style="Filter.TLabel").grid(row=0, column=2, padx=5)
        self.entry_tahun = ttk.Entry(filter_frame, width=10)
        self.entry_tahun.grid(row=0, column=3, padx=5)

        ttk.Button(filter_frame, text="Tampilkan Grafik",
                   command=self.tampilkan_grafik).grid(row=0, column=4, padx=10)

        # ===============================
        # TOMBOL KEMBALI
        # ===============================
        ttk.Button(self, text="Kembali ke Menu Utama",
                   command=lambda: controller.show_frame("Menu Utama Manager")).pack(pady=10)

        # ===============================
        # CANVAS MATPLOTLIB
        # ===============================
        self.figure = plt.Figure(figsize=(8, 4.5), dpi=100)
        self.ax = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.canvas.draw()

        # ===============================
        # DEFAULT NILAI BULAN & TAHUN
        # ===============================
        today = datetime.now()
        current_year = today.strftime("%Y")
        current_month_num = today.strftime("%m")

        for name, num in bulan_map.items():
            if num == current_month_num:
                self.combo_bulan.set(name)
                break
        self.entry_tahun.insert(0, current_year)

        self.tampilkan_grafik()

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

            # ===============================
            # QUERY: TOTAL PENGELUARAN PER TANGGAL
            # ===============================
            c.execute("""
                SELECT tanggal, SUM(nominal) AS total_harian
                FROM transaksi_kas_keluar
                WHERE strftime('%m', tanggal) = ? AND strftime('%Y', tanggal) = ?
                GROUP BY tanggal
                ORDER BY tanggal ASC
            """, (bulan_angka, tahun))

            data = c.fetchall()
            conn.close()

            self.ax.clear()

            if not data:
                self.ax.axis('off')
                self.ax.text(0.5, 0.5, f"Tidak ada data pengeluaran untuk {bulan} {tahun}.",
                             ha='center', va='center', fontsize=11, color='gray')
                self.canvas.draw()
                return

            # ===============================
            # GRAFIK BAR PENGELUARAN
            # ===============================
            tanggal = [int(d[0][-2:]) for d in data]  # ambil tanggal (1–31)
            total = [d[1] for d in data]

            bars = self.ax.bar(tanggal, total, color="#D9534F")

            # Tambahkan label Rp di atas batang
            for bar in bars:
                height = bar.get_height()
                formatted_height = f"{height:,.0f}".replace(",", "#").replace(".", ",").replace("#", ".")
                self.ax.text(bar.get_x() + bar.get_width()/2, height + max(total)*0.02,
                             f"Rp{formatted_height}", ha='center', va='bottom', fontsize=8)

            total_bulan = sum(total)
            formatted_total_bulan = f"{total_bulan:,.0f}".replace(",", "#").replace(".", ",").replace("#", ".")

            self.ax.set_title(f"Grafik Pengeluaran per Tanggal ({bulan} {tahun})", fontsize=13, fontweight="bold")
            self.ax.set_xlabel("Tanggal", fontsize=10)
            self.ax.set_ylabel("Total Pengeluaran (Rp)", fontsize=10)
            self.ax.grid(axis='y', linestyle='--', alpha=0.6)
            self.ax.set_xticks(tanggal)

            self.ax.set_xlim(min(tanggal) - 1, max(tanggal) + 1)
            self.ax.set_ylim(0, max(total) * 1.2)

            # Tampilkan total keseluruhan di bawah grafik
            self.ax.text(0.5, -0.2, f"Total Pengeluaran Bulan Ini: Rp{formatted_total_bulan}",
                         transform=self.ax.transAxes, ha='center', fontsize=10, fontweight="bold", color="#D9534F")

            self.canvas.draw()

        except sqlite3.Error as e:
            messagebox.showerror("Error Database", f"Gagal mengambil data: {e}")


