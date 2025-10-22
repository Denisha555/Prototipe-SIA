import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter
from manager.laporan_perubahan_modal import hitung_modal

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

    def format_rupiah_titik(self, nominal):
        formatted = f"{int(nominal):,.0f}".replace(",", "#").replace(".", ",").replace("#", ".")
        return f"Rp{formatted}"

    def format_jutaan(self, x, pos):
        if x == 0:
            return '0'
        formatted = f'{x*1e-6:,.0f}'.replace(",", "#").replace(".", ",").replace("#", ".") 
        return formatted


    def tampilkan_grafik(self):
        tahun = self.entry_tahun.get()

        if not tahun.isdigit() or len(tahun) != 4:
            messagebox.showerror("Error", "Masukkan tahun yang valid (contoh: 2023)!")
            return

        try:
            conn = sqlite3.connect("data_keuangan.db")
            c = conn.cursor()
            
            current_month_num = datetime.now().strftime("%m")
            current_year = datetime.now().strftime("%Y")
            
            bulan_labels_order = sorted(list(bulan_map.values())) # ['01', '02', ..., '12']

            for bulan_num in bulan_labels_order:
                if tahun == current_year and bulan_num > current_month_num:
                    continue 

                # Cek apakah data bulan tersebut sudah ada di rekap_modal
                c.execute("""
                    SELECT 1 
                    FROM rekap_modal
                    WHERE strftime('%Y', tanggal) = ? AND strftime('%m', tanggal) = ?
                """, (tahun, bulan_num))
                
                if c.fetchone() is None:
                    hitung_modal(bulan_num, tahun)
            
            conn.commit()
            conn.close()
            
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
                messagebox.showinfo("Info", f"Tidak ada data perubahan modal yang terekam untuk tahun {tahun}.")
                self.ax.clear()
                self.ax.set_title(f"Grafik Perubahan Modal Pemilik Tahun {tahun}", fontsize=12, fontweight="bold")
                self.ax.axis('off')
                self.ax.text(0.5, 0.5, "Data tidak tersedia.", ha='center', va='center', fontsize=11, color='gray')
                self.canvas.draw()
                return

            bulan_terisi = {v: k for k, v in bulan_map.items()} 
            
            modal_akhir_bulanan = {} 
            
            for bulan_num, modal_akhir in data:
                modal_akhir_bulanan[bulan_num] = modal_akhir

            # Urutan Bulan (dari 01 sampai 12)
            bulan_labels_order = sorted(list(bulan_map.values()))
            
            labels_plot = [bulan_terisi.get(num, num) for num in bulan_labels_order]
            values_plot = [modal_akhir_bulanan.get(num, 0) for num in bulan_labels_order] 
            
            if tahun == current_year:
                max_index = int(current_month_num)
                labels_plot = labels_plot[:max_index]
                values_plot = values_plot[:max_index]

            self.ax.clear()
            
            self.ax.plot(labels_plot, values_plot, marker='o', linestyle='-', color='#8B4513', linewidth=2, label="Modal Akhir")
            
            formatter = FuncFormatter(self.format_jutaan)
            self.ax.yaxis.set_major_formatter(formatter)

            for i, val in enumerate(values_plot):
                if val != 0:
                    formatted_val = self.format_rupiah_titik(val) 
                    self.ax.text(labels_plot[i], val, formatted_val, ha='center', va='bottom', fontsize=8)

            self.ax.set_title(f"Grafik Perubahan Modal Pemilik Tahun {tahun}", fontsize=12, fontweight="bold")
            self.ax.set_xlabel("Bulan")
            self.ax.set_ylabel("Saldo Modal (Juta Rupiah)")
            
            plt.setp(self.ax.get_xticklabels(), rotation=45, ha="right")
            
            self.ax.grid(axis='y', linestyle='--', alpha=0.7)
            self.figure.tight_layout(pad=3.0)
            self.canvas.draw()

        except sqlite3.Error as e:
            messagebox.showerror("Error Database", f"Gagal mengambil data Modal: {e}")
        except Exception as e:
            messagebox.showerror("Error Aplikasi", f"Terjadi kesalahan saat menampilkan grafik: {e}")