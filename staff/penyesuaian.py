import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date

def cek_nomor_akun(nama_akun):
    conn = sqlite3.connect("data_keuangan.db")
    c = conn.cursor()
    c.execute("SELECT kode_akun FROM akun WHERE nama_akun = ?", (nama_akun,))
    akun = c.fetchone()
    conn.close()
    return akun[0] if akun else None


class PenyesuaianPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(self, text="📝 Penyesuaian", font=("Helvetica", 18, "bold")).grid(
            row=0, column=0, columnspan=2, pady=15
        )

        # === Form Input ===
        ttk.Label(self, text="Tanggal:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.entry_tanggal = ttk.Entry(self, width=30)
        self.entry_tanggal.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        self.entry_tanggal.insert(0, date.today().strftime("%Y-%m-%d"))
        self.entry_tanggal.config(state="readonly")

        ttk.Label(self, text="Akun:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.combo_akun = ttk.Combobox(self, width=27, state="readonly")
        self.combo_akun.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        ttk.Label(self, text="Nominal (Rp):").grid(row=3, column=0, sticky="e", padx=10, pady=5)
        self.entry_nominal = ttk.Entry(self, width=30)
        self.entry_nominal.grid(row=3, column=1, sticky="w", padx=10, pady=5)

        ttk.Button(self, text="Simpan", command=self.simpan_ke_db).grid(
            row=4, column=0, columnspan=2, pady=10
        )

        ttk.Button(
            self,
            text="Kembali ke Menu Utama",
            command=lambda: controller.show_frame("Menu Utama Staff")
        ).grid(row=5, column=0, columnspan=2, pady=5)

        self.load_akun()

    def load_akun(self):
        """Ambil daftar akun tertentu dari tabel akun"""
        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()
        c.execute("SELECT kode_akun, nama_akun FROM akun WHERE kode_akun IN ('113', '121')")
        akun_list = [f"{row[0]} - {row[1]}" for row in c.fetchall()]
        conn.close()
        self.combo_akun["values"] = akun_list

    def simpan_ke_db(self):
        tanggal = self.entry_tanggal.get().strip()
        akun = self.combo_akun.get().strip()
        nominal_str = self.entry_nominal.get().strip()

        if not akun or not nominal_str:
            messagebox.showerror("Error", "Semua field harus diisi!")
            return

        try:
            nominal = float(nominal_str)
        except ValueError:
            messagebox.showerror("Error", "Nominal harus berupa angka!")
            return

        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()

        try:
            if akun.startswith("113"):
                # Penyesuaian Perlengkapan
                entries = [
                    ("Beban Perlengkapan", nominal, 0),
                    ("Perlengkapan", 0, nominal)
                ]
            elif akun.startswith("121"):
                # Penyesuaian Penyusutan Peralatan
                entries = [
                    ("Beban Penyusutan Peralatan", nominal, 0),
                    ("Akumulasi Penyusutan Peralatan", 0, nominal)
                ]
            else:
                messagebox.showerror("Error", "Akun tidak dikenali untuk penyesuaian!")
                conn.close()
                return

            for nama_akun, debit, kredit in entries:
                kode_akun = cek_nomor_akun(nama_akun)
                if not kode_akun:
                    messagebox.showerror("Error", f"Akun '{nama_akun}' tidak ditemukan di database.")
                    conn.close()
                    return

                c.execute("""
                    INSERT INTO transaksi_penyesuaian (tanggal, kode_akun, debit, kredit)
                    VALUES (?, ?, ?, ?)
                """, (tanggal, kode_akun, debit, kredit))

                c.execute("""
                    INSERT INTO jurnal_umum_detail (tanggal, keterangan, kode_akun, debit, kredit, jenis_jurnal)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (tanggal, kode_akun, nama_akun, debit, kredit, 'PENYESUAIAN'))

            conn.commit()
            messagebox.showinfo("Sukses", "Data penyesuaian berhasil disimpan!")

            self.entry_nominal.delete(0, tk.END)
            self.combo_akun.set("")

        except sqlite3.Error as e:
            messagebox.showerror("Error Database", str(e))
        finally:
            conn.close()
