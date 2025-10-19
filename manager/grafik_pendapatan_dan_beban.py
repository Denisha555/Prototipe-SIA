import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from function.bulan_map import bulan_map

class GrafikPendapatanDanBebanPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="📊 Grafik Pendapatan dan Beban", font=("Helvetica", 18, "bold")).pack(pady=15)

        # Frame filter
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
        self.figure = plt.Figure(figsize=(8, 4.5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.axis('off')
        self.ax.text(0.5, 0.5, "Belum ada grafik.\nPilih bulan dan tahun lalu tekan 'Tampilkan Grafik'.",
                     ha='center', va='center', fontsize=11, color='gray')

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas.draw()

        # Default bulan & tahun
        today = datetime.now()
        self.entry_tahun.insert(0, today.strftime("%Y"))
        current_month_num = today.strftime("%m")
        for name, num in bulan_map.items():
            if num == current_month_num:
                self.combo_bulan.set(name)
                break

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

            # Ambil data pendapatan (akun 4xx)
            c.execute("""
                SELECT tanggal, SUM(kredit) AS total_pendapatan
                FROM jurnal_umum_detail
                WHERE kode_akun LIKE '4%' 
                AND strftime('%m', tanggal)=? AND strftime('%Y', tanggal)=?
                GROUP BY tanggal
            """, (bulan_angka, tahun))
            pendapatan_data = dict(c.fetchall())

            # Ambil data beban (akun 5xx)
            c.execute("""
                SELECT tanggal, SUM(debit) AS total_beban
                FROM jurnal_umum_detail
                WHERE kode_akun LIKE '5%' 
                AND strftime('%m', tanggal)=? AND strftime('%Y', tanggal)=?
                GROUP BY tanggal
            """, (bulan_angka, tahun))
            beban_data = dict(c.fetchall())

            conn.close()

            # Gabungkan tanggal dari dua sumber
            semua_tanggal = sorted(set(
                [int(t[-2:]) for t in pendapatan_data.keys()] +
                [int(t[-2:]) for t in beban_data.keys()]
            ))

            if not semua_tanggal:
                self.ax.clear()
                self.ax.axis('off')
                self.ax.text(0.5, 0.5, f"Tidak ada data untuk {bulan} {tahun}.",
                             ha='center', va='center', fontsize=11, color='gray')
                self.canvas.draw()
                return

            # Siapkan data
            pendapatan = [pendapatan_data.get(f"{tahun}-{bulan_angka}-{str(t).zfill(2)}", 0) for t in semua_tanggal]
            beban = [beban_data.get(f"{tahun}-{bulan_angka}-{str(t).zfill(2)}", 0) for t in semua_tanggal]

            # Gambar grafik batang berdampingan
            self.ax.clear()
            bar_width = 0.4
            x = range(len(semua_tanggal))
            self.ax.bar([i - bar_width/2 for i in x], pendapatan, width=bar_width, color="#5cb85c", label="Pendapatan")
            self.ax.bar([i + bar_width/2 for i in x], beban, width=bar_width, color="#d9534f", label="Beban")

            # Tambah label
            self.ax.set_xticks(list(x))
            self.ax.set_xticklabels(semua_tanggal)
            self.ax.set_xlabel("Tanggal")
            self.ax.set_ylabel("Jumlah (Rp)")
            self.ax.set_title(f"Pendapatan vs Beban per Tanggal ({bulan} {tahun})", fontsize=13, fontweight="bold")
            self.ax.legend()
            self.ax.grid(axis='y', linestyle='--', alpha=0.6)

            # Tampilkan total
            total_pendapatan = sum(pendapatan)
            total_beban = sum(beban)
            laba_rugi = total_pendapatan - total_beban
            warna_laba = "#5cb85c" if laba_rugi >= 0 else "#d9534f"

            self.ax.text(0.5, -0.22,
                         f"Total Pendapatan: Rp{total_pendapatan:,.0f}   |   Total Beban: Rp{total_beban:,.0f}   |   Laba/Rugi: Rp{laba_rugi:,.0f}",
                         transform=self.ax.transAxes, ha='center', fontsize=10, color=warna_laba, fontweight="bold")

            self.canvas.draw()

        except sqlite3.Error as e:
            messagebox.showerror("Error Database", f"Gagal mengambil data: {e}")
