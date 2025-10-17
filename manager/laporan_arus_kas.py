import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime

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
    """Fungsi format Rupiah sederhana tanpa simbol negatif."""
    try:
        amount = int(amount)
        if amount == 0:
            return ""
        formatted = f"{abs(amount):,}".replace(",", "#").replace(".", ",").replace("#", ".")
        return formatted
    except (TypeError, ValueError):
        return ""

# === CLASS UTAMA LAPORAN ARUS KAS ===
class LaporanArusKasPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Ambil bulan & tahun saat ini
        now = datetime.datetime.now()
        bulan_sekarang = now.strftime("%B")  # nama bulan (English)
        tahun_sekarang = str(now.year)

        if bulan_sekarang not in bulan_map:
            eng_to_id = {
                "January": "Januari", "February": "Februari", "March": "Maret",
                "April": "April", "May": "Mei", "June": "Juni", "July": "Juli",
                "August": "Agustus", "September": "September", "October": "Oktober",
                "November": "November", "December": "Desember"
            }
            bulan_sekarang = eng_to_id.get(bulan_sekarang, bulan_sekarang)

        ttk.Label(self, text="📊 Laporan Arus Kas", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self, text="Bulan:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.combo_bulan = ttk.Combobox(self, values=list(bulan_map.keys()), state="readonly", width=25)
        self.combo_bulan.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.combo_bulan.set(bulan_sekarang)

        ttk.Label(self, text="Tahun:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_tahun = ttk.Entry(self, width=28)
        self.entry_tahun.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.entry_tahun.insert(0, tahun_sekarang)

        ttk.Button(self, text="Tampilkan", command=self.tampil).grid(row=3, column=0, columnspan=2, pady=10)

        self.treeview = ttk.Treeview(self, columns=("keterangan", "nominal", 'subtotal'), show="headings", height=15)
        self.treeview.heading("keterangan", text="Keterangan")
        self.treeview.heading("nominal", text="Nominal (Rp)")
        self.treeview.heading("subtotal", text="Subtotal (Rp)")
        self.treeview.column("keterangan", width=280)
        self.treeview.column("nominal", width=120, anchor="e")
        self.treeview.column("subtotal", width=120, anchor="e")
        self.treeview.grid(row=4, column=0, columnspan=2, pady=10, padx=20, sticky="nsew")

        ttk.Button(self, text="Kembali ke Menu Utama", command=lambda: controller.show_frame("Menu Utama Manager")).grid(row=5, column=0, columnspan=2, pady=10)

    # === FUNGSI AMBIL SALDO KAS AWAL ===
    def _get_cash_initial_balance(self, start_of_month_date):
        conn = _connect_db()
        c = conn.cursor()
        
        query = """
            SELECT SUM(debit) - SUM(kredit)
            FROM jurnal_umum_detail
            WHERE kode_akun = '111' 
              AND tanggal < ?
        """
        c.execute(query, (start_of_month_date,)) 
        saldo = c.fetchone()[0] or 0
        conn.close()
        return saldo

    def _get_cash_flow_data(self, bulan_num, tahun):
        conn = _connect_db()
        c = conn.cursor()
        
        query = """
            SELECT debit, kredit, keterangan, transaksi_ref_id, id 
            FROM jurnal_umum_detail
            WHERE kode_akun = '111' 
              AND strftime('%m', tanggal) = ?
              AND strftime('%Y', tanggal) = ?
        """
        c.execute(query, (bulan_num, tahun))
        cash_movements = c.fetchall()
        
        categorized_flows = {
            "operasi": {"masuk": 0, "keluar": 0, "detail": []},
            "investasi": {"masuk": 0, "keluar": 0, "detail": []},
            "pendanaan": {"masuk": 0, "keluar": 0, "detail": []},
        }
        
        for debit_kas, kredit_kas, keterangan_kas, ref_id, ju_id_kas in cash_movements:
            partner_row = None
            
            if ref_id:
                c.execute("""
                    SELECT a.kode_akun, a.nama_akun 
                    FROM jurnal_umum_detail jd
                    JOIN akun a ON jd.kode_akun = a.kode_akun
                    WHERE jd.transaksi_ref_id = ? AND jd.kode_akun != '111'
                    LIMIT 1
                """, (ref_id,))
                partner_row = c.fetchone()

            if not partner_row:
                if debit_kas > 0 and not ref_id:
                    c.execute("""
                        SELECT a.kode_akun, a.nama_akun 
                        FROM jurnal_umum_detail jd
                        JOIN akun a ON jd.kode_akun = a.kode_akun
                        WHERE jd.kode_akun LIKE '3%' -- Hanya cari Modal/Prive
                          AND jd.kredit = ?            -- Nilai Kredit sama dengan Debit Kas
                          AND jd.transaksi_ref_id IS NULL -- Jika memang NULL
                          AND strftime('%Y-%m-%d', jd.tanggal) = (SELECT strftime('%Y-%m-%d', tanggal) FROM jurnal_umum_detail WHERE id = ?)
                        LIMIT 1
                    """, (debit_kas, ju_id_kas))
                    partner_row = c.fetchone()
            # --------------------------------------------------------------------------
            
            if partner_row:
                partner_kode, partner_nama = partner_row
                
                movement = debit_kas - kredit_kas
                
                if partner_kode.startswith(('4', '5')) or partner_kode in ('112', '113', '211', '212'):
                    category = "operasi"
                elif partner_kode.startswith(('12')):
                    category = "investasi"
                elif partner_kode.startswith(('3')):
                    category = "pendanaan"
                else:
                    category = "operasi"
                
                flow_type = "masuk" if movement > 0 else "keluar"
                flow_value = abs(movement)
                categorized_flows[category][flow_type] += flow_value
                
                if flow_type == "masuk":
                    keterangan_detail = f"Penerimaan dari {partner_nama}"
                else:
                    keterangan_detail = f"Pembayaran untuk {partner_nama}"
                    
                ref_info = f" (Ref: {ref_id})" if ref_id else ""
                categorized_flows[category]["detail"].append({
                    "keterangan": f"{keterangan_detail}{ref_info}",
                    "nilai": flow_value,
                    "jenis": flow_type
                })
        
        conn.close()
        return categorized_flows


    # === Fungsi utama tampilkan laporan ===
    def tampil(self):
        bulan_nama = self.combo_bulan.get()
        tahun = self.entry_tahun.get().strip()

        if not bulan_nama or not tahun:
            messagebox.showerror("Error", "Bulan dan Tahun harus diisi!")
            return

        try:
            bulan_num = bulan_map[bulan_nama]
            tahun_int = int(tahun)
        except (KeyError, ValueError):
            messagebox.showerror("Error", "Bulan atau Tahun tidak valid.")
            return

        # Bersihkan tabel
        self.treeview.delete(*self.treeview.get_children())
        
        # Tanggal awal bulan (untuk menghitung Saldo Awal)
        start_of_month_date = f"{tahun}-{bulan_num}-01"
        
        # Ambil saldo kas awal
        saldo_kas_awal = self._get_cash_initial_balance(start_of_month_date)
        
        # Ambil dan kategorikan arus kas
        try:
            flows = self._get_cash_flow_data(bulan_num, tahun)
        except sqlite3.Error as e:
            messagebox.showerror("Error Database", f"Gagal memuat data arus kas: {e}")
            return


        total_neto = 0

        # Helper untuk memasukkan baris ke treeview
        def insert_row(keterangan, nominal="", subtotal="", tag=""):
            self.treeview.insert("", "end", values=(keterangan, nominal, subtotal), tags=(tag,))

        # Atur tag styles
        self.treeview.tag_configure('header', font=('Helvetica', 10, 'bold'), background='#D9EAF7')
        self.treeview.tag_configure('masuk', foreground='green')
        self.treeview.tag_configure('keluar', foreground='red')
        self.treeview.tag_configure('subtotal', font=('Helvetica', 10, 'bold'), background='#F0F0F0')
        self.treeview.tag_configure('total', font=('Helvetica', 11, 'bold'), background='#E0F7FA')

        insert_row(f"PERIODE {bulan_nama.upper()} {tahun}", tag='total')
        
        # ARUS KAS DARI AKTIVITAS OPERASI
        insert_row("AKTIVITAS OPERASI", tag='header')
        neto_operasi = 0
        
        if flows['operasi']['detail']:
            for flow in flows['operasi']['detail']:
                nilai_str = _format_rupiah(flow['nilai'])
                if flow['jenis'] == 'masuk':
                    insert_row(flow['keterangan'], nilai_str, tag='masuk')
                    neto_operasi += flow['nilai']
                else:
                    insert_row(flow['keterangan'], f"({nilai_str})", tag='keluar')
                    neto_operasi -= flow['nilai']
        else:
            insert_row("Tidak ada arus kas operasi bulan ini.", "","")
                
        insert_row("Neto Operasi", "", _format_rupiah(neto_operasi), tag='subtotal')
        total_neto += neto_operasi
        
        insert_row("") # Spacer

        # ARUS KAS DARI AKTIVITAS INVESTASI
        insert_row("AKTIVITAS INVESTASI", tag='header')
        neto_investasi = 0
        if flows['investasi']['detail']:
            for flow in flows['investasi']['detail']:
                nilai_str = _format_rupiah(flow['nilai'])
                if flow['jenis'] == 'masuk':
                    insert_row(flow['keterangan'], nilai_str, tag='masuk')
                    neto_investasi += flow['nilai']
                else:
                    insert_row(flow['keterangan'], f"({nilai_str})", tag='keluar')
                    neto_investasi -= flow['nilai']
        else:
            insert_row("Tidak ada arus kas investasi bulan ini.", "","")
                
        insert_row("Neto Investasi", "", _format_rupiah(neto_investasi), tag='subtotal')
        total_neto += neto_investasi
        
        insert_row("")

        # ARUS KAS DARI AKTIVITAS PENDANAAN
        insert_row("AKTIVITAS PENDANAAN", tag='header')
        neto_pendanaan = 0
        if flows['pendanaan']['detail']:
            for flow in flows['pendanaan']['detail']:
                nilai_str = _format_rupiah(flow['nilai'])
                if flow['jenis'] == 'masuk':
                    insert_row(flow['keterangan'], nilai_str, tag='masuk')
                    neto_pendanaan += flow['nilai']
                else:
                    insert_row(flow['keterangan'], f"({nilai_str})", tag='keluar')
                    neto_pendanaan -= flow['nilai']
        else:
            insert_row("Tidak ada arus kas pendanaan bulan ini.", "","")
                
        insert_row("Neto Pendanaan", "", _format_rupiah(neto_pendanaan), tag='subtotal')
        total_neto += neto_pendanaan
        
        insert_row("") # Spacer

        # KENAIKAN/PENURUNAN KAS
        keterangan_neto = "Kenaikan Kas" if total_neto >= 0 else "Penurunan Kas"
        insert_row(keterangan_neto, "", _format_rupiah(abs(total_neto)), tag='subtotal')
        
        insert_row("")

        # SALDO KAS AKHIR PERIODE
        saldo_kas_akhir = saldo_kas_awal + total_neto
        
        insert_row("Ditambah: Saldo Kas Awal Periode", "", _format_rupiah(saldo_kas_awal), tag='header')
        insert_row("SALDO KAS AKHIR PERIODE", "", _format_rupiah(saldo_kas_akhir), tag='total')