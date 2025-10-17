import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
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

def _format_rupiah_util(amount):
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
        WHERE (a.kategori IN ('Pendapatan', 'Beban') OR a.kode_akun = '312') 
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

        ttk.Button(self, text="Kembali ke Menu Utama", command=lambda: controller.show_frame("Menu Utama Manager")
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
        self.bb_frame = ttk.LabelFrame(self, text="Rincian Buku Besar")
        self.bb_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        self.bb_frame.grid_columnconfigure(0, weight=1)
        self.bb_frame.grid_rowconfigure(0, weight=1)
        
        self.current_treeviews = []
        
        self._create_empty_treeview(self.bb_frame)

    # FUNGSI JURNAL PENUTUP
    def _calculate_closing_entries(self, balances, bulan_num, tahun):
        """Menghitung entri jurnal penutup."""
        tanggal_penutup = _get_closing_date(bulan_num, tahun)
        closing_entries = []
        total_debit = 0
        total_kredit = 0
        
        # Menutup Akun Pendapatan
        pendapatan_to_close = {k: v for k, v in balances.items() if k.startswith('4') and v['saldo'] > 0}
        total_pendapatan = sum(item['saldo'] for item in pendapatan_to_close.values())

        if total_pendapatan > 0:
            closing_entries.append(("", "Menutup Akun Pendapatan", "", "", "", 'header'))
            closing_entries.append((tanggal_penutup, f"  {ILL_NAMA}", ILL_KODE, "", _format_rupiah_util(total_pendapatan), 'subentry'))
            total_kredit += total_pendapatan
            for kode, item in pendapatan_to_close.items():
                closing_entries.append((tanggal_penutup, item['nama'], kode, _format_rupiah_util(item['saldo']), "", ''))
                total_debit += item['saldo']
        closing_entries.append(("", "", "", "", "", 'spacer'))

        # Menutup Akun Beban
        beban_to_close = {k: v for k, v in balances.items() if k.startswith('5') and v['saldo'] > 0}
        total_beban = sum(abs(item['saldo']) for item in beban_to_close.values())

        if total_beban > 0:
            closing_entries.append(("", "Menutup Akun Beban", "", "", "", 'header'))
            closing_entries.append((tanggal_penutup, ILL_NAMA, ILL_KODE, _format_rupiah_util(total_beban), "", ''))
            total_debit += total_beban
            for kode, item in beban_to_close.items():
                saldo_abs = abs(item['saldo'])
                closing_entries.append((tanggal_penutup, f"  {item['nama']}", kode, "", _format_rupiah_util(saldo_abs), 'subentry'))
                total_kredit += saldo_abs
        closing_entries.append(("", "", "", "", "", 'spacer'))
        
        # Menutup Ikhtisar Laba/Rugi ke Modal
        laba_bersih = total_pendapatan - total_beban
        
        if laba_bersih != 0:
            closing_entries.append(("", "Menutup Ikhtisar Laba/Rugi ke Modal", "", "", "", 'header'))
            if laba_bersih > 0: # Laba
                closing_entries.append((tanggal_penutup, ILL_NAMA, ILL_KODE, _format_rupiah_util(laba_bersih), "", ''))
                closing_entries.append((tanggal_penutup, f"  {MODAL_NAMA}", MODAL_KODE, "", _format_rupiah_util(laba_bersih), 'subentry'))
                total_debit += laba_bersih
                total_kredit += laba_bersih
            else: # Rugi
                rugi = abs(laba_bersih)
                closing_entries.append((tanggal_penutup, MODAL_NAMA, MODAL_KODE, _format_rupiah_util(rugi), "", ''))
                closing_entries.append((tanggal_penutup, f"  {ILL_NAMA}", ILL_KODE, "", _format_rupiah_util(rugi), 'subentry'))
                total_debit += rugi
                total_kredit += rugi
            closing_entries.append(("", "", "", "", "", 'spacer'))

        # Menutup Akun Prive
        prive_to_close = {k: v for k, v in balances.items() if k == '312' and v['saldo'] > 0}
        total_prive = sum(abs(item['saldo']) for item in prive_to_close.values())

        if total_prive > 0:
            closing_entries.append(("", "Menutup Akun Prive", "", "", "", 'header'))
            prive_kode = '312'
            prive_nama = self.akun_map.get(f"{prive_kode} - Prive Pemilik", {}).get('nama', 'Prive Pemilik')
            
            closing_entries.append((tanggal_penutup, MODAL_NAMA, MODAL_KODE, _format_rupiah_util(total_prive), "", ''))
            closing_entries.append((tanggal_penutup, f"  {prive_nama}", prive_kode, "", _format_rupiah_util(total_prive), 'subentry'))
            
            total_debit += total_prive
            total_kredit += total_prive
            
        return closing_entries, total_debit, total_kredit

    def _auto_post_jurnal_penutup(self, bulan_num, tahun):
        balances = _get_account_balances_for_closing(bulan_num, tahun)
        entries_to_post, total_debit, total_kredit = self._calculate_closing_entries(balances, bulan_num, tahun)
        
        if total_debit != total_kredit:
            return False 
            
        conn = _connect_db()
        c = conn.cursor()
        
        try:
            # Hapus Jurnal Penutup lama
            c.execute("""
                DELETE FROM jurnal_umum_detail 
                WHERE jenis_jurnal = ? AND strftime('%m', tanggal) = ? AND strftime('%Y', tanggal) = ?
            """, (JENIS_JURNAL, bulan_num, tahun))

            # Posting Entri baru
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
            return True
            
        except sqlite3.Error as e:
            conn.rollback()
            return False
        finally:
            conn.close()

    def _create_empty_treeview(self, parent_frame):
        tree = ttk.Treeview(parent_frame, columns=("tanggal", "keterangan", "debit", "kredit", "saldo"), show="headings")
        tree.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        parent_frame.grid_rowconfigure(2, weight=1)
        
        tree.column("tanggal", width=150, anchor=tk.CENTER)
        tree.heading("tanggal", text="Tanggal")
        tree.column("keterangan", width=240, anchor=tk.W)
        tree.heading("keterangan", text="Keterangan")
        tree.column("debit", width=150, anchor=tk.E)
        tree.heading("debit", text="Debit (Rp)")
        tree.column("kredit", width=150, anchor=tk.E)
        tree.heading("kredit", text="Kredit (Rp)")
        tree.column("saldo", width=170, anchor=tk.E)
        tree.heading("saldo", text="Saldo (Rp)")
        
        # Scrollbar
        vsb = ttk.Scrollbar(parent_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=2, column=1, sticky="ns")

        tree.tag_configure('info', foreground='gray')
        
        self.current_treeviews = [tree]
        
    def _format_rupiah(self, amount):
        if amount == 0:
            return ""
        is_negative = amount < 0
        abs_amount = abs(amount)
        formatted = f"{int(abs_amount):,.0f}".replace(",", "#").replace(".", ",").replace("#", ".")
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
            query = """
                SELECT SUM(debit) - SUM(kredit)
                FROM jurnal_umum_detail
                WHERE kode_akun = ? 
                  AND tanggal < ?
                  -- Hanya UMUM dan PENYESUAIAN yang membentuk Saldo Awal, PENUTUP hanya memengaruhi bulan itu.
                  AND (jenis_jurnal IS NULL OR jenis_jurnal NOT IN ('PENUTUP')) 
            """
            c.execute(query, (kode_akun, f"{year}-{bulan_num}-01"))
            
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
            SELECT tanggal, keterangan, debit, kredit, jenis_jurnal
            FROM jurnal_umum_detail
            WHERE kode_akun = ? 
            AND strftime('%m', tanggal) = ?
            AND strftime('%Y', tanggal) = ?
            -- Sudah mencakup PENUTUP
            AND (jenis_jurnal IS NULL OR jenis_jurnal IN ('UMUM', 'PENYESUAIAN', 'PENUTUP'))
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

        bulan_num = bulan_map[selected_bulan]
        
        self._auto_post_jurnal_penutup(bulan_num, selected_tahun)

        saldo_awal = self._get_beginning_balance(kode_akun, selected_tahun, selected_bulan)
        transaksi_bulanan = self._get_monthly_transactions(kode_akun, selected_tahun, selected_bulan)

        if not transaksi_bulanan and saldo_awal == 0:
            messagebox.showinfo("Info", f"Tidak ada transaksi untuk akun {kode_akun} pada periode ini.")
            self._create_empty_treeview(self.bb_frame)
            return
            
        self.bb_frame.config(text=f"Rincian Buku Besar: {kode_akun} - {nama_akun}")

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
            "SALDO AWAL",
            "", 
            "",
            self._format_rupiah(saldo_berjalan)
        ), tags=('saldo_awal',))
        tree.tag_configure('saldo_awal', font=('Helvetica', 10, 'bold'), background='#F0F0F0')
        
        for tgl, ket, debit, kredit, jenis in transaksi_bulanan:
            debit = debit or 0
            kredit = kredit or 0

            # Hitung saldo berjalan
            if saldo_normal == 'Debit':
                saldo_berjalan += debit - kredit
            else:
                saldo_berjalan += kredit - debit
                
            total_debit += debit
            total_kredit += kredit

            if jenis == 'PENYESUAIAN':
                keterangan_tampil = f"AJP {ket}"
                tag_style = 'penyesuaian'
            elif jenis == 'PENUTUP':
                keterangan_tampil = f"JP {ket}"
                tag_style = 'penutup'
            else:
                keterangan_tampil = ket
                tag_style = ''
                
            tree.insert("", "end", values=(
                tgl,
                keterangan_tampil,
                self._format_rupiah(debit) if debit else "",
                self._format_rupiah(kredit) if kredit else "",
                self._format_rupiah(saldo_berjalan)
            ), tags=(tag_style,))
            
        tree.insert("", "end", values=(
            "", 
            "SALDO AKHIR", 
            self._format_rupiah(total_debit),
            self._format_rupiah(total_kredit),
            self._format_rupiah(saldo_berjalan)
        ), tags=('saldo_akhir',))

        tree.tag_configure('saldo_akhir', font=('Helvetica', 11, 'bold'), background='#E0F7FA')
        
        self.current_treeviews.append(tree)