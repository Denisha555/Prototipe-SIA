import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, date
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

def _get_closing_date(bulan_num, tahun):
    try:
        from calendar import monthrange
        _, last_day = monthrange(int(tahun), int(bulan_num))
        return f"{tahun}-{bulan_num}-{last_day:02d}"
    except Exception:
        return f"{tahun}-{bulan_num}-30"

class JurnalPenutupPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        now = datetime.now()
        bulan_sekarang_eng = now.strftime("%B")
        tahun_sekarang = str(now.year)
        english_to_indo = {
            "January": "Januari", "February": "Februari", "March": "Maret",
            "April": "April", "May": "Mei", "June": "Juni", "July": "Juli",
            "August": "Agustus", "September": "September", "October": "Oktober",
            "November": "November", "December": "Desember"
        }
        bulan_sekarang = english_to_indo.get(bulan_sekarang_eng, "Januari")

        ttk.Label(
            self, text="📝 Laporan Jurnal Penutup", font=("Helvetica", 18, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=15)

        # --- FORM INPUT ---
        ttk.Label(self, text="Periode Bulan:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.combo_bulan = ttk.Combobox(self, values=list(bulan_map.keys()), state="readonly", width=25)
        self.combo_bulan.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.combo_bulan.set(bulan_sekarang)

        ttk.Label(self, text="Periode Tahun:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_tahun = ttk.Entry(self, width=28)
        self.entry_tahun.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.entry_tahun.insert(0, tahun_sekarang)

        ttk.Button(self, text="Tampilkan", command=self.tampil).grid(row=3, column=0, columnspan=2, pady=15)

        cols = ("tanggal", "keterangan", "kode_akun", "debit", "kredit")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=15)
        
        self.tree.heading("tanggal", text="Tanggal")
        self.tree.heading("keterangan", text="Keterangan")
        self.tree.heading("kode_akun", text="Kode")
        self.tree.heading("debit", text="Debit (Rp)")
        self.tree.heading("kredit", text="Kredit (Rp)")

        self.tree.column("tanggal", width=80, anchor="center")
        self.tree.column("keterangan", width=220, anchor="w")
        self.tree.column("kode_akun", width=60, anchor="center")
        self.tree.column("debit", width=120, anchor="e")
        self.tree.column("kredit", width=120, anchor="e")
        
        self.tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
        ttk.Button(self, text="Kembali Ke Menu Utama", command=lambda: controller.show_frame("Menu Utama Manager")).grid(row=5, column=0, columnspan=2, pady=10)
        
    def _get_period_balances(self, bulan_num, tahun):
        conn = _connect_db()
        c = conn.cursor()

        query_accounts = """
            SELECT kode_akun, nama_akun, kategori
            FROM akun 
            WHERE kategori IN ('Pendapatan', 'Beban') OR nama_akun LIKE 'Prive%'
            ORDER BY kode_akun ASC
        """
        c.execute(query_accounts)
        all_accounts = c.fetchall()
        
        balances = {}

        for kode_akun, nama_akun, kategori in all_accounts:
            query_ju = """
                SELECT SUM(debit), SUM(kredit)
                FROM jurnal_umum_detail
                WHERE kode_akun = ?
                  AND strftime('%m', tanggal) = ?
                  AND strftime('%Y', tanggal) = ?
                  AND jenis_jurnal NOT IN ('PENYESUAIAN', 'PENUTUP') 
            """
            c.execute(query_ju, (kode_akun, bulan_num, tahun))
            ju_d, ju_k = c.fetchone()
            ju_d = ju_d if ju_d is not None else 0
            ju_k = ju_k if ju_k is not None else 0
            
            query_ajp = """
                SELECT SUM(debit), SUM(kredit)
                FROM transaksi_penyesuaian
                WHERE kode_akun = ?
                  AND strftime('%m', tanggal) = ?
                  AND strftime('%Y', tanggal) = ?
            """
            c.execute(query_ajp, (kode_akun, bulan_num, tahun))
            ajp_d, ajp_k = c.fetchone()
            ajp_d = ajp_d if ajp_d is not None else 0
            ajp_k = ajp_k if ajp_k is not None else 0
            net_debit = ju_d + ajp_d
            net_kredit = ju_k + ajp_k
            
            if kategori == 'Pendapatan' or kode_akun.startswith('4'):
                net_balance = net_kredit - net_debit
            else:
                net_balance = net_debit - net_kredit
            
            if net_balance > 0:
                balances[kode_akun] = {
                    'nama': nama_akun,
                    'kategori': kategori,
                    'net_balance': net_balance
                }
        
        conn.close()
        return balances

    def tampil(self):
        bulan_nama = self.combo_bulan.get()
        tahun = self.entry_tahun.get().strip()

        if not bulan_nama or not tahun:
            messagebox.showerror("Error", "Bulan dan Tahun harus diisi.")
            return
        try:
            bulan_num = bulan_map[bulan_nama]
            int(tahun)
        except Exception:
            messagebox.showerror("Error", "Input Bulan/Tahun tidak valid.")
            return

        # Hapus data lama di Treeview
        self.tree.delete(*self.tree.get_children())

        # Ambil Saldo Nominal dan Prive
        balances = self._get_period_balances(bulan_num, tahun)
        
        # Hitung Total Laba/Rugi
        pendapatan_to_close = {k: v['net_balance'] for k, v in balances.items() if v['kategori'] == 'Pendapatan'}
        beban_to_close = {k: v['net_balance'] for k, v in balances.items() if v['kategori'] == 'Beban'}
        prive_to_close = {k: v['net_balance'] for k, v in balances.items() if 'Prive' in v['nama']}
        
        total_pendapatan = sum(pendapatan_to_close.values())
        total_beban = sum(beban_to_close.values())
        total_prive = sum(prive_to_close.values())
        
        laba_bersih = total_pendapatan - total_beban
        
        if total_pendapatan == 0 and total_beban == 0 and total_prive == 0:
            messagebox.showinfo("Info", "Tidak ada akun nominal (Pendapatan, Beban, Prive) yang perlu ditutup untuk periode ini.")
            return

        # Generate Jurnal Penutup
        closing_entries = []
        tanggal_penutup = _get_closing_date(bulan_num, tahun)
        
        ILL_KODE = "600"
        MODAL_KODE = "311"
        MODAL_NAMA = "Modal Pemilik"
        ILL_NAMA = "Ikhtisar Laba/Rugi"

        if total_pendapatan > 0:
            closing_entries.append(("", "Menutup Akun Pendapatan", "", "", "", 'header'))
            for kode, amount in pendapatan_to_close.items():
                nama = balances[kode]['nama']
                closing_entries.append((tanggal_penutup, f"  {nama}", kode, _format_rupiah(amount), "", ''))
            closing_entries.append((tanggal_penutup, f"  {ILL_NAMA}", ILL_KODE, "", _format_rupiah(total_pendapatan), 'subentry'))
            closing_entries.append(("", "", "", "", "", 'spacer'))

        # Menutup Akun Beban
        if total_beban > 0:
            closing_entries.append(("", "Menutup Akun Beban", "", "", "", 'header'))
            closing_entries.append((tanggal_penutup, f"  {ILL_NAMA}", ILL_KODE, _format_rupiah(total_beban), "", ''))
            for kode, amount in beban_to_close.items():
                nama = balances[kode]['nama']
                closing_entries.append((tanggal_penutup, f"  {nama}", kode, "", _format_rupiah(amount), 'subentry'))
            closing_entries.append(("", "", "", "", "", 'spacer'))

        # Menutup ILL
        if laba_bersih != 0:
            ket = "Laba Bersih" if laba_bersih > 0 else "Rugi Bersih"
            closing_entries.append(("", f"Menutup Ikhtisar {ket}", "", "", "", 'header'))
            if laba_bersih > 0:
                closing_entries.append((tanggal_penutup, f"  {ILL_NAMA}", ILL_KODE, _format_rupiah(laba_bersih), "", ''))
                closing_entries.append((tanggal_penutup, f"  {MODAL_NAMA}", MODAL_KODE, "", _format_rupiah(laba_bersih), 'subentry'))
            else:
                rugi = abs(laba_bersih)
                closing_entries.append((tanggal_penutup, f"  {MODAL_NAMA}", MODAL_KODE, _format_rupiah(rugi), "", ''))
                closing_entries.append((tanggal_penutup, f"  {ILL_NAMA}", ILL_KODE, "", _format_rupiah(rugi), 'subentry'))
            closing_entries.append(("", "", "", "", "", 'spacer'))

        # Menutup Akun Prive
        if total_prive > 0:
            closing_entries.append(("", "Menutup Akun Prive", "", "", "", 'header'))
            prive_kode = next(iter(prive_to_close))
            prive_nama = balances[prive_kode]['nama']
            closing_entries.append((tanggal_penutup, f"  {MODAL_NAMA}", MODAL_KODE, _format_rupiah(total_prive), "", ''))
            closing_entries.append((tanggal_penutup, f"  {prive_nama}", prive_kode, "", _format_rupiah(total_prive), 'subentry'))

        for tanggal, nama, kode, debit, kredit, tag in closing_entries:
            self.tree.insert("", "end", values=(tanggal, nama, kode, debit, kredit), tags=(tag,))
        
        # Konfigurasi Gaya
        self.tree.tag_configure("header", font=('Helvetica', 10, 'bold'), background='#B3E5FC', foreground='#000000')
        self.tree.tag_configure("subentry", background='#F5F5F5')
        self.tree.tag_configure("spacer", background='white')