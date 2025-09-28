import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from get_data import get_data 
from bulan_map import bulan_map
from datetime import datetime

class PelaporanPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 11), padding=6)
        style.configure("Title.TLabel", font=("Helvetica", 18, "bold"))

        ttk.Label(self, text="📊 Laporan Keuangan", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, pady=20
        )
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Input Bulan
        ttk.Label(self, text="Bulan").grid(row=1, column=0, sticky="e", pady=5, padx=20)
        self.combo_bulan = ttk.Combobox(
            self,
            values=list(bulan_map.keys()),
            state="readonly",
            width=20
        )
        self.combo_bulan.grid(row=1, column=1, pady=5, sticky="w")
        
        today_month_num = datetime.now().strftime("%m")
        for indo_name, month_num in bulan_map.items():
            if month_num == today_month_num:
                 self.combo_bulan.set(indo_name)
                 break

        # Input Tahun
        ttk.Label(self, text="Tahun").grid(row=2, column=0, sticky="e", pady=5, padx=20)
        self.entry_tahun = ttk.Entry(self, width=23)
        self.entry_tahun.grid(row=2, column=1, pady=5, sticky="w")
        self.entry_tahun.insert(0, str(datetime.now().year))

        # Input Kategori
        ttk.Label(self, text="Kategori").grid(row=3, column=0, sticky="e", pady=5, padx=20)
        self.combo_kategori = ttk.Combobox(self, values=["Semua", "Pemasukan", "Pengeluaran"], state="readonly", width=20)
        self.combo_kategori.grid(row=3, column=1, pady=5, sticky="w")
        self.combo_kategori.set("Semua")

        # Tombol
        ttk.Button(self, text="📑 Tampilkan Laporan", command=self._show_laporan).grid(row=4, column=0, padx=10, pady=20, sticky="e")
        ttk.Button(self, text="⬅️ Kembali ke Menu",
                   command=lambda: controller.show_frame("Menu")).grid(row=4, column=1, padx=10, pady=20, sticky="w")
    
    
    def _format_rupiah(self, amount):
        try:
            return f"Rp{int(amount):,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except ValueError:
            return "Rp0"

    def _open_edit_form(self, event, tree_widget, top_level_window):
        selected_item = tree_widget.selection()
        if not selected_item:
            return
        values = tree_widget.item(selected_item, 'values')
        
        if len(values) < 5:
            messagebox.showerror("Error", "Data transaksi tidak lengkap.")
            return

        id_transaksi = values[0]
        tanggal = values[1]
        jumlah_numeric_str = values[2].replace('Rp', '').replace('.', '').strip()
        kategori = values[3]
        keterangan = values[4]
        data_to_edit = (id_transaksi, tanggal, jumlah_numeric_str, kategori, keterangan)
        
        try:
            pencatatan_page = self.controller.frames["Pencatatan"]
            pencatatan_page.load_selected_transaction(data_to_edit)
            top_level_window.destroy()
            self.controller.show_frame("Pencatatan")

        except KeyError:
            messagebox.showerror("Error Navigasi", "Halaman Pencatatan tidak ditemukan. Pastikan 'Pencatatan' terdaftar di App.")
        except AttributeError as e:
            messagebox.showerror("Error Navigasi", f"Gagal memuat data ke Pencatatan: {e}")


    def _show_laporan(self):
        bulan_str = self.combo_bulan.get()
        tahun = self.entry_tahun.get()
        kategori = self.combo_kategori.get()
        
        if not (bulan_str and tahun.isdigit() and kategori):
            messagebox.showerror("Error", "Bulan, Tahun (harus angka 4 digit), dan Kategori harus diisi.")
            return

        bulan = bulan_map.get(bulan_str)
        if not bulan:
            messagebox.showerror("Error", "Pilihan Bulan tidak valid.")
            return

        try:
            raw_data = get_data(bulan, tahun, kategori, include_id=True)
        except Exception as e:
            messagebox.showerror("Error Database", f"Gagal mengambil data: {e}")
            return
        
        if not raw_data:
            messagebox.showinfo("Info", f"Tidak ada data transaksi untuk {kategori} pada bulan {bulan_str} {tahun}.")
            return
        total_pemasukan = sum(row[2] for row in raw_data if row[3] == "Pemasukan")
        total_pengeluaran = sum(row[2] for row in raw_data if row[3] == "Pengeluaran")
        saldo = total_pemasukan - total_pengeluaran
        
        laporan_window = tk.Toplevel(self)
        laporan_window.title(f"Laporan {kategori} - {bulan_str} {tahun}")
        laporan_window.geometry("800x600")

        laporan_window.grid_rowconfigure(1, weight=1)
        laporan_window.grid_columnconfigure(0, weight=1)
        laporan_window.grid_columnconfigure(1, weight=0)
        
        # Frame Ringkasan
        summary_frame = ttk.LabelFrame(laporan_window, text="Ringkasan", padding=10)
        summary_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew", columnspan=2)
        
        summary_frame.grid_columnconfigure(0, weight=1)
        summary_frame.grid_columnconfigure(1, weight=1)
        summary_frame.grid_columnconfigure(2, weight=1)

        ttk.Label(summary_frame, text="Total Pemasukan:", font=("Helvetica", 11)).grid(row=0, column=0, padx=5, sticky="w")
        ttk.Label(summary_frame, text=self._format_rupiah(total_pemasukan), foreground="green", font=("Helvetica", 11, "bold")).grid(row=1, column=0, padx=5, sticky="w")

        ttk.Label(summary_frame, text="Total Pengeluaran:", font=("Helvetica", 11)).grid(row=0, column=1, padx=5, sticky="w")
        ttk.Label(summary_frame, text=self._format_rupiah(total_pengeluaran), foreground="red", font=("Helvetica", 11, "bold")).grid(row=1, column=1, padx=5, sticky="w")
        
        saldo_color = "blue" if saldo >= 0 else "red"
        ttk.Label(summary_frame, text="Saldo Bersih:", font=("Helvetica", 11)).grid(row=0, column=2, padx=5, sticky="w")
        ttk.Label(summary_frame, text=self._format_rupiah(saldo), font=("Helvetica", 12, "bold"), foreground=saldo_color).grid(row=1, column=2, padx=5, sticky="w")

        columns = ("ID", "Tanggal", "Jumlah", "Kategori", "Keterangan")
        tree = ttk.Treeview(laporan_window, columns=columns, show="headings")
        
        tree.column("ID", width=0, stretch=tk.NO)
        tree.heading("ID", text="ID")
        tree.column("Tanggal", width=90, anchor=tk.CENTER)
        tree.heading("Tanggal", text="Tanggal")
        tree.column("Jumlah", width=120, anchor=tk.E)
        tree.heading("Jumlah", text="Jumlah (Rp)")
        tree.column("Kategori", width=100, anchor=tk.CENTER)
        tree.heading("Kategori", text="Kategori")
        tree.column("Keterangan", width=350, anchor=tk.W)
        tree.heading("Keterangan", text="Keterangan")

        for row in raw_data:
            formatted_row = (row[0], row[1], self._format_rupiah(row[2]), row[3], row[4])
            tree.insert("", tk.END, values=formatted_row)
        vsb = ttk.Scrollbar(laporan_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        
        tree.grid(row=1, column=0, padx=(10, 0), pady=5, sticky="nsew")
        vsb.grid(row=1, column=1, padx=(0, 10), sticky="ns")

        tree.bind('<Double-1>', lambda e: self._open_edit_form(e, tree, laporan_window))
        ttk.Label(laporan_window, text="*Double-klik baris untuk Edit/Hapus data di Pencatatan", font=("Helvetica", 10, "italic")).grid(row=2, column=0, padx=10, pady=(0, 5), sticky="w")

        ttk.Button(laporan_window, text="Tutup Laporan", command=laporan_window.destroy).grid(row=3, column=0, columnspan=2, pady=10)

        laporan_window.transient(self)
        laporan_window.grab_set()
        self.wait_window(laporan_window)
        
        self.combo_bulan.set(datetime.now().strftime("%B")) # Kembali ke bulan saat ini
        self.entry_tahun.delete(0, tk.END)
        self.entry_tahun.insert(0, str(datetime.now().year))
        self.combo_kategori.set("Semua")
