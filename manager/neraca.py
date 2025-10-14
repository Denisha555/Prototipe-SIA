import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
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

        # Daftar bulan
        bulan_list = list(bulan_map.keys())

        # Ambil bulan dan tahun saat ini
        now = datetime.now()
        bulan_sekarang = list(bulan_map.keys())[int(now.strftime("%m")) - 1]
        tahun_sekarang = now.strftime("%Y")

        # === Input kategori, bulan, tahun ===
        ttk.Label(self, text="Kategori:").grid(row=1, column=0, sticky="e", pady=5, padx=20)
        self.combo_kategori = ttk.Combobox(self, width=25, state="readonly", values=["Aktiva", "Pasiva"])
        self.combo_kategori.grid(row=1, column=1, sticky="w", pady=5)
        self.combo_kategori.set("Aktiva")

        ttk.Label(self, text="Bulan:").grid(row=2, column=0, sticky="e", pady=5, padx=20)
        self.combo_bulan = ttk.Combobox(self, width=25, state="readonly", values=bulan_list)
        self.combo_bulan.grid(row=2, column=1, sticky="w", pady=5)
        self.combo_bulan.set(bulan_sekarang)  # default bulan ini

        ttk.Label(self, text="Tahun:").grid(row=3, column=0, sticky="e", pady=5, padx=20)
        self.entry_tahun = ttk.Entry(self, width=28)
        self.entry_tahun.grid(row=3, column=1, sticky="w", pady=5)
        self.entry_tahun.insert(0, tahun_sekarang)  # default tahun ini

        ttk.Button(self, text="Tampilkan", command=self.load_neraca).grid(
            row=4, column=0, columnspan=2, pady=10
        )

        # === Frame isi tabel ===
        self.frame_isi = ttk.Frame(self)
        self.frame_isi.grid(row=5, column=0, columnspan=2, pady=10)

        self.tree = ttk.Treeview(
            self.frame_isi, columns=("akun", "saldo"), show="headings", height=12
        )
        self.tree.heading("akun", text="Akun")
        self.tree.heading("saldo", text="Saldo (Rp)")
        self.tree.column("akun", width=200)
        self.tree.column("saldo", width=120, anchor="e")
        self.tree.grid(row=0, column=0, padx=20)

        ttk.Button(
            self,
            text="Kembali Ke Menu Utama",
            command=lambda: controller.show_frame("Menu Utama Manager"),
        ).grid(row=6, column=0, columnspan=2, pady=10)

    def load_neraca(self):
        kategori = self.combo_kategori.get().strip()
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

        aktiva, pasiva = [], []

        # Ambil modal akhir
        c.execute("""
            SELECT modal_akhir FROM rekap_modal
            WHERE strftime('%m', tanggal) = ?
            AND strftime('%Y', tanggal) = ?
        """, (bulan_num, tahun))
        hasil_modal = c.fetchone()
        modal_akhir = hasil_modal[0] if hasil_modal else None

        if modal_akhir:
            pasiva.append(("Modal Akhir", modal_akhir))
        else:
            messagebox.showerror(
                "Error",
                "Silahkan ke halaman Laporan Perubahan Modal untuk menghitung perubahan modal terlebih dahulu."
            )
            conn.close()
            return

        # Hitung saldo tiap akun
        for kode_akun, nama_akun in akun_list:
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

            if kode_akun.startswith("1"):  # Aktiva
                aktiva.append((nama_akun, saldo))
            elif kode_akun.startswith(("2", "3")):  # Pasiva (Kewajiban / Modal)
                pasiva.append((nama_akun, abs(saldo)))

        # Pindahkan peralatan & akumulasi penyusutan ke aktiva
        for p in pasiva[:]:
            if p[0] in ("Peralatan", "Akumulasi Penyusutan Peralatan"):
                aktiva.append(p)
                pasiva.remove(p)
            elif p[0] == "Modal Pemilik":
                pasiva.remove(p)

        conn.close()

        # Hapus isi tabel sebelumnya
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Isi ulang tabel sesuai kategori
        if kategori == "Aktiva":
            for nama_akun, saldo in aktiva:
                self.tree.insert("", "end", values=(nama_akun, f"{saldo:,.0f}"))
        else:  # Pasiva
            for nama_akun, saldo in pasiva:
                self.tree.insert("", "end", values=(nama_akun, f"{saldo:,.0f}"))

        # Tambahkan total
        total_aktiva = sum(s for _, s in aktiva)
        total_pasiva = sum(s for _, s in pasiva)

        if kategori == "Aktiva":
            self.tree.insert("", "end", values=("TOTAL AKTIVA", f"{total_aktiva:,.0f}"))
        else:
            self.tree.insert("", "end", values=("TOTAL PASIVA", f"{total_pasiva:,.0f}"))

        # Cek keseimbangan
        if total_aktiva != total_pasiva:
            messagebox.showwarning(
                "⚠️ Tidak Seimbang",
                f"Total Aktiva ({total_aktiva:,.0f}) ≠ Total Pasiva ({total_pasiva:,.0f})"
            )
