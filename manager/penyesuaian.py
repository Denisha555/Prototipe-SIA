import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date

class PenyesuaianPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="🧾 Penyesuaian", font=("Helvetica", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=15)

        # === Form Input ===
        row_data = 1
        ttk.Label(self, text="Tanggal:").grid(row=row_data, column=0, sticky="e", padx=10, pady=5)
        self.entry_tanggal = ttk.Entry(self, width=30, state="readonly")
        self.entry_tanggal.grid(row=row_data, column=1, sticky="w", padx=10, pady=5)
        self.entry_tanggal.insert(0, date.today().strftime("%Y-%m-%d"))

        row_data =+1
        ttk.Label(self, text="Akun Debit:").grid(row=row_data, column=0, sticky="e", padx=10, pady=5)
        self.combo_debit = ttk.Combobox(self, width=27, state="readonly")
        self.combo_debit.grid(row=row_data, column=1, sticky="w", padx=10, pady=5)

        row_data =+1
        ttk.Label(self, text="Akun Kredit:").grid(row=row_data, column=0, sticky="e", padx=10, pady=5)
        self.combo_kredit = ttk.Combobox(self, width=27, state="readonly")
        self.combo_kredit.grid(row=row_data, column=1, sticky="w", padx=10, pady=5)

        row_data =+1
        ttk.Label(self, text="Nominal (Rp):").grid(row=row_data, column=0, sticky="e", padx=10, pady=5)
        self.entry_nominal = ttk.Entry(self, width=30)
        self.entry_nominal.grid(row=row_data, column=1, sticky="w", padx=10, pady=5)

        ttk.Button(self, text="Tambah ke Daftar", command=self.tambah_ke_tabel).grid(row=6, column=0, columnspan=2, pady=10)

        # === Tabel Data ===
        self.tree = ttk.Treeview(self, columns=("tanggal", "keterangan", "debit", "kredit", "nominal"), show="headings", height=8)
        self.tree.grid(row=7, column=0, columnspan=2, padx=15, pady=10, sticky="nsew")

        self.tree.heading("tanggal", text="Tanggal")
        self.tree.heading("keterangan", text="Keterangan")
        self.tree.heading("debit", text="Akun Debit")
        self.tree.heading("kredit", text="Akun Kredit")
        self.tree.heading("nominal", text="Nominal (Rp)")

        self.tree.column("tanggal", width=100, anchor="center")
        self.tree.column("keterangan", width=150)
        self.tree.column("debit", width=120)
        self.tree.column("kredit", width=120)
        self.tree.column("nominal", width=100, anchor="e")

        # === Tombol Simpan & Navigasi ===
        ttk.Button(self, text="💾 Simpan ke Database", command=self.simpan_ke_db).grid(row=8, column=0, columnspan=2, pady=10)
        ttk.Button(self, text="◀️ Kembali ke Menu", command=lambda: controller.show_frame("Menu Utama Manager")).grid(row=9, column=0, columnspan=2, pady=5)

        # Load daftar akun dari database
        self.load_akun()

    def load_akun(self):
        """Ambil daftar akun dari tabel akun"""
        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()
        c.execute("SELECT kode_akun, nama_akun FROM akun")
        akun_list = [f"{row[0]} - {row[1]}" for row in c.fetchall()]
        conn.close()

        self.combo_debit["values"] = akun_list
        self.combo_kredit["values"] = akun_list

    def tambah_ke_tabel(self):
        tanggal = self.entry_tanggal.get().strip()
        keterangan = self.entry_keterangan.get().strip()
        debit = self.combo_debit.get().strip()
        kredit = self.combo_kredit.get().strip()
        nominal = self.entry_nominal.get().strip()

        if not all([tanggal, keterangan, debit, kredit, nominal]):
            messagebox.showerror("Error", "Semua kolom wajib diisi!")
            return

        try:
            float(nominal)
        except ValueError:
            messagebox.showerror("Error", "Nominal harus berupa angka!")
            return

        self.tree.insert("", "end", values=(tanggal, keterangan, debit, kredit, nominal))

        # Kosongkan input setelah tambah
        self.entry_keterangan.delete(0, tk.END)
        self.entry_nominal.delete(0, tk.END)

    def simpan_ke_db(self):
        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()

        rows = self.tree.get_children()
        if not rows:
            messagebox.showwarning("Peringatan", "Tidak ada data untuk disimpan.")
            return

        for row in rows:
            tanggal, keterangan, debit, kredit, nominal = self.tree.item(row)["values"]
            nominal = float(nominal)

            # Ambil kode akun dari combo (misal "111 - Kas" → ambil "111")
            debit_kode = debit.split(" - ")[0]
            kredit_kode = kredit.split(" - ")[0]

            # Simpan dua baris: satu debit, satu kredit
            c.execute("""
                INSERT INTO jurnal_umum_detail (tanggal, kode_akun, keterangan, debit, kredit)
                VALUES (?, ?, ?, ?, ?)
            """, (tanggal, debit_kode, keterangan, nominal, 0))
            c.execute("""
                INSERT INTO jurnal_umum_detail (tanggal, kode_akun, keterangan, debit, kredit)
                VALUES (?, ?, ?, ?, ?)
            """, (tanggal, kredit_kode, keterangan, 0, nominal))

        conn.commit()
        conn.close()

        messagebox.showinfo("Sukses", "penyesuaian berhasil disimpan.")
        for row in rows:
            self.tree.delete(row)

if __name__ == "__main__":
    root = tk.Tk()
    class dummy:
        def show_frame(self, frame_name):
            pass
    app = PenyesuaianPage(root, dummy())
    app.pack()
    app.mainloop()