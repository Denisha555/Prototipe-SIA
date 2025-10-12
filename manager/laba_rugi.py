import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

try:
    from function.bulan_map import bulan_map 
except ImportError:
    try:
        from bulan_map import bulan_map
    except ImportError:
        bulan_map = {
            "Januari": "01", "Februari": "02", "Maret": "03", 
            "April": "04", "Mei": "05", "Juni": "06",
            "Juli": "07", "Agustus": "08", "September": "09",
            "Oktober": "10", "November": "11", "Desember": "12"
        }

def _connect_db():
    return sqlite3.connect('data_keuangan.db')

def _format_rupiah(amount):
    try:
        abs_amount = abs(int(amount)) 
        formatted = f"{abs_amount:,.0f}".replace(",", "#").replace(".", ",").replace("#", ".")
        return formatted
    except (TypeError, ValueError):
        return ""

def _get_account_balances(bulan_num, tahun):
    conn = _connect_db()
    c = conn.cursor()

    c.execute("""
        SELECT kode_akun, nama_akun, kategori, saldo_normal 
        FROM akun 
        WHERE kategori IN ('Pendapatan', 'Beban') 
        ORDER BY kode_akun ASC
    """)
    operating_accounts = c.fetchall()
    
    report_data = []

    for kode_akun, nama_akun, kategori, saldo_normal in operating_accounts:
        
        # Hitung Saldo Normal (NS) - Mutasi Jurnal Umum
        query_ns = """
            SELECT SUM(debit), SUM(kredit)
            FROM jurnal_umum_detail
            WHERE kode_akun = ?
              AND strftime('%m', tanggal) = ?
              AND strftime('%Y', tanggal) = ?
              AND jenis_jurnal NOT IN ('PENYESUAIAN', 'PENUTUP') 
        """
        c.execute(query_ns, (kode_akun, bulan_num, tahun))
        ns_d_mutasi, ns_k_mutasi = c.fetchone()
        ns_d_mutasi = ns_d_mutasi if ns_d_mutasi is not None else 0
        ns_k_mutasi = ns_k_mutasi if ns_k_mutasi is not None else 0
        
        ns_balance = ns_d_mutasi - ns_k_mutasi
        
        # Hitung Jurnal Penyesuaian (AJP)
        query_ajp = """
            SELECT SUM(debit), SUM(kredit)
            FROM transaksi_penyesuaian
            WHERE kode_akun = ?
              AND strftime('%m', tanggal) = ?
              AND strftime('%Y', tanggal) = ?
        """
        c.execute(query_ajp, (kode_akun, bulan_num, tahun))
        ajp_d_mutasi, ajp_k_mutasi = c.fetchone()
        ajp_d_mutasi = ajp_d_mutasi if ajp_d_mutasi is not None else 0
        ajp_k_mutasi = ajp_k_mutasi if ajp_k_mutasi is not None else 0

        # Hitung Neraca Saldo Disesuaikan (NSD)
        nsd_balance = ns_balance + (ajp_d_mutasi - ajp_k_mutasi)
        
        nsd_d = max(0, nsd_balance)
        nsd_k = abs(min(0, nsd_balance))
        
        if nsd_d != 0 or nsd_k != 0:
            report_data.append({
                'kode': kode_akun,
                'nama': nama_akun,
                'kategori': kategori,
                'debit': nsd_d, 
                'kredit': nsd_k, 
            })
    
    conn.close()
    return report_data


class LabaRugiPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        
        ttk.Label(
            self,
            text="💰 Laporan Laba Rugi",
            font=("Helvetica", 18, "bold")
        ).grid(row=0, column=0, pady=(15, 10))

        form_frame = ttk.Frame(self)
        form_frame.grid(row=1, column=0, pady=10)

        bulan_list = list(bulan_map.keys())
        current_month_name = datetime.now().strftime("%B")
        english_to_indo = {
            "January": "Januari", "February": "Februari", "March": "Maret", 
            "April": "April", "May": "Mei", "June": "Juni",
            "July": "Juli", "August": "Agustus", "September": "September",
            "October": "Oktober", "November": "November", "December": "Desember"
        }
        default_month = english_to_indo.get(current_month_name, "Januari")

        ttk.Label(form_frame, text="Bulan:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.combo_bulan = ttk.Combobox(form_frame, width=27, state="readonly", values=bulan_list)
        self.combo_bulan.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.combo_bulan.set(default_month)

        ttk.Label(form_frame, text="Tahun:").grid(row=0, column=2, padx=10, pady=5, sticky="e")
        self.entry_tahun = ttk.Entry(form_frame, width=10)
        self.entry_tahun.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.entry_tahun.insert(0, str(datetime.now().year))

        ttk.Button(form_frame, text="Tampilkan", command=self.load_report).grid(row=0, column=4, padx=15)

        # --- Treeview ---
        scroll_frame = ttk.Frame(self)
        scroll_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        scroll_frame.grid_rowconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            scroll_frame, 
            columns=("nama", "jumlah"), 
            show="headings", 
            height=20
        )

        self.tree.column("nama", width=350, anchor="w")
        self.tree.heading("nama", text="Rincian")
        self.tree.column("jumlah", width=150, anchor="e")
        self.tree.heading("jumlah", text="Jumlah (Rp)")

        vsb = ttk.Scrollbar(scroll_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        ttk.Button(self, text="Kembali ke menu utama", command=lambda: controller.show_frame("Menu Utama Manager")).grid(row=3, column=0, pady=10)


    def load_report(self):
        bulan_nama = self.combo_bulan.get()
        tahun = self.entry_tahun.get()

        if not bulan_nama or not tahun:
            messagebox.showerror("Error", "Bulan dan Tahun harus diisi.")
            return

        try:
            bulan_num = bulan_map[bulan_nama]
            int(tahun)
        except Exception:
            messagebox.showerror("Error", "Input Bulan/Tahun tidak valid.")
            return

        # Hapus data lama
        for i in self.tree.get_children():
            self.tree.delete(i)

        data = _get_account_balances(bulan_num, tahun)

        if not data:
            self.insert_row("Info", f"Tidak ada Pendapatan atau Beban di periode {bulan_nama} {tahun}.", 'center_bold', '')
            return

        total_pendapatan = 0
        total_beban = 0

        # === PENDAPATAN ===
        self.insert_row("PENDAPATAN:", "", 'header_section', '')
        
        pendapatan_items = [item for item in data if item['kategori'] == 'Pendapatan']
        for item in pendapatan_items:
            jumlah = item['kredit'] - item['debit']
            if jumlah > 0:
                self.insert_row(item['nama'], _format_rupiah(jumlah), 'item', '')
                total_pendapatan += jumlah

        self.insert_row("Total Pendapatan", _format_rupiah(total_pendapatan), 'subtotal', 'Rp')
        self.insert_row("", "", 'separator', '')

        # === BEBAN ===
        self.insert_row("BEBAN:", "", 'header_section', '')

        beban_items = [item for item in data if item['kategori'] == 'Beban']
        for item in beban_items:
            jumlah = item['debit'] - item['kredit']
            if jumlah > 0:
                self.insert_row(item['nama'], _format_rupiah(jumlah), 'item', '')
                total_beban += jumlah
        
        self.insert_row("Total Beban", _format_rupiah(total_beban), 'subtotal', 'Rp')
        self.insert_row("", "", 'separator', '')

        # === LABA BERSIH ===
        laba_bersih = total_pendapatan - total_beban
        keterangan = "LABA BERSIH" if laba_bersih >= 0 else "RUGI BERSIH"

        self.insert_row(
            keterangan, 
            _format_rupiah(abs(laba_bersih)), 
            'grand_total', 
            'Rp' if laba_bersih != 0 else ''
        )
        
        self.tree.tag_configure('header_section', font=('Helvetica', 10, 'bold'), foreground='#005662') 
        self.tree.tag_configure('separator', background='#EEEEEE')
        self.tree.tag_configure('subtotal', font=('Helvetica', 10, 'bold'), background='#F0F0F0') 
        self.tree.tag_configure('grand_total', font=('Helvetica', 11, 'bold'), background='#E0F7FA') 
        self.tree.tag_configure('item', font=('Helvetica', 10), foreground='#424242')

        messagebox.showinfo("Sukses", f"Laporan Laba Rugi untuk bulan {bulan_nama} {tahun} berhasil dimuat.")


    def insert_row(self, label, amount_str, tag, prefix=""):
        formatted_amount = f"{prefix} {amount_str}" if prefix else amount_str
        self.tree.insert("", "end", values=(label, formatted_amount), tags=(tag,))