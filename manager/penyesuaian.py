import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date

def format_rupiah(nominal):
    formatted = f"{int(nominal):,.0f}".replace(",", "#").replace(".", ",").replace("#", ".")
    return f"{formatted}"

def cek_nomor_akun(nama_akun):
    conn = sqlite3.connect("data_keuangan.db")
    c = conn.cursor()
    c.execute("SELECT kode_akun FROM akun WHERE nama_akun = ?", (nama_akun,))
    akun = c.fetchone()
    conn.close()
    return akun[0] if akun else None

def _connect_db():
    return sqlite3.connect('data_keuangan.db')


class PenyesuaianPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(2, weight=1) 

        ttk.Label(self, text="🧾 Jurnal Penyesuaian", font=("Helvetica", 18, "bold")).grid(
            row=0, column=0, columnspan=2, pady=15
        )

        # FORM INPUT
        frame_input = ttk.LabelFrame(self, text="Input Penyesuaian")
        frame_input.grid(row=1, column=0, padx=10, pady=10, sticky="n")

        ttk.Label(frame_input, text="Tanggal:").grid(row=0, column=0, sticky="e", padx=10, pady=5)
        self.entry_tanggal = ttk.Entry(frame_input, width=30)
        self.entry_tanggal.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        self.entry_tanggal.insert(0, date.today().strftime("%Y-%m-%d"))
        self.entry_tanggal.config(state="readonly")

        ttk.Label(frame_input, text="Jenis Penyesuaian:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.combo_akun = ttk.Combobox(
            frame_input,
            state="readonly",
            values=[
                "Beban Perlengkapan", 
                "Beban Sewa", 
                "Beban Penyusutan Peralatan",
                "Pendapatan Diterima di Muka",
                "Pendapatan Jasa Belum Diterima"
            ],
            width=27,
        )
        self.combo_akun.grid(row=1, column=1, sticky="w", padx=10, pady=5)

        ttk.Label(frame_input, text="Nominal (Rp):").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.entry_nominal = ttk.Entry(frame_input, width=30)
        self.entry_nominal.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        ttk.Button(
            frame_input, 
            text="Simpan", 
            command=self.simpan_penyesuaian,
        ).grid(row=3, column=0, columnspan=2, pady=(10, 5))

        frame_tabel = ttk.LabelFrame(self, text="Daftar Transaksi Penyesuaian")
        frame_tabel.grid(row=1, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        frame_tabel.grid_columnconfigure(0, weight=1)
        frame_tabel.grid_rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            frame_tabel, 
            columns=("Tanggal", "JenisPenyesuaian", "Nominal"),
            show="headings",
            height=20
        )
        self.tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Scrollbar
        vsb = ttk.Scrollbar(frame_tabel, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.column("Tanggal", width=100, anchor="center")
        self.tree.column("JenisPenyesuaian", width=350, anchor="w")
        self.tree.column("Nominal", width=150, anchor="e")

        self.tree.heading("Tanggal", text="Tanggal")
        self.tree.heading("JenisPenyesuaian", text="Penyesuaian")
        self.tree.heading("Nominal", text="Nominal (Rp)")

        ttk.Button(
            frame_input,
            text="Kembali ke Menu Utama",
            command=lambda: controller.show_frame("Menu Utama Manager")
            ).grid(row=4, column=0, columnspan=2, pady=(5, 10))


        self.load_penyesuaian_data()

    def load_penyesuaian_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = _connect_db()
        c = conn.cursor()

        c.execute("""
            SELECT tanggal, keterangan, debit
            FROM jurnal_umum_detail
            WHERE jenis_jurnal = 'PENYESUAIAN' AND debit > 0
            ORDER BY tanggal DESC, id DESC
            LIMIT 50 
        """)
        data = c.fetchall()
        conn.close()

        for row in data:
            tanggal, keterangan_akun, nominal = row
            jenis_penyesuaian = keterangan_akun 
            nominal_fmt = f"{format_rupiah(nominal)}"

            self.tree.insert("", "end", values=(tanggal, jenis_penyesuaian, nominal_fmt))

    def simpan_penyesuaian(self):
        tanggal = self.entry_tanggal.get()
        akun_text = self.combo_akun.get()
        nominal_str = self.entry_nominal.get().replace('.', '').replace(',', '')

        if not tanggal or not akun_text or not nominal_str:
            messagebox.showerror("Error", "Semua field harus diisi!")
            return

        try:
            nominal = int(nominal_str)
            if nominal <= 0:
                raise ValueError("Nominal harus lebih dari nol.")
        except ValueError as e:
            messagebox.showerror("Error", f"Nominal tidak valid: {e}")
            return

        conn = _connect_db()
        c = conn.cursor()

        try:
            if akun_text == "Beban Perlengkapan":
                entries = [
                    ("Beban Perlengkapan", nominal, 0),
                    ("Perlengkapan", 0, nominal)
                ]
            elif akun_text == "Beban Sewa":
                entries = [
                    ("Beban Sewa", nominal, 0),
                    ("Sewa Dibayar di Muka", 0, nominal)
                ]
            elif akun_text == "Beban Penyusutan Peralatan":
                entries = [
                    ("Beban Penyusutan Peralatan", nominal, 0),
                    ("Akumulasi Penyusutan Peralatan", 0, nominal)
                ]
            elif akun_text == "Pendapatan Diterima di Muka":
                 entries = [
                    ("Pendapatan Diterima di Muka", nominal, 0), 
                    ("Pendapatan Jasa", 0, nominal)             
                ]
            elif akun_text == "Pendapatan Jasa Belum Diterima":
                 entries = [
                    ("Piutang Usaha", nominal, 0),              
                    ("Pendapatan Jasa", 0, nominal)             
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
                    INSERT INTO jurnal_umum_detail (tanggal, kode_akun, keterangan, debit, kredit, jenis_jurnal)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (tanggal, kode_akun, nama_akun, debit, kredit, 'PENYESUAIAN'))
                

            conn.commit()
            messagebox.showinfo("Sukses", "Data penyesuaian berhasil disimpan!")

            self.entry_nominal.delete(0, tk.END)
            self.combo_akun.set("")
            
            self.load_penyesuaian_data()

        except sqlite3.Error as e:
            messagebox.showerror("Error Database", str(e))
        finally:
            conn.close()
