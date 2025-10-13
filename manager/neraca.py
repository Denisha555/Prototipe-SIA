import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from function.bulan_map import bulan_map

def _connect_db():
    return sqlite3.connect("data_keuangan.db")

class NeracaPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        ttk.Label(self, text="💼 Neraca", font=("Helvetica", 18, "bold")).grid(
            row=0, column=0, columnspan=2, pady=15
        )

        bulan_list = list(bulan_map.keys())

        ttk.Label(self, text="Bulan:").grid(row=1, column=0, sticky="e", pady=5)
        self.combo_bulan = ttk.Combobox(self, width=25, state="readonly", values=bulan_list)
        self.combo_bulan.grid(row=1, column=1, sticky="w", pady=5)

        ttk.Label(self, text="Tahun:").grid(row=2, column=0, sticky="e", pady=5)
        self.entry_tahun = ttk.Entry(self, width=28)
        self.entry_tahun.grid(row=2, column=1, sticky="w", pady=5)

        ttk.Button(self, text="Tampilkan Neraca", command=self.load_neraca).grid(
            row=3, column=0, columnspan=2, pady=10
        )

        # Frame isi tabel Aktiva & Pasiva
        self.frame_isi = ttk.Frame(self)
        self.frame_isi.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=10)

        self.tree_aktiva = ttk.Treeview(self.frame_isi, columns=("akun", "saldo"), show="headings", height=12)
        self.tree_aktiva.heading("akun", text="Aktiva")
        self.tree_aktiva.heading("saldo", text="Saldo (Rp)")
        self.tree_aktiva.column("akun", width=200)
        self.tree_aktiva.column("saldo", width=120, anchor="e")
        self.tree_aktiva.grid(row=0, column=0, padx=20)

        self.tree_pasiva = ttk.Treeview(self.frame_isi, columns=("akun", "saldo"), show="headings", height=12)
        self.tree_pasiva.heading("akun", text="Pasiva")
        self.tree_pasiva.heading("saldo", text="Saldo (Rp)")
        self.tree_pasiva.column("akun", width=250)
        self.tree_pasiva.column("saldo", width=120, anchor="e")
        self.tree_pasiva.grid(row=0, column=1, padx=20)

    def load_neraca(self):
        bulan = self.combo_bulan.get().strip()
        tahun = self.entry_tahun.get().strip()
        if not bulan or not tahun:
            messagebox.showerror("Error", "Silakan pilih bulan dan isi tahun terlebih dahulu.")
            return

        bulan_num = bulan_map[bulan]
        conn = _connect_db()
        c = conn.cursor()

        # Ambil daftar akun
        c.execute("SELECT kode_akun, nama_akun FROM akun ORDER BY kode_akun ASC")
        akun_list = c.fetchall()

        aktiva = []
        pasiva = []

        for kode_akun, nama_akun in akun_list:
            # Hitung total debit dan kredit bulan itu
            c.execute("""
                SELECT 
                    IFNULL(SUM(debit), 0) as total_debit,
                    IFNULL(SUM(kredit), 0) as total_kredit
                FROM jurnal_umum_detail
                WHERE kode_akun = ?
                AND strftime('%m', tanggal) = ?
                AND strftime('%Y', tanggal) = ?
            """, (kode_akun, bulan_num, tahun))
            hasil = c.fetchone()
            total_debit, total_kredit = hasil if hasil else (0, 0)
            saldo = total_debit - total_kredit

            # Masukkan ke sisi sesuai jenis akun
            if kode_akun.startswith("1"):  # Aktiva
                aktiva.append((nama_akun, saldo))
            elif kode_akun.startswith("2") or kode_akun.startswith("3"):  # Pasiva (Kewajiban / Modal)
                pasiva.append((nama_akun, abs(saldo)))

        conn.close()

        # Hapus isi sebelumnya
        for item in self.tree_aktiva.get_children():
            self.tree_aktiva.delete(item)
        for item in self.tree_pasiva.get_children():
            self.tree_pasiva.delete(item)

        # Isi ulang tabel
        for nama_akun, saldo in aktiva:
            self.tree_aktiva.insert("", "end", values=(nama_akun, f"{saldo:,.0f}"))
        for nama_akun, saldo in pasiva:
            self.tree_pasiva.insert("", "end", values=(nama_akun, f"{saldo:,.0f}"))

        # Tambahkan total di bawah
        total_aktiva = sum(s for _, s in aktiva)
        total_pasiva = sum(s for _, s in pasiva)
        self.tree_aktiva.insert("", "end", values=("TOTAL AKTIVA", f"{total_aktiva:,.0f}"))
        self.tree_pasiva.insert("", "end", values=("TOTAL PASIVA", f"{total_pasiva:,.0f}"))

        if total_aktiva != total_pasiva:
            messagebox.showwarning("⚠️ Tidak Seimbang", 
                f"Total Aktiva ({total_aktiva:,.0f}) ≠ Total Pasiva ({total_pasiva:,.0f})")



if __name__ == "__main__":
    root = tk.Tk()
    class Dummy:
        def show_frame(self, f): pass
    app = NeracaPage(root, Dummy())
    app.pack(fill="both", expand=True)
    root.mainloop()
