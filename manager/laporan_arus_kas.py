import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
from function.bulan_map import bulan_map


class LaporanArusKasPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        now = datetime.datetime.now()
        bulan_sekarang = now.strftime("%B")
        tahun_sekarang = str(now.year)

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

        self.treeview = ttk.Treeview(self, columns=("keterangan", "detail", 'nominal'), show="headings", height=12)
        self.treeview.heading("keterangan", text="Keterangan")
        self.treeview.heading("detail", text="Detail")
        self.treeview.heading("nominal", text="Nominal (Rp)")
        self.treeview.column("keterangan", width=200)
        self.treeview.column("detail", width=200)
        self.treeview.column("nominal", width=150, anchor="e")
        self.treeview.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(self, text="Kembali Ke Menu Utama", command=lambda: controller.show_frame("Menu Utama Manager")).grid(row=5, column=0, columnspan=2, pady=10)

    # === fungsi bantu untuk hitung laba rugi (contoh sederhana) ===
    def hitung_laba_rugi(self, bulan, tahun):
        conn = sqlite3.connect('data_keuangan.db')
        c = conn.cursor()
        c.execute("""
            SELECT SUM(kredit - debit)
            FROM jurnal_umum_detail
            WHERE (kode_akun LIKE '4%' OR kode_akun LIKE '5%')
              AND jenis_jurnal = 'UMUM'
              AND strftime('%m', tanggal) = ?
              AND strftime('%Y', tanggal) = ?
        """, (bulan, tahun))
        hasil = c.fetchone()[0]
        conn.close()
        return hasil if hasil else 0

    # === tampil laporan arus kas ===
    def tampil(self):
        bulan_nama = self.combo_bulan.get()
        tahun = self.entry_tahun.get().strip()

        if not bulan_nama or not tahun:
            messagebox.showerror("Error", "Bulan dan Tahun harus diisi!")
            return

        try:
            bulan_num = bulan_map[bulan_nama]
        except KeyError:
            messagebox.showerror("Error", "Nama bulan tidak valid.")
            return

        try:
            int(tahun)
        except ValueError:
            messagebox.showerror("Error", "Tahun harus berupa angka.")
            return

        # bersihkan tabel
        self.treeview.delete(*self.treeview.get_children())

        # === Aktivitas Operasi ===
        conn = sqlite3.connect('data_keuangan.db')
        c = conn.cursor()
        c.execute("""
            SELECT keterangan, SUM(kredit - debit), kode_akun
            FROM jurnal_umum_detail
            WHERE (kode_akun LIKE '1%' OR kode_akun LIKE '4%')
              AND jenis_jurnal = 'UMUM'
              AND strftime('%m', tanggal) = ?
              AND strftime('%Y', tanggal) = ?
            GROUP BY keterangan
        """, (bulan_num, tahun))
        operasi = c.fetchall()
        conn.close()

        total_operasi = 0

        self.treeview.insert("", "end", values=("Aktivitas Operasi", "", ""))
        for ket, nominal, kode_akun in operasi:
            if kode_akun == '111' or kode_akun == '121' or kode_akun == '122':
                continue
            self.treeview.insert("", "end", values=("", ket, f"{nominal:,.0f}"))
            total_operasi += nominal

        self.treeview.insert("", "end", values=("", "Total Arus Kas Operasi", f"{total_operasi:,.0f}"), tags="total")

        # === Aktivitas Investasi ===
        conn = sqlite3.connect('data_keuangan.db')
        c = conn.cursor()
        c.execute("""
            SELECT keterangan, SUM(kredit - debit)
            FROM jurnal_umum_detail
            WHERE kode_akun = '121'
              AND jenis_jurnal = 'UMUM'
              AND strftime('%m', tanggal) = ?
              AND strftime('%Y', tanggal) = ?
            GROUP BY keterangan
        """, (bulan_num, tahun))
        investasi = c.fetchall()
        conn.close()

        total_investasi = sum([x[1] for x in investasi]) if investasi else 0
        self.treeview.insert("", "end", values=("Aktivitas Investasi", "", ""))
        for ket, nominal in investasi:
            self.treeview.insert("", "end", values=("", ket, f"{nominal:,.0f}"))
        self.treeview.insert("", "end", values=("", "Total Arus Kas Investasi", f"{total_investasi:,.0f}"), tags="total")

        # === Aktivitas Pendanaan ===
        conn = sqlite3.connect('data_keuangan.db')
        c = conn.cursor()
        c.execute("""
            SELECT keterangan, SUM(kredit - debit)
            FROM jurnal_umum_detail
            WHERE kode_akun = '311'
              AND jenis_jurnal = 'UMUM'
              AND strftime('%m', tanggal) = ?
              AND strftime('%Y', tanggal) = ?
            GROUP BY keterangan
        """, (bulan_num, tahun))
        pendanaan = c.fetchall()
        conn.close()

        total_pendanaan = sum([x[1] for x in pendanaan]) if pendanaan else 0
        self.treeview.insert("", "end", values=("Aktivitas Pendanaan", "", ""))
        for ket, nominal in pendanaan:
            self.treeview.insert("", "end", values=("", ket, f"{nominal:,.0f}"))
        self.treeview.insert("", "end", values=("", "Total Arus Kas Pendanaan", f"{total_pendanaan:,.0f}"), tags="total")

        # === Total Kenaikan Kas ===
        total_kas = total_operasi + total_investasi + total_pendanaan
        self.treeview.insert("", "end", values=("", "Total Arus Kas", f"{total_kas:,.0f}"), tags="total")

        self.treeview.tag_configure("total", font=('Helvetica', 10, 'bold'), background='#E0F7FA')
