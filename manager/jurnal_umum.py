import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from function.bulan_map import bulan_map 
from datetime import datetime

class JurnalUmumPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(self, text="📘 Jurnal Umum", font=("Helvetica", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=15)

        bulan_list = list(bulan_map.keys())

        ttk.Label(self, text="Bulan: ").grid(row=1, column=0, sticky="e", pady=5)
        self.combo_bulan = ttk.Combobox(self, width=27, state="readonly", values=bulan_list)
        self.combo_bulan.grid(row=1, column=1, sticky="w", pady=5)

        ttk.Label(self, text="Tahun: ").grid(row=2, column=0, sticky="e", pady=5)
        self.entry_tahun = ttk.Entry(self, width=30)
        self.entry_tahun.grid(row=2, column=1, sticky="w", pady=5)

        ttk.Button(self, text="Tampilkan", command=self.load_laporan).grid(row=3, column=0, columnspan=2, pady=10)

        # Treeview untuk jurnal umum
        self.tree = ttk.Treeview(self, columns=("tanggal", "keterangan", "kode_akun", "nama_akun", "debit", "kredit"), show="headings", height=15)
        self.tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.tree.column("tanggal", width=130, anchor=tk.CENTER)
        self.tree.heading("tanggal", text="Tanggal")
        self.tree.column("keterangan", width=320, anchor=tk.W) 
        self.tree.heading("keterangan", text="Keterangan")
        self.tree.column("kode_akun", width=130, anchor=tk.CENTER)
        self.tree.heading("kode_akun", text="Kode Akun")
        self.tree.column("nama_akun", width=120, anchor=tk.W)
        self.tree.heading("nama_akun", text="Nama Akun")
        self.tree.column("debit", width=100, anchor=tk.E)
        self.tree.heading("debit", text="Debit (Rp)")
        self.tree.column("kredit", width=100, anchor=tk.E)
        self.tree.heading("kredit", text="Kredit (Rp)")
        
        ttk.Button(self, text="Kembali ke Menu Utama", command=lambda: controller.show_frame("Menu Utama Manager")
                   ).grid(row=6, column=0, columnspan=2, pady=5)
        
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

    def _connect_db(self):
        return sqlite3.connect('data_keuangan.db')

    def _format_rupiah(self, amount):
        if amount is None or amount == 0:
            return ""
        return f"{int(amount):,.0f}".replace(",", "X").replace(".", ",").replace("X", ".") 
    
    def _get_bulan_angka(self, nama_bulan):
        return bulan_map.get(nama_bulan, None)

    def load_laporan(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        bulan = self.combo_bulan.get()
        tahun = self.entry_tahun.get()

        if not bulan or not tahun.isdigit() or len(tahun) != 4:
            messagebox.showerror("Error", "Silakan pilih bulan dan isi tahun terlebih dahulu!")
            return

        bulan_angka = self._get_bulan_angka(bulan)
        if not bulan_angka:
            messagebox.showerror("Error", "Nama bulan tidak valid.")
            return

        conn = self._connect_db()
        c = conn.cursor()
        total_debit = 0
        total_kredit = 0

        try:
            query = """
                SELECT 
                    jud.tanggal, 
                    jud.transaksi_ref_id, 
                    jud.keterangan, 
                    jud.kode_akun, 
                    a.nama_akun, 
                    jud.debit, 
                    jud.kredit
                FROM jurnal_umum_detail jud
                JOIN akun a ON jud.kode_akun = a.kode_akun 
                WHERE strftime('%m', jud.tanggal) = ?
                  AND strftime('%Y', jud.tanggal) = ?
                  AND jud.jenis_jurnal = 'UMUM' -- FILTER HANYA JURNAL UMUM
                ORDER BY jud.tanggal ASC, jud.transaksi_ref_id ASC, jud.kredit DESC 
            """
            c.execute(query, (bulan_angka, tahun))
            results = c.fetchall()

            if not results:
                messagebox.showinfo("Info", f"Tidak ada data Jurnal Umum untuk {bulan} {tahun}.")
                return

            last_ref_id = None
            # PASTIKAN URUTAN UNPACKING SESUAI DENGAN QUERY (7 KOLOM)
            for tanggal, ref_id, keterangan_transaksi, kode_akun, nama_akun, debit, kredit in results:
                
                # Pastikan debit dan kredit adalah numerik (int/float)
                debit = debit if debit is not None else 0
                kredit = kredit if kredit is not None else 0
                
                if ref_id != last_ref_id:
                    if last_ref_id is not None:
                        self.tree.insert("", "end", values=("--", "", "", "", "", ""), tags=('separator',))
                    last_ref_id = ref_id
                
                if kredit > 0:
                    nama_akun = f"        {nama_akun}"
                    
                # Formatting Rupiah
                formatted_debit = self._format_rupiah(debit) if debit > 0 else ""
                formatted_kredit = self._format_rupiah(kredit) if kredit > 0 else ""
                
                total_debit += debit
                total_kredit += kredit

                # Masukkan data ke Treeview
                self.tree.insert("", "end", values=(
                    tanggal, 
                    f"[{ref_id}] {keterangan_transaksi}",
                    kode_akun, 
                    nama_akun, 
                    formatted_debit, 
                    formatted_kredit
                ))
            
            # Total
            self.tree.insert("", "end", values=("", "", "", "TOTAL", self._format_rupiah(total_debit), self._format_rupiah(total_kredit)), tags=('total',))
            
            self.tree.tag_configure('total', font=('Helvetica', 10, 'bold'), background='#E0F7FA')
            self.tree.tag_configure('separator', background='#EEEEEE')
            
            if round(total_debit) != round(total_kredit):
                 messagebox.showwarning("Peringatan", "Jurnal tidak seimbang (Debit ≠ Kredit). Periksa data.")

        except sqlite3.Error as e:
            messagebox.showerror("Error Database", f"Gagal mengambil data Jurnal Umum: {e}")
        finally:
            conn.close()