import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

try:
    from function.bulan_map import bulan_map
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
        amount = int(amount)
        if amount == 0:
            return ""
        return f"{amount:,.0f}".replace(",", "#").replace(".", ",").replace("#", ".")
    except (TypeError, ValueError):
        return "" 

class WorksheetPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        
        ttk.Label(
            self,
            text="📊 Kertas Kerja (Worksheet) 12 Kolom",
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

        ttk.Button(form_frame, text="Tampilkan", command=self.load_worksheet).grid(row=0, column=4, padx=15)

        scroll_frame = ttk.Frame(self)
        scroll_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        scroll_frame.grid_rowconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(0, weight=1)

        hsb = ttk.Scrollbar(scroll_frame, orient="horizontal")
        hsb.grid(row=1, column=0, sticky="ew")

        vsb = ttk.Scrollbar(scroll_frame, orient="vertical")
        vsb.grid(row=0, column=1, sticky="ns")

        self.tree = ttk.Treeview(
            scroll_frame, 
            columns=("kode", "akun", "ns_d", "ns_k", "ajp_d", "ajp_k", "nsd_d", "nsd_k", "lr_d", "lr_k", "ner_d", "ner_k"), 
            show="headings", 
            height=20,
            xscrollcommand=hsb.set,
            yscrollcommand=vsb.set
        )

        hsb.config(command=self.tree.xview)
        vsb.config(command=self.tree.yview)

        self.tree.column("kode", width=60, anchor="center")
        self.tree.heading("kode", text="Kode")
        self.tree.column("akun", width=180, anchor="w")
        self.tree.heading("akun", text="Nama Akun")
        
        def setup_col(name, text, width=100):
            self.tree.column(name, width=width, anchor="e")
            self.tree.heading(name, text=text)

        # Neraca Saldo
        setup_col("ns_d", "NS Debit")
        setup_col("ns_k", "NS Kredit")
        # Penyesuaian
        setup_col("ajp_d", "AJP Debit")
        setup_col("ajp_k", "AJP Kredit")
        # Neraca Saldo Disesuaikan
        setup_col("nsd_d", "NSD Debit")
        setup_col("nsd_k", "NSD Kredit")
        # Laba Rugi
        setup_col("lr_d", "LR Debit")
        setup_col("lr_k", "LR Kredit")
        # Neraca
        setup_col("ner_d", "NER Debit")
        setup_col("ner_k", "NER Kredit")

        self.tree.grid(row=0, column=0, sticky="nsew")
        
        ttk.Button(self, text="Kembali ke menu utama", command=lambda: controller.show_frame("Menu Utama Manager")).grid(row=3, column=0, pady=10)


    def _get_account_balances(self, bulan_num, tahun):
        conn = _connect_db()
        c = conn.cursor()

        c.execute("SELECT kode_akun, nama_akun, kategori, saldo_normal FROM akun ORDER BY kode_akun ASC")
        all_accounts = c.fetchall()
        
        worksheet_data = {}

        for kode_akun, nama_akun, kategori, saldo_normal in all_accounts:
            
            # 1. Neraca Saldo (NS) - Hanya dari Jurnal Umum (non-penyesuaian)
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
            
            # Hitung Saldo NS
            ns_balance = ns_d_mutasi - ns_k_mutasi
            ns_d = max(0, ns_balance)
            ns_k = abs(min(0, ns_balance))
            
            # 2. Jurnal Penyesuaian (AJP)
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

            # Hanya masukkan akun yang memiliki mutasi di NS atau AJP
            if ns_d != 0 or ns_k != 0 or ajp_d_mutasi != 0 or ajp_k_mutasi != 0:
                worksheet_data[kode_akun] = {
                    'nama': nama_akun,
                    'kategori': kategori,
                    'saldo_normal': saldo_normal,
                    'ns_d': ns_d,
                    'ns_k': ns_k,
                    'ajp_d': ajp_d_mutasi,
                    'ajp_k': ajp_k_mutasi,
                }
        
        conn.close()
        return worksheet_data


    def load_worksheet(self):
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

        for i in self.tree.get_children():
            self.tree.delete(i)

        data = self._get_account_balances(bulan_num, tahun)
        if not data:
            messagebox.showinfo("Info", "Tidak ada data transaksi atau penyesuaian untuk periode ini.")
            return

        # Inisialisasi Total Global
        total_ns = [0, 0] # D, K
        total_ajp = [0, 0]
        total_nsd = [0, 0]
        total_lr = [0, 0]
        total_ner = [0, 0]
        
        for kode, item in data.items():
            # Hitung Neraca Saldo Disesuaikan (NSD)
            nsd_balance = (item['ns_d'] - item['ns_k']) + (item['ajp_d'] - item['ajp_k'])
            nsd_d = max(0, nsd_balance)
            nsd_k = abs(min(0, nsd_balance))
            
            # Pisahkan ke Laba Rugi (LR) atau Neraca (NER)
            lr_d, lr_k, ner_d, ner_k = 0, 0, 0, 0
            
            kategori = item['kategori']
            
            if kategori in ['Pendapatan', 'Beban']:
                # Pindahkan akun riil (LR)
                lr_d, lr_k = nsd_d, nsd_k
            else:
                # Pindahkan akun nominal (Neraca)
                ner_d, ner_k = nsd_d, nsd_k

            # Update Total Global
            total_ns[0] += item['ns_d']
            total_ns[1] += item['ns_k']
            total_ajp[0] += item['ajp_d']
            total_ajp[1] += item['ajp_k']
            total_nsd[0] += nsd_d
            total_nsd[1] += nsd_k
            total_lr[0] += lr_d
            total_lr[1] += lr_k
            total_ner[0] += ner_d
            total_ner[1] += ner_k
            
            self.tree.insert("", "end", values=(
                kode,
                item['nama'],
                _format_rupiah(item['ns_d']),
                _format_rupiah(item['ns_k']),
                _format_rupiah(item['ajp_d']),
                _format_rupiah(item['ajp_k']),
                _format_rupiah(nsd_d),
                _format_rupiah(nsd_k),
                _format_rupiah(lr_d),
                _format_rupiah(lr_k),
                _format_rupiah(ner_d),
                _format_rupiah(ner_k),
            ))

        # === BARIS TOTAL SEBELUM LABA/RUGI ===
        self._insert_total_row(
            "TOTAL SEBELUM LR", 
            total_ns, total_ajp, total_nsd, total_lr, total_ner, 'subtotal'
        )

        # === HITUNG LABA RUGI BERSIH ===
        laba_bersih = total_lr[1] - total_lr[0] # (Pendapatan - Beban)

        lr_balance_d, lr_balance_k, ner_balance_d, ner_balance_k = 0, 0, 0, 0
        keterangan = "NIHIL" 

        if laba_bersih > 0:
            lr_balance_d = laba_bersih
            ner_balance_k = laba_bersih
            formatted_laba = _format_rupiah(laba_bersih)
            keterangan = f"LABA BERSIH (Rp{formatted_laba})"
        elif laba_bersih < 0:
            rugi_bersih = abs(laba_bersih)
            lr_balance_k = rugi_bersih
            ner_balance_d = rugi_bersih
            formatted_rugi = _format_rupiah(rugi_bersih)
            keterangan = f"RUGI BERSIH (Rp{formatted_rugi})"
        
        total_lr[0] += lr_balance_d
        total_lr[1] += lr_balance_k
        total_ner[0] += ner_balance_d
        total_ner[1] += ner_balance_k

        # === BARIS LABA/RUGI ===
        self.tree.insert("", "end", values=(
            "",
            keterangan,
            "", "", "", "", "", "",
            _format_rupiah(lr_balance_d),
            _format_rupiah(lr_balance_k),
            _format_rupiah(ner_balance_d),
            _format_rupiah(ner_balance_k),
        ), tags=('laba_rugi',))
        
        # === BARIS TOTAL AKHIR ===
        self._insert_total_row(
            "TOTAL AKHIR", 
            total_ns, total_ajp, total_nsd, total_lr, total_ner, 'grand_total'
        )

        self.tree.tag_configure('subtotal', font=('Helvetica', 10, 'bold'), background='#F0F0F0') 
        self.tree.tag_configure('laba_rugi', font=('Helvetica', 10, 'italic'), background='#E0F7FA')
        self.tree.tag_configure('grand_total', font=('Helvetica', 11, 'bold'), background='#B3E5FC')
        
        if (total_ns[0] == total_ns[1] and total_ajp[0] == total_ajp[1] and 
            total_nsd[0] == total_nsd[1] and total_lr[0] == total_lr[1] and 
            total_ner[0] == total_ner[1]):
            messagebox.showinfo("Sukses", "Kertas Kerja berhasil dimuat dan SEIMBANG.")
        else:
            messagebox.showwarning("Peringatan", "Kertas Kerja **TIDAK SEIMBANG**! Periksa entri dan perhitungan Anda.")


    def _insert_total_row(self, label, total_ns, total_ajp, total_nsd, total_lr, total_ner, tag):
        self.tree.insert("", "end", values=(
            "",
            label,
            _format_rupiah(total_ns[0]),
            _format_rupiah(total_ns[1]),
            _format_rupiah(total_ajp[0]),
            _format_rupiah(total_ajp[1]),
            _format_rupiah(total_nsd[0]),
            _format_rupiah(total_nsd[1]),
            _format_rupiah(total_lr[0]),
            _format_rupiah(total_lr[1]),
            _format_rupiah(total_ner[0]),
            _format_rupiah(total_ner[1]),
        ), tags=(tag,))