import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class PenjualanPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(self, text="🛒 Input Transaksi Penjualan", font=("Helvetica", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=20)

        ttk.Label(self, text="Jasa:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.combo_jasa = ttk.Combobox(self, width=27, state="readonly")
        self.combo_jasa.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(self, text="Deskripsi:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.combo_deskripsi = ttk.Combobox(self, width=27)
        self.combo_deskripsi.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        self.combo_jasa.bind("<<ComboboxSelected>>", self.update_deskripsi)

        ttk.Label(self, text="Jumlah:").grid(row=3, column=0, sticky="e", padx=10, pady=5)
        self.entry_jumlah = ttk.Entry(self, width=30)
        self.entry_jumlah.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        ttk.Button(self, text="Tambahkan ke Transaksi", command=self.tambah_transaksi).grid(row=4, column=0, columnspan=2, pady=15)

        self.tree = ttk.Treeview(
            self,
            columns=("id", "nama", "deskripsi", "jumlah", "harga", "total"),
            show="headings",
            height=8
        )
        self.tree.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        for col, text in [
            ("id", "ID"),
            ("nama", "Jasa"),
            ("deskripsi", "Deskripsi"),
            ("jumlah", "Jumlah"),
            ("harga", "Harga (Rp)"),
            ("total", "Total (Rp)")
        ]:
            self.tree.heading(col, text=text, anchor="center")
            self.tree.column(col, anchor="center", width=120)

        ttk.Button(self, text="Simpan", command=self.simpan_transaksi).grid(row=6, column=0, columnspan=2, pady=15)

        ttk.Button(self, text="Kembali ke menu utama", command=lambda: controller.show_frame("Menu Utama Staff")).grid(row=7, column=0, columnspan=2, pady=5)

        self.load_jasa()

    def update_deskripsi(self, event):
        jasa_index = self.combo_jasa.current()
        if jasa_index != -1:
            deskripsi = self.jasa_data[jasa_index][3]
            if deskripsi:
                self.combo_deskripsi["values"] = [deskripsi]
                self.combo_deskripsi.current(0)
            else:
                self.combo_deskripsi["values"] = ["(Tidak ada deskripsi)"]
                self.combo_deskripsi.current(0)

    def load_jasa(self):
        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()
        c.execute("SELECT rowid, nama_jasa, harga, detail_jasa FROM jasa")
        self.jasa_data = c.fetchall()
        conn.close()

        self.combo_jasa["values"] = [f"{j[1]} - Rp{j[2]:,.0f}" for j in self.jasa_data]

        jasa = self.combo_jasa.get()

        if jasa == self.jasa_data[1]:
            self.combo_deskripsi["values"] = [j[3] for j in self.jasa_data]

    def tambah_transaksi(self):
        jasa_index = self.combo_jasa.current()
        jumlah_str = self.entry_jumlah.get().strip()

        if jasa_index == -1:
            messagebox.showerror("Error", "Pilih jasa terlebih dahulu!")
            return
        if not jumlah_str.isdigit() or int(jumlah_str) <= 0:
            messagebox.showerror("Error", "Jumlah harus berupa angka positif!")
            return

        jumlah = int(jumlah_str)
        jasa_id, nama, harga, deskripsi = self.jasa_data[jasa_index]
        total = harga * jumlah

        self.tree.insert("", "end", values=(
            jasa_id, nama, deskripsi, jumlah, f"Rp{harga:,.0f}", f"Rp{total:,.0f}"
        ))

        self.combo_jasa.set("")
        self.combo_deskripsi.set("")
        self.entry_jumlah.delete(0, tk.END)

    def simpan_transaksi(self):
        transaksi_data = [self.tree.item(i)["values"] for i in self.tree.get_children()]
        if not transaksi_data:
            messagebox.showerror("Error", "Tidak ada transaksi untuk disimpan!")
            return

        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()

        today = datetime.date.today()
        c.execute("SELECT transaksi_penjualan_id FROM transaksi_penjualan WHERE tanggal = ?", (today,))
        existing = c.fetchall()
        antrian = len(existing) + 1
        antrian_str = str(antrian).zfill(3)

        datestr = today.strftime("%Y%m%d")
        transaksi_id = f"PJ{datestr}{antrian_str}"

        # total keseluruhan (pakai kolom total, yaitu index ke-5)
        total_semua = 0
        for row in transaksi_data:
            total_val = int(str(row[5]).replace("Rp", "").replace(",", ""))
            total_semua += total_val

        # simpan header transaksi
        c.execute(
            "INSERT INTO transaksi_penjualan (transaksi_penjualan_id, tanggal, total, kategori) VALUES (?, ?, ?, ?)",
            (transaksi_id, today, total_semua, "Pendapatan")
        )

        # simpan detail transaksi
        count = 1
        for data in transaksi_data:
            jasa_id = data[0]
            jumlah = data[3]  # jumlah kolom ke-3
            count_str = str(count).zfill(3)
            detail_id = f"DPJ{datestr}{antrian_str}{count_str}"
            c.execute(
                "INSERT INTO detail_transaksi_penjualan (detail_penjualan_id, transaksi_penjualan_id, jasa_id, jumlah) VALUES (?, ?, ?, ?)",
                (detail_id, transaksi_id, jasa_id, jumlah)
            )
            count += 1

        keterangan_ju = f"Pendapatan Jasa dari Transaksi {transaksi_id}"
            
        c.execute("""
            INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, debit)
            VALUES (?, ?, ?, ?, ?)
        """, (transaksi_id, today, '111', keterangan_ju, total_semua))
            
        c.execute("""
            INSERT INTO jurnal_umum_detail (transaksi_ref_id, tanggal, kode_akun, keterangan, kredit)
            VALUES (?, ?, ?, ?, ?)
        """, (transaksi_id, today, '401', keterangan_ju, total_semua))

        conn.commit()
        conn.close()

        messagebox.showinfo("Sukses", f"Transaksi {transaksi_id} berhasil disimpan!\nTotal: Rp{total_semua:,.0f}")

        # bersihkan tabel
        for i in self.tree.get_children():
            self.tree.delete(i)

