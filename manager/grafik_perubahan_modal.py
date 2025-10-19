import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

try:
    from function.bulan_map import bulan_map
except ImportError:
    bulan_map = {
        "Januari": "01", "Februari": "02", "Maret": "03", 
        "April": "04", "Mei": "05", "Juni": "06",
        "Juli": "07", "Agustus": "08", "September": "09",
        "Oktober": "10", "November": "11", "Desember": "12"
    }

class GrafikModalPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="📈 Grafik Perubahan Modal Tahunan", font=("Helvetica", 18, "bold")).pack(pady=15)

        # Frame filter
        filter_frame = ttk.Frame(self)
        filter_frame.pack(pady=5)

        ttk.Label(filter_frame, text="Tahun:").grid(row=0, column=0, padx=5)
        self.entry_tahun = ttk.Entry(filter_frame, width=10)
        self.entry_tahun.grid(row=0, column=1, padx=5)

        ttk.Button(filter_frame, text="Tampilkan Grafik", command=self.tampilkan_grafik).grid(row=0, column=2, padx=10)

        ttk.Button(self, text="Kembali ke Menu Utama",
                   command=lambda: controller.show_frame("Menu Utama Manager")).pack(pady=10)

        # Canvas untuk grafik
        self.figure = plt.Figure(figsize=(8, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Default tahun
        current_year = datetime.now().strftime("%Y")
        self.entry_tahun.insert(0, current_year)
        
        # Tampilkan grafik default saat pertama kali dimuat
        self.tampilkan_grafik()

    def tampilkan_grafik(self):
        tahun = self.entry_tahun.get()

        if not tahun.isdigit() or len(tahun) != 4:
            messagebox.showerror("Error", "Masukkan tahun yang valid (contoh: 2023)!")
            return

        try:
            conn = sqlite3.connect("data_keuangan.db")
            c = conn.cursor()
            c.execute("""
                SELECT strftime('%m', tanggal), modal_akhir 
                FROM rekap_modal
                WHERE strftime('%Y', tanggal) = ?
                ORDER BY tanggal ASC
            """, (tahun,))

            data = c.fetchall()
            conn.close()

            if not data:
                messagebox.showinfo("Info", f"Tidak ada data perubahan modal yang terekam untuk tahun {tahun}.\nPastikan Laporan Perubahan Modal sudah dibuat untuk bulan-bulan di tahun tersebut.")
                self.ax.clear()
                self.canvas.draw()
                return

            bulan_terisi = {v: k for k, v in bulan_map.items()} 
            
            # Dictionary untuk menampung modal akhir per bulan
            modal_akhir_bulanan = {} 
            
            for bulan_num, modal_akhir in data:
                modal_akhir_bulanan[bulan_num] = modal_akhir

            # Urutan Bulan (dari 01 sampai 12)
            bulan_labels_order = sorted(list(bulan_map.values()))
            
            labels_plot = [bulan_terisi.get(num, num) for num in bulan_labels_order]
            values_plot = [modal_akhir_bulanan.get(num, 0) for num in bulan_labels_order] 

            self.ax.clear()
            
            self.ax.plot(labels_plot, values_plot, marker='o', linestyle='-', color='#8B4513', linewidth=2, label="Modal Akhir")
            
            for i, val in enumerate(values_plot):
                # Hanya tampilkan label untuk nilai > 0
                if val > 0:
                    self.ax.text(labels_plot[i], val, f'Rp{int(val):,}', ha='center', va='bottom', fontsize=8)

            self.ax.set_title(f"Grafik Perubahan Modal Pemilik Tahun {tahun}", fontsize=12, fontweight="bold")
            self.ax.set_xlabel("Bulan")
            self.ax.set_ylabel("Saldo Modal (Rp)")
            
            # Rotasi label X agar tidak tumpang tindih
            plt.setp(self.ax.get_xticklabels(), rotation=45, ha="right")
            
            self.ax.grid(axis='y', linestyle='--', alpha=0.7)
            self.ax.ticklabel_format(axis='y', style='plain')
            self.figure.tight_layout(pad=3.0)
            self.canvas.draw()

        except sqlite3.Error as e:
            messagebox.showerror("Error Database", f"Gagal mengambil data Modal: {e}")
