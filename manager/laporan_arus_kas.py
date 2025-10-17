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

        # Ambil bulan & tahun saat ini
        now = datetime.datetime.now()
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

        ttk.Label(self, text="📊 Laporan Arus Kas", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(self, text="Bulan:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.combo_bulan = ttk.Combobox(self, values=list(bulan_map.keys()), state="readonly", width=25)
        self.combo_bulan.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.combo_bulan.set(bulan_sekarang)  # ← default bulan sekarang

        ttk.Label(self, text="Tahun:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_tahun = ttk.Entry(self, width=28)
        self.entry_tahun.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.entry_tahun.insert(0, tahun_sekarang)  # ← default tahun sekarang

        ttk.Button(self, text="Tampilkan", command=self.tampil).grid(row=3, column=0, columnspan=2, pady=10)

        self.treeview = ttk.Treeview(self, columns=("keterangan", "detail", 'nominal'), show="headings", height=10)
        self.treeview.heading("keterangan", text="Keterangan")
        self.treeview.heading("detail", text="Detail")
        self.treeview.heading("nominal", text="Nominal (Rp)")
        self.treeview.column("keterangan", width=250)
        self.treeview.column("detail", width=150)
        self.treeview.column("nominal", width=150, anchor="e")
        self.treeview.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(self, text="Kembali Ke Menu Utama", command=lambda: controller.show_frame("Menu Utama Manager")).grid(row=5, column=0, columnspan=2, pady=10)

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

        today = datetime.date.today()
        datestr = today.strftime("%Y-%m-%d")

        conn = sqlite3.connect('data_keuangan.db')
        c = conn.cursor()
        c.execute("""
            SELECT id FROM rekap_modal
            WHERE strftime('%m', tanggal) = ? AND strftime('%Y', tanggal) = ?
        """, (bulan_num, tahun))
        data = c.fetchall()
        conn.close()

        if isinstance(modal_awal, tuple):
            modal_awal = modal_awal[0]
        if isinstance(modal_akhir, tuple):
            modal_akhir = modal_akhir[0]

        try:
            conn = sqlite3.connect('data_keuangan.db')
            c = conn.cursor()
            if not data:
                print("Belum ada data")
                c.execute("""
                    INSERT INTO rekap_modal (tanggal, modal_awal, modal_akhir) 
                    VALUES (?, ?, ?)
                """, (datestr, modal_awal, modal_akhir))
                conn.commit()
            elif data:
                print("Ada data")
                c.execute("""
                    UPDATE rekap_modal 
                    SET modal_akhir = ?, modal_awal = ?
                    WHERE strftime('%m', tanggal) = ? AND strftime('%Y', tanggal) = ?
                """, (modal_akhir, modal_awal, bulan_num, tahun))
                conn.commit() 
            conn.close()
            
        except(sqlite3.Error) as error:
            print("Error while connecting to sqlite", error)


# === Testing mandiri ===
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Laporan Perubahan Modal")
    app = LaporanArusKasPage(root, None)
    app.pack(fill="both", expand=True)
    root.mainloop()
