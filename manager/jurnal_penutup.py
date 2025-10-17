import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, date
from calendar import monthrange 

try:
    from function.bulan_map import bulan_map
except ImportError:
    bulan_map = {
        "Januari": "01", "Februari": "02", "Maret": "03", 
        "April": "04", "Mei": "05", "Juni": "06",
        "Juli": "07", "Agustus": "08", "September": "09",
        "Oktober": "10", "November": "11", "Desember": "12"
    }

ILL_KODE = '313'
ILL_NAMA = 'Ikhtisar Laba/Rugi' 
MODAL_KODE = '311'
MODAL_NAMA = 'Modal Pemilik'
JENIS_JURNAL = 'PENUTUP'

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
        _, last_day = monthrange(int(tahun), int(bulan_num))
        return f"{tahun}-{bulan_num}-{last_day:02d}"
    except Exception:
        return f"{tahun}-{bulan_num}-30"

def _get_account_balances_for_closing(bulan_num, tahun):
    conn = _connect_db()
    c = conn.cursor()

    c.execute("SELECT kode_akun FROM akun WHERE kode_akun = ?", (ILL_KODE,))
    if not c.fetchone():
        c.execute("INSERT INTO akun (kode_akun, nama_akun, kategori, saldo_normal) VALUES (?, ?, 'Ekuitas', 'Kredit')", (ILL_KODE, ILL_NAMA))
        conn.commit()
    
    query = """
        SELECT a.kode_akun, a.nama_akun, a.saldo_normal, 
                SUM(CASE WHEN jd.jenis_jurnal != 'PENUTUP' THEN jd.debit ELSE 0 END) AS total_debit, 
                SUM(CASE WHEN jd.jenis_jurnal != 'PENUTUP' THEN jd.kredit ELSE 0 END) AS total_kredit
        FROM akun a
        LEFT JOIN jurnal_umum_detail jd ON a.kode_akun = jd.kode_akun
        WHERE a.kategori IN ('Pendapatan', 'Beban', 'Ekuitas') AND a.kode_akun IN ('312', '401', '511', '512', '513', '514', '520')
          AND strftime('%m', jd.tanggal) = ?
          AND strftime('%Y', jd.tanggal) = ?
        GROUP BY a.kode_akun, a.nama_akun, a.saldo_normal
    """
    c.execute(query, (bulan_num, tahun))
    rows = c.fetchall()
    conn.close()

    balances = {}
    for kode, nama, sn, debit, kredit in rows:
        debit = debit or 0
        kredit = kredit or 0
        
        if sn == 'Kredit':
            saldo = kredit - debit
        else: 
            saldo = debit - kredit

        balances[kode] = {
            'nama': nama,
            'saldo': saldo
        }
    return balances


class JurnalPenutupPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ttk.Button(self, 
                   text="Kembali ke Menu Utama", 
                   command=lambda: self.controller.show_frame("Menu Utama Manager"),
                   style="Back.TButton").grid(
                       row=0, column=0, sticky="w", padx=20, pady=(10, 0)
                   )

        ttk.Label(self, text="🔄 Jurnal Penutup", font=("Helvetica", 18, "bold")).grid(row=1, column=0, columnspan=2, pady=(15, 10))

        form_frame = ttk.Frame(self)
        form_frame.grid(row=2, column=0, columnspan=2, pady=5)
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)
        
        bulan_list = list(bulan_map.keys())

        ttk.Label(form_frame, text="Bulan: ").grid(row=0, column=0, sticky="e", pady=5)
        self.combo_bulan = ttk.Combobox(form_frame, width=27, state="readonly", values=bulan_list)
        self.combo_bulan.grid(row=0, column=1, sticky="w", pady=5)
        
        now = datetime.now()
        bulan_num_sekarang = now.strftime("%m")
        bulan_map_terbalik = {v: k for k, v in bulan_map.items()}
        bulan_nama_sekarang = bulan_map_terbalik.get(bulan_num_sekarang)

        if bulan_nama_sekarang:
            self.combo_bulan.set(bulan_nama_sekarang)

        ttk.Label(form_frame, text="Tahun: ").grid(row=1, column=0, sticky="e", pady=5)
        self.entry_tahun = ttk.Entry(form_frame, width=30)
        self.entry_tahun.grid(row=1, column=1, sticky="w", pady=5)
        self.entry_tahun.insert(0, str(now.year))

        ttk.Button(self, text="Tampilkan", command=self.tampilkan_jurnal_penutup).grid(row=3, column=0, columnspan=2, pady=10)
        
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=4, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=("tanggal", "keterangan", "kode_akun", "debit", "kredit"), show="headings", height=15)
        self.tree.heading("tanggal", text="Tanggal", anchor="w")
        self.tree.heading("keterangan", text="Keterangan", anchor="w")
        self.tree.heading("kode_akun", text="Kode Akun", anchor="w")
        self.tree.heading("debit", text="Debit (Rp)", anchor="e")
        self.tree.heading("kredit", text="Kredit (Rp)", anchor="e")
        self.tree.column("tanggal", width=90)
        self.tree.column("keterangan", width=250)
        self.tree.column("kode_akun", width=90)
        self.tree.column("debit", width=120, anchor="e")
        self.tree.column("kredit", width=120, anchor="e")
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns")

    def _recalculate_and_save_jurnal_penutup(self, bulan_num, tahun):
        balances = _get_account_balances_for_closing(bulan_num, tahun)
        entries_to_post, total_debit, total_kredit = self._calculate_closing_entries(balances, bulan_num, tahun)
        
        if total_debit != total_kredit:
            return False, entries_to_post, total_debit, total_kredit
            
        conn = _connect_db()
        c = conn.cursor()
        
        try:
            c.execute("""
                DELETE FROM jurnal_umum_detail 
                WHERE jenis_jurnal = ? AND strftime('%m', tanggal) = ? AND strftime('%Y', tanggal) = ?
            """, (JENIS_JURNAL, bulan_num, tahun))

            transaksi_id = f"JP-{tahun}{bulan_num}-{datetime.now().strftime('%H%M%S')}"

            for tanggal, nama, kode, debit, kredit, tag in entries_to_post:
                if tag in ('header', 'spacer', 'total'):
                    continue
                    
                debit_val = int(str(debit).replace('.', '').replace(',', '') or 0)
                kredit_val = int(str(kredit).replace('.', '').replace(',', '') or 0)
                
                keterangan_db = nama.strip()
                if keterangan_db.startswith('  '):
                    keterangan_db = keterangan_db[2:] 

                if debit_val > 0 or kredit_val > 0:
                    c.execute("""
                        INSERT INTO jurnal_umum_detail 
                        (transaksi_ref_id, tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (transaksi_id, tanggal, kode, keterangan_db, debit_val, kredit_val, JENIS_JURNAL))

            conn.commit()
            return True, entries_to_post, total_debit, total_kredit
            
        except sqlite3.Error as e:
            messagebox.showerror("Error Database", f"Gagal menyimpan Jurnal Penutup: {e}")
            conn.rollback()
            return False, entries_to_post, total_debit, total_kredit
        finally:
            conn.close()


    def tampilkan_jurnal_penutup(self):
        
        bulan_nama = self.combo_bulan.get()
        tahun = self.entry_tahun.get().strip()

        if not bulan_nama or not tahun:
            messagebox.showerror("Error", "Bulan dan Tahun harus diisi!")
            return

        try:
            bulan_num = bulan_map[bulan_nama]
        except KeyError:
            messagebox.showerror("Error", "Bulan tidak valid.")
            return

        is_posted, closing_entries, total_debit, total_kredit = self._recalculate_and_save_jurnal_penutup(bulan_num, tahun)
        
        self.tree.delete(*self.tree.get_children())
        
        for tanggal, nama, kode, debit, kredit, tag in closing_entries:
            self.tree.insert("", "end", values=(tanggal, nama, kode, debit, kredit), tags=(tag,))
            
        # Tampilkan Total
        self.tree.insert("", "end", values=("", "TOTAL", "", _format_rupiah(total_debit), _format_rupiah(total_kredit)), tags=('total',))
        
        self.tree.tag_configure('header', font=('Helvetica', 10, 'bold'), background='#E9ECEF', foreground='#495057')
        self.tree.tag_configure('subentry', foreground='#495057')
        self.tree.tag_configure('spacer', background='#FFFFFF')
        self.tree.tag_configure('total', font=('Helvetica', 10, 'bold'), background='#E0F7FA')
        
        if total_debit != total_kredit:
            messagebox.showwarning("Peringatan", "Jurnal Penutup TIDAK SEIMBANG! Posting ke database dibatalkan. Periksa Jurnal Umum/Penyesuaian.")
        elif not is_posted:
             messagebox.showerror("Error Posting", "Gagal menyimpan Jurnal Penutup. Periksa log database.")

    def _calculate_closing_entries(self, balances, bulan_num, tahun):
        tanggal_penutup = _get_closing_date(bulan_num, tahun)
        closing_entries = []
        total_debit = 0
        total_kredit = 0
        
        # Menutup Akun Pendapatan (Debit Pendapatan, Kredit ILL)
        pendapatan_to_close = {k: v for k, v in balances.items() if k.startswith('4') and v['saldo'] > 0}
        total_pendapatan = sum(item['saldo'] for item in pendapatan_to_close.values())

        if total_pendapatan > 0:
            closing_entries.append(("", "Menutup Akun Pendapatan", "", "", "", 'header'))
            
            # Entri Kredit: Ikhtisar Laba/Rugi
            closing_entries.append((tanggal_penutup, f"  {ILL_NAMA}", ILL_KODE, "", _format_rupiah(total_pendapatan), 'subentry'))
            total_kredit += total_pendapatan

            # Entri Debit: Akun Pendapatan
            for kode, item in pendapatan_to_close.items():
                closing_entries.append((tanggal_penutup, item['nama'], kode, _format_rupiah(item['saldo']), "", ''))
                total_debit += item['saldo']
        closing_entries.append(("", "", "", "", "", 'spacer'))

        # Menutup Akun Beban (Debit ILL, Kredit Beban)
        beban_to_close = {k: v for k, v in balances.items() if k.startswith('5') and v['saldo'] > 0}
        total_beban = sum(abs(item['saldo']) for item in beban_to_close.values())

        if total_beban > 0:
            closing_entries.append(("", "Menutup Akun Beban", "", "", "", 'header'))
            
            # Entri Debit: Ikhtisar Laba/Rugi
            closing_entries.append((tanggal_penutup, ILL_NAMA, ILL_KODE, _format_rupiah(total_beban), "", ''))
            total_debit += total_beban

            # Entri Kredit: Akun Beban
            for kode, item in beban_to_close.items():
                saldo_abs = abs(item['saldo'])
                closing_entries.append((tanggal_penutup, f"  {item['nama']}", kode, "", _format_rupiah(saldo_abs), 'subentry'))
                total_kredit += saldo_abs
        closing_entries.append(("", "", "", "", "", 'spacer'))
        
        # Menutup Ikhtisar Laba/Rugi ke Modal
        laba_bersih = total_pendapatan - total_beban
        
        if laba_bersih != 0:
            closing_entries.append(("", "Menutup Ikhtisar Laba/Rugi ke Modal", "", "", "", 'header'))
            
            if laba_bersih > 0: # Laba (Debit ILL, Kredit Modal)
                closing_entries.append((tanggal_penutup, ILL_NAMA, ILL_KODE, _format_rupiah(laba_bersih), "", ''))
                closing_entries.append((tanggal_penutup, f"  {MODAL_NAMA}", MODAL_KODE, "", _format_rupiah(laba_bersih), 'subentry'))
                total_debit += laba_bersih
                total_kredit += laba_bersih
            else: # Rugi (Debit Modal, Kredit ILL)
                rugi = abs(laba_bersih)
                closing_entries.append((tanggal_penutup, MODAL_NAMA, MODAL_KODE, _format_rupiah(rugi), "", ''))
                closing_entries.append((tanggal_penutup, f"  {ILL_NAMA}", ILL_KODE, "", _format_rupiah(rugi), 'subentry'))
                total_debit += rugi
                total_kredit += rugi
            closing_entries.append(("", "", "", "", "", 'spacer'))

        # Menutup Akun Prive
        prive_to_close = {k: v for k, v in balances.items() if k.startswith('312') and v['saldo'] > 0}
        total_prive = sum(abs(item['saldo']) for item in prive_to_close.values())

        if total_prive > 0:
            closing_entries.append(("", "Menutup Akun Prive", "", "", "", 'header'))
            prive_kode = next(iter(prive_to_close))
            prive_nama = prive_to_close[prive_kode]['nama']
            
            # Entri Debit: Modal 
            closing_entries.append((tanggal_penutup, MODAL_NAMA, MODAL_KODE, _format_rupiah(total_prive), "", ''))
            
            # Entri Kredit: Prive
            closing_entries.append((tanggal_penutup, f"  {prive_nama}", prive_kode, "", _format_rupiah(total_prive), 'subentry'))
            
            total_debit += total_prive
            total_kredit += total_prive
            
        return closing_entries, total_debit, total_kredit