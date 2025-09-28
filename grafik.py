import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
from get_data import get_data
from bulan_map import bulan_map
from matplotlib.ticker import FuncFormatter
from collections import defaultdict


class GrafikPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        ttk.Label(self, text="Analisis Keuangan", font=("Helvetica", 18)).grid(row=0, column=0, columnspan=2, pady=20)

        # Input Bulan
        ttk.Label(self, text="Bulan").grid(row=1, column=0, sticky="e", pady=5, padx=10)
        self.combo_bulan = ttk.Combobox(
            self,
            values=[
                "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                "Juli", "Agustus", "September", "Oktober", "November", "Desember"
            ],
            state="readonly",
            width=20
        )
        self.combo_bulan.grid(row=1, column=1, pady=5, sticky="w")

        # Input Tahun
        ttk.Label(self, text="Tahun").grid(row=2, column=0, sticky="e", pady=5, padx=10)
        self.entry_tahun = ttk.Entry(self, width=23)
        self.entry_tahun.grid(row=2, column=1, pady=5, sticky="w")

        # Input Kategori
        ttk.Label(self, text="Kategori").grid(row=3, column=0, sticky="e", pady=5, padx=10)
        self.combo_kategori = ttk.Combobox(
            self,
            values=["Semua", "Pemasukan", "Pengeluaran"],
            state="readonly",
            width=20
        )
        self.combo_kategori.grid(row=3, column=1, pady=10, sticky="w")

        def tampil_grafik():
            bulan_str = self.combo_bulan.get()
            bulan_int = bulan_map.get(bulan_str, "")
            tahun = self.entry_tahun.get()
            kategori = self.combo_kategori.get()

            if not (bulan_str and tahun.isdigit()):
                messagebox.showerror("Error", "Tahun harus diisi dengan benar!")
                return
            
            if not kategori:
                messagebox.showerror("Error", "Kategori harus dipilih!")
                return
            
            data = get_data(bulan_int, tahun, kategori)
            if not data:
                messagebox.showinfo("Info", "Tidak ada data untuk periode ini.")
                return
            
            def func(pct, allvals):
                absolute = int(round(pct/100.*sum(allvals)))
                return f"{pct:.1f}%\nRp{absolute:,}"
            
            def format_rupiah(x, pos=None):
                if x >= 1_000_000_000:
                    return f'{x/1_000_000_000:.1f} Miliar'
                elif x >= 1_000_000:
                    return f'{x/1_000_000:.1f} Juta'
                elif x >= 1_000:
                    return f'{x/1_000:.0f} Ribu'
                else:
                    return str(int(x))
            
            if kategori == "Semua":
                pemasukan = sum(row[1] for row in data if row[2] == "Pemasukan")
                pengeluaran = sum(row[1] for row in data if row[2] == "Pengeluaran")
                labels = ['Pemasukan', 'Pengeluaran']
                sizes = [pemasukan, pengeluaran]
                colors = ['#4CAF50', '#F44336']
                mng = plt.get_current_fig_manager()
                mng.window.state('zoomed') 
                plt.gcf().canvas.manager.set_window_title("Grafik Pemasukan & Pengeluaran")
                plt.pie(sizes, labels=labels, colors=colors, autopct=lambda pct: func(pct, sizes), startangle=140)
                plt.title(f'Pemasukan dan Pengeluaran di {bulan_str} {tahun}')
                plt.show()
            elif kategori in ["Pemasukan", "Pengeluaran"]:
                tanggal_list = []
                jumlah_list = []

                for i in range(len(data)):
                    if data[i][2] == kategori:
                        if data[i][0] in tanggal_list:
                            jumlah_list[tanggal_list.index(data[i][0])] += data[i][1]
                        else:
                            tanggal_list.append(data[i][0])
                            jumlah_list.append(data[i][1])

                if kategori == "Pemasukan":
                    color = '#2196F3'
                    title = "Grafik Pemasukan"
                elif kategori == "Pengeluaran":
                    color = '#FF5722'
                    title = "Grafik Pengeluaran"

                fig, ax = plt.subplots()
                bars = ax.bar(tanggal_list, jumlah_list, color=color)

                # Label di atas batang
                ax.bar_label(bars, labels=[format_rupiah(y) for y in jumlah_list], padding=3)

                ax.set_title(f'{kategori} di {bulan_str} {tahun}')
                ax.yaxis.set_major_formatter(FuncFormatter(format_rupiah))
                plt.xticks(rotation=90)

                # Zoom window
                fig.canvas.manager.window.state('zoomed')
                fig.canvas.manager.set_window_title(title)

                plt.tight_layout()
                plt.show()


            # Reset Form
            self.combo_bulan.set('')
            self.entry_tahun.delete(0, tk.END)
            self.combo_kategori.set('')
            

        # Tombol 
        ttk.Button(self, text="📈 Tampilkan Grafik", 
                   command=tampil_grafik).grid(row=4, column=0, padx=10, pady=10, sticky="e")
        ttk.Button(self, text="⬅️ Kembali ke Menu", 
                   command=lambda: controller.show_frame("Menu")).grid(row=4, column=1, padx=10, pady=10, sticky="w")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
