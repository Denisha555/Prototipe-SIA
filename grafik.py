import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
from get_data import get_data
from function.bulan_map import bulan_map
from matplotlib.ticker import FuncFormatter
from collections import defaultdict
import datetime
import numpy as np

class GrafikPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        style = ttk.Style()
        style.configure("Title.TLabel", font=("Helvetica", 18, "bold"))
        style.configure("TLabel", font=("Helvetica", 12))
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        ttk.Label(self, text="📈 Analisis Grafik Keuangan", style="Title.TLabel").grid(
            row=0, column=1, columnspan=1, pady=20
        )

        input_frame = ttk.Frame(self)
        input_frame.grid(row=1, column=1, padx=20, pady=10, sticky="n")
        
        # Input Bulan
        ttk.Label(input_frame, text="Bulan").grid(row=0, column=0, sticky="e", pady=5, padx=10)
        self.combo_bulan = ttk.Combobox(
            input_frame,
            values=list(bulan_map.keys()),
            state="readonly",
            width=20
        )
        self.combo_bulan.grid(row=0, column=1, pady=5, sticky="w")
        
        current_month_num = datetime.date.today().strftime('%m')
        for indo_name, month_num in bulan_map.items():
            if month_num == current_month_num:
                 self.combo_bulan.set(indo_name)
                 break

        # Input Tahun
        ttk.Label(input_frame, text="Tahun").grid(row=1, column=0, sticky="e", pady=5, padx=10)
        self.entry_tahun = ttk.Entry(input_frame, width=23)
        self.entry_tahun.grid(row=1, column=1, pady=5, sticky="w")
        self.entry_tahun.insert(0, str(datetime.date.today().year))


        ttk.Label(input_frame, text="Kategori").grid(row=2, column=0, sticky="e", pady=5, padx=10)
        self.combo_kategori = ttk.Combobox(
            input_frame,
            values=["Semua", "Pemasukan", "Pengeluaran"],
            state="readonly",
            width=20
        )
        self.combo_kategori.grid(row=2, column=1, pady=5, sticky="w")
        self.combo_kategori.set("Semua")


        def format_rupiah(x, pos=None):
            if x >= 1e9:
                return 'Rp{:1.1f} M'.format(x * 1e-9).replace(".", ",")
            elif x >= 1e6:
                return 'Rp{:1.1f} Jt'.format(x * 1e-6).replace(".", ",")
            elif x >= 1e3:
                return 'Rp{:1.0f} Rb'.format(x * 1e-3).replace(".", ",")
            # Jika nilainya kecil (di bawah ribuan), tampilkan angka penuh
            return 'Rp{:,.0f}'.format(x).replace(",", "#").replace(".", ",").replace("#", ".")
        
        def format_pie_label(pct, total_amount):
            val = int(np.round(pct/100.*total_amount))
            return f"{pct:.1f}%\n({format_rupiah(val)})"


        def tampil_grafik():
            bulan_str = self.combo_bulan.get()
            tahun = self.entry_tahun.get()
            kategori = self.combo_kategori.get()
            
            if not (bulan_str and tahun.isdigit()):
                messagebox.showerror("Error", "Bulan dan Tahun (harus angka) harus diisi.")
                return

            bulan = bulan_map.get(bulan_str)
            
            try:
                data_raw = get_data(bulan, tahun, kategori)
            except Exception as e:
                messagebox.showerror("Error Database", f"Gagal mengambil data: {e}")
                return
            
            if not data_raw:
                messagebox.showinfo("Info", f"Tidak ada data transaksi untuk {bulan_str} {tahun} yang dapat divisualisasikan.")
                return

            if kategori == "Semua":
                total_pemasukan = sum(row[1] for row in data_raw if row[2] == "Pemasukan")
                total_pengeluaran = sum(row[1] for row in data_raw if row[2] == "Pengeluaran")
                
                sizes = [total_pemasukan, total_pengeluaran]
                labels = ["Pemasukan", "Pengeluaran"]
                colors = ['#4CAF50', '#F44336']
                
                valid_sizes = [s for s in sizes if s > 0]
                valid_labels = [l for l, s in zip(labels, sizes) if s > 0]
                valid_colors = [c for c, s in zip(colors, sizes) if s > 0]

                if not valid_sizes:
                    messagebox.showinfo("Info", "Tidak ada data Pemasukan maupun Pengeluaran untuk bulan ini.")
                    return

                total_amount = sum(valid_sizes)

                fig, ax = plt.subplots(figsize=(10, 6))
                
                wedges, texts, autotexts = ax.pie(
                    valid_sizes, 
                    labels=valid_labels, 
                    colors=valid_colors,
                    autopct=lambda pct: format_pie_label(pct, total_amount),
                    startangle=90, 
                    shadow=True,
                    wedgeprops={"edgecolor": "black", "linewidth": 0.5},
                    textprops={'fontsize': 11}
                )
                
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_weight('bold')
                
                ax.set_title(f'Perbandingan Pemasukan vs Pengeluaran di {bulan_str} {tahun}', fontsize=16, pad=20)
                ax.axis('equal')

                ax.legend(
                    wedges, valid_labels, 
                    title="Kategori", 
                    loc="center left",
                    bbox_to_anchor=(1, 0, 0.5, 1)
                )

                fig.canvas.manager.set_window_title("Pie Chart Pemasukan & Pengeluaran")
                fig.canvas.manager.window.state('zoomed') 
                plt.tight_layout()
                plt.show()
                return

            else:
                daily_totals = defaultdict(int)
                for row in data_raw:
                    daily_totals[row[0]] += row[1]
                
                sorted_dates = sorted(daily_totals.keys())
                tanggal_list = sorted_dates
                jumlah_list = [daily_totals[d] for d in sorted_dates]
                
                if kategori == "Pemasukan":
                    color = '#2196F3'
                    title = "Grafik Pemasukan Harian"
                elif kategori == "Pengeluaran":
                    color = '#FF5722'
                    title = "Grafik Pengeluaran Harian"

                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.bar(tanggal_list, jumlah_list, color=color)

                ax.set_title(f'Total {kategori} Harian di {bulan_str} {tahun}', fontsize=14, pad=20)
                ax.set_xlabel("Tanggal", fontsize=12)
                ax.set_ylabel(f"Jumlah {kategori}", fontsize=12)
                
                ax.yaxis.set_major_formatter(FuncFormatter(format_rupiah))
                plt.xticks(rotation=45, ha='right')

                ax.grid(axis='y', linestyle='--', alpha=0.7)

                plt.tight_layout()
                
                fig.canvas.manager.set_window_title(title)
                fig.canvas.manager.window.state('zoomed') 

                plt.show()

        # Tombol
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=1, padx=20, pady=10, sticky="n") 
        
        ttk.Button(btn_frame, text="📈 Tampilkan Grafik", 
                   command=tampil_grafik).grid(row=0, column=0, padx=10, pady=20)
        ttk.Button(btn_frame, text="⬅️ Kembali ke Menu", 
                   command=lambda: controller.show_frame("Menu")).grid(row=0, column=1, padx=10, pady=20)
