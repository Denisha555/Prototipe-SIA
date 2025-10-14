import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from function.bulan_map import bulan_map


# === Fungsi bantu ambil saldo akun untuk perhitungan laba rugi ===
def _get_account_balances(bulan_num, tahun):
    conn = sqlite3.connect('data_keuangan.db')
    c = conn.cursor()

    c.execute("""
        SELECT kode_akun, nama_akun, kategori, saldo_normal 
        FROM akun 
        WHERE kategori IN ('Pendapatan', 'Beban') 
        ORDER BY kode_akun ASC
    """)
    accounts = c.fetchall()
    conn.close()

    report_data = []
    conn = sqlite3.connect('data_keuangan.db')
    c = conn.cursor()

    for kode_akun, nama_akun, kategori, saldo_normal in accounts:
        # Mutasi Jurnal Umum (tanpa penyesuaian/penutupan)
        query_ns = """
            SELECT SUM(debit), SUM(kredit)
            FROM jurnal_umum_detail
            WHERE kode_akun = ?
              AND strftime('%m', tanggal) = ?
              AND strftime('%Y', tanggal) = ?
              AND (jenis_jurnal IS NULL OR jenis_jurnal NOT IN ('PENYESUAIAN', 'PENUTUP'))
        """
        c.execute(query_ns, (kode_akun, bulan_num, tahun))
        ns_d, ns_k = c.fetchone() or (0, 0)
        ns_d = ns_d or 0
        ns_k = ns_k or 0

        # Mutasi Jurnal Penyesuaian
        query_ajp = """
            SELECT SUM(debit), SUM(kredit)
            FROM transaksi_penyesuaian
            WHERE kode_akun = ?
              AND strftime('%m', tanggal) = ?
              AND strftime('%Y', tanggal) = ?
        """
        c.execute(query_ajp, (kode_akun, bulan_num, tahun))
        ajp_d, ajp_k = c.fetchone() or (0, 0)
        ajp_d = ajp_d or 0
        ajp_k = ajp_k or 0

        # Hitung saldo akhir akun
        saldo = (ns_d - ns_k) + (ajp_d - ajp_k)

        report_data.append({
            "kode": kode_akun,
            "nama": nama_akun,
            "kategori": kategori,
            "debit": max(0, saldo),
            "kredit": abs(min(0, saldo))
        })

    conn.close()
    return report_data


# === Kelas GUI ===
class LaporanPerubahanModalPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Ambil bulan & tahun saat ini
        now = datetime.now()
        bulan_sekarang = now.strftime("%B")  # nama bulan (English)
        tahun_sekarang = str(now.year)

        # Mapping ke bulan_map jika perlu ubah ke format Indonesia
        if bulan_sekarang not in bulan_map:
            # Pastikan nama bulan sesuai key di bulan_map (misalnya "Oktober", bukan "October")
            # Kalau bulan_map pakai bahasa Indonesia:
            eng_to_id = {
                "January": "Januari", "February": "Februari", "March": "Maret",
                "April": "April", "May": "Mei", "June": "Juni", "July": "Juli",
                "August": "Agustus", "September": "September", "October": "Oktober",
                "November": "November", "December": "Desember"
            }
            bulan_sekarang = eng_to_id.get(bulan_sekarang, bulan_sekarang)

        ttk.Label(self, text="📊 Laporan Perubahan Modal", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self, text="Bulan:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.combo_bulan = ttk.Combobox(self, values=list(bulan_map.keys()), state="readonly", width=25)
        self.combo_bulan.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.combo_bulan.set(bulan_sekarang)  # ← default bulan sekarang

        ttk.Label(self, text="Tahun:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_tahun = ttk.Entry(self, width=28)
        self.entry_tahun.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.entry_tahun.insert(0, tahun_sekarang)  # ← default tahun sekarang

        ttk.Button(self, text="Tampilkan", command=self.tampil).grid(row=3, column=0, columnspan=2, pady=10)

        self.treeview = ttk.Treeview(self, columns=("keterangan", "nominal"), show="headings", height=10)
        self.treeview.heading("keterangan", text="Keterangan")
        self.treeview.heading("nominal", text="Nominal (Rp)")
        self.treeview.column("keterangan", width=250)
        self.treeview.column("nominal", width=150, anchor="e")
        self.treeview.grid(row=4, column=0, columnspan=2, pady=10)

    # === Fungsi utama tampilkan laporan ===
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

        laba_bersih = self.hitung_laba_rugi(bulan_num, tahun)

        # Bersihkan tabel
        self.treeview.delete(*self.treeview.get_children())

        # === Ambil modal awal (akun 311 misalnya) ===
        conn = sqlite3.connect('data_keuangan.db')
        c = conn.cursor()
        c.execute("""
            SELECT kredit
            FROM jurnal_umum_detail
            WHERE kode_akun = '311'
              AND strftime('%m', tanggal) = ?
              AND strftime('%Y', tanggal) = ?
        """, (bulan_num, tahun))
        row = c.fetchone()
        modal_awal = row[0] if row and row[0] is not None else 0
        conn.close()

        # === Tampilkan hasil laporan ===
        self.treeview.insert("", "end", values=("Modal Awal", f"{modal_awal:,.0f}"))
        self.treeview.insert("", "end", values=("Laba Bersih", f"{laba_bersih:,.0f}"))

        modal_akhir = modal_awal + laba_bersih
        self.treeview.insert("", "end", values=("Modal Akhir", f"{modal_akhir:,.0f}"), tags=("akhir",))

        # Atur style background tag-nya
        self.treeview.tag_configure("akhir", font=('Helvetica', 11, 'bold'), background='#E0F7FA')

    # === Fungsi hitung laba rugi ===
    def hitung_laba_rugi(self, bulan_num, tahun):
        data = _get_account_balances(bulan_num, tahun)
        total_pendapatan = sum(item["kredit"] - item["debit"] for item in data if item["kategori"] == "Pendapatan")
        total_beban = sum(item["debit"] - item["kredit"] for item in data if item["kategori"] == "Beban")
        return total_pendapatan - total_beban


# === Testing mandiri ===
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Laporan Perubahan Modal")
    app = LaporanPerubahanModalPage(root, None)
    app.pack(fill="both", expand=True)
    root.mainloop()
