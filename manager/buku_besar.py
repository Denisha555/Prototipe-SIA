import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from function.bulan_map import bulan_map 
from datetime import datetime

def _connect_db():
    return sqlite3.connect('data_keuangan.db')

class BukuBesarPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # --- Konfigurasi tata letak utama ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # === Judul Halaman ===
        ttk.Label(
            self,
            text="📘 Buku Besar",
            font=("Helvetica", 18, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(15, 10))
        
        form_frame = ttk.Frame(self)
        form_frame.grid(row=1, column=0, columnspan=2, pady=10)

        bulan_list = list(bulan_map.keys())
        self.akun_map = self._get_account_data()
        akun_list = list(self.akun_map.keys())

        ttk.Label(form_frame, text="Akun:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.combo_akun = ttk.Combobox(form_frame, width=27, state="readonly", values=akun_list)
        self.combo_akun.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        if akun_list:
            self.combo_akun.current(0)
            
        ttk.Label(form_frame, text="Bulan:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.combo_bulan = ttk.Combobox(form_frame, width=27, state="readonly", values=bulan_list)
        self.combo_bulan.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form_frame, text="Tahun:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.entry_tahun = ttk.Entry(form_frame, width=30)
        self.entry_tahun.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Button(form_frame, text="Tampilkan", command=self.show_buku_besar).grid(
            row=3, column=0, columnspan=2, pady=10
        )

        ttk.Button(self, text="Kembali Ke Menu Utama", command=lambda: controller.show_frame("Menu Utama Manager")
                   ).grid(row=3, column=0, columnspan=2, pady=5)
        
        today = datetime.now()
        current_year = today.strftime("%Y")
        current_month_num = today.strftime("%m")
        
        current_month_name = None
        for name, num in bulan_map.items():
            if num == current_month_num:
                current_month_name = name
                break
                
        if current_month_name:
            self.combo_bulan.set(current_month_name)
        
        self.entry_tahun.insert(0, current_year)

        # === Frame Utama untuk Buku Besar ===
        self.bb_frame = ttk.Frame(self)
        self.bb_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        self.bb_frame.grid_columnconfigure(0, weight=1)
        self.bb_frame.grid_rowconfigure(0, weight=1)
        
        self.current_treeviews = []
        
        self._create_empty_treeview(self.bb_frame)

    def _create_empty_treeview(self, parent_frame):
        
        for widget in parent_frame.winfo_children():
            widget.destroy()

        ttk.Label(
            parent_frame,
            text="Akun: [Pilih Akun]",
            font=("Helvetica", 14, "bold"),
            anchor="w"
        ).grid(row=0, column=0, sticky="ew", pady=(5, 0))
        ttk.Label(
            parent_frame,
            text="Saldo Normal: -",
            anchor="w"
        ).grid(row=1, column=0, sticky="ew", pady=(0, 5))
            
        tree = ttk.Treeview(parent_frame, columns=("tanggal", "keterangan", "debit", "kredit", "saldo"), show="headings")
        tree.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        parent_frame.grid_rowconfigure(2, weight=1)
        
        tree.column("tanggal", width=100, anchor=tk.CENTER)
        tree.heading("tanggal", text="Tanggal")
        tree.column("keterangan", width=350, anchor=tk.W)
        tree.heading("keterangan", text="Keterangan")
        tree.column("debit", width=130, anchor=tk.E)
        tree.heading("debit", text="Debit (Rp)")
        tree.column("kredit", width=130, anchor=tk.E)
        tree.heading("kredit", text="Kredit (Rp)")
        tree.column("saldo", width=150, anchor=tk.E)
        tree.heading("saldo", text="Saldo (Rp)")
        
        # Scrollbar
        vsb = ttk.Scrollbar(parent_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=2, column=1, sticky="ns")

        tree.tag_configure('info', foreground='gray')
        
        self.current_treeviews = [tree]
        

    def _format_rupiah(self, amount):
        is_negative = amount < 0
        abs_amount = abs(amount)
        formatted = f"{abs_amount:,.0f}".replace(",", "#").replace(".", ",").replace("#", ".")
        return f"({formatted})" if is_negative else formatted

    def _get_account_data(self):
        conn = _connect_db()
        c = conn.cursor()
        akun_map = {}
        try:
            c.execute("SELECT kode_akun, nama_akun, saldo_normal FROM akun ORDER BY kode_akun ASC")
            for kode, nama, saldo_normal in c.fetchall():
                akun_map[f"{kode} - {nama}"] = {'kode': kode, 'nama': nama, 'saldo_normal': saldo_normal}
        except sqlite3.Error as e:
            messagebox.showerror("Error Database", f"Gagal memuat daftar akun: {e}")
        finally:
            conn.close()
        return akun_map

    def _get_beginning_balance(self, kode_akun, year, month):
        conn = _connect_db()
        c = conn.cursor()
        
        bulan_num = bulan_map[month]
        
        balance = 0
        try:
            c.execute("""
                SELECT SUM(debit) - SUM(kredit)
                FROM jurnal_umum_detail
                WHERE kode_akun = ? AND tanggal < ?
            """, (kode_akun, f"{year}-{bulan_num}-01"))
            
            result = c.fetchone()
            if result and result[0] is not None:
                balance = result[0]

        except sqlite3.Error as e:
            messagebox.showerror("Error Database", f"Gagal menghitung saldo awal: {e}")
        finally:
            conn.close()
            
        return balance

    def _get_monthly_transactions(self, kode_akun, year, month):
        conn = _connect_db()
        c = conn.cursor()
        
        bulan_num = bulan_map[month]
        
        query = """
            SELECT tanggal, keterangan, debit, kredit
            FROM jurnal_umum_detail
            WHERE kode_akun = ? 
            AND strftime('%m', tanggal) = ?
            AND strftime('%Y', tanggal) = ?
            ORDER BY tanggal ASC, id ASC
        """
        transactions = []
        try:
            c.execute(query, (kode_akun, bulan_num, year))
            transactions = c.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Error Database", f"Gagal memuat transaksi bulanan: {e}")
        finally:
            conn.close()
            
        return transactions


    def show_buku_besar(self):
        for widget in self.bb_frame.winfo_children():
            widget.destroy()
        self.current_treeviews = []
        
        selected_akun_str = self.combo_akun.get()
        selected_bulan = self.combo_bulan.get()
        selected_tahun = self.entry_tahun.get()
        
        if not all([selected_akun_str, selected_bulan, selected_tahun]):
            messagebox.showerror("Error", "Pilih Akun, Bulan, dan isi Tahun.")
            self._create_empty_treeview(self.bb_frame)
            return
            
        try:
            akun_data = self.akun_map[selected_akun_str]
        except KeyError:
             messagebox.showerror("Error", "Akun tidak valid.")
             self._create_empty_treeview(self.bb_frame)
             return
             
        kode_akun = akun_data['kode']
        nama_akun = akun_data['nama']
        saldo_normal = akun_data['saldo_normal']

        saldo_awal = self._get_beginning_balance(kode_akun, selected_tahun, selected_bulan)
        
        transaksi_bulanan = self._get_monthly_transactions(kode_akun, selected_tahun, selected_bulan)

        if not transaksi_bulanan and saldo_awal == 0:
            messagebox.showinfo("Info", f"Tidak ada transaksi untuk akun {kode_akun} pada periode ini.")
            self._create_empty_treeview(self.bb_frame)
            return
            
        ttk.Label(
            self.bb_frame,
            text=f"Akun: {kode_akun} - {nama_akun}",
            font=("Helvetica", 14, "bold"),
            anchor="w"
        ).grid(row=0, column=0, sticky="ew", pady=(5, 0))
        ttk.Label(
            self.bb_frame,
            text=f"Saldo Normal: {saldo_normal}",
            anchor="w"
        ).grid(row=1, column=0, sticky="ew", pady=(0, 5))
            
        tree = ttk.Treeview(self.bb_frame, columns=("tanggal", "keterangan", "debit", "kredit", "saldo"), show="headings")
        tree.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        self.bb_frame.grid_rowconfigure(2, weight=1)
        
        tree.column("tanggal", width=100, anchor=tk.CENTER)
        tree.heading("tanggal", text="Tanggal")
        tree.column("keterangan", width=350, anchor=tk.W)
        tree.heading("keterangan", text="Keterangan")
        tree.column("debit", width=130, anchor=tk.E)
        tree.heading("debit", text="Debit (Rp)")
        tree.column("kredit", width=130, anchor=tk.E)
        tree.heading("kredit", text="Kredit (Rp)")
        tree.column("saldo", width=150, anchor=tk.E)
        tree.heading("saldo", text=f"Saldo ({saldo_normal}) (Rp)")
        
        vsb = ttk.Scrollbar(self.bb_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=2, column=1, sticky="ns")
        
        # --- HITUNG DAN INPUT DATA ---
        saldo_berjalan = saldo_awal
        total_debit = 0
        total_kredit = 0
        
        tree.insert("", "end", values=(
            selected_bulan,
            "Saldo Awal",
            "", 
            "",
            self._format_rupiah(saldo_berjalan)
        ), tags=('saldo_awal',))
        tree.tag_configure('saldo_awal', font=('Helvetica', 10, 'bold'), background='#F0F0F0')
        
        for tgl, ket, debit, kredit in transaksi_bulanan:
            if saldo_normal == 'Debit':
                saldo_berjalan += debit - kredit
            else:
                saldo_berjalan += kredit - debit
                
            total_debit += debit
            total_kredit += kredit

            tree.insert("", "end", values=(
                tgl,
                ket,
                self._format_rupiah(debit) if debit else "",
                self._format_rupiah(kredit) if kredit else "",
                self._format_rupiah(saldo_berjalan)
            ))
            
        tree.insert("", "end", values=(
            "", 
            "SALDO AKHIR", 
            self._format_rupiah(total_debit), 
            self._format_rupiah(total_kredit), 
            self._format_rupiah(saldo_berjalan)
        ), tags=('saldo_akhir',))
        
        tree.tag_configure('saldo_akhir', font=('Helvetica', 11, 'bold'), background='#E0F7FA')
        
        self.current_treeviews.append(tree)