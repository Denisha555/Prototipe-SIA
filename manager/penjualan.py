import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def format_rupiah(nominal):
    formatted = f"{int(nominal):,.0f}".replace(",", "#").replace(".", ",").replace("#", ".")
    return f"{formatted}"

class PenjualanPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(
            self, text="🛒 Manajemen Transaksi Penjualan",
            font=("Helvetica", 18, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=20)

        # ================== FRAME KIRI ==================
        frame_kiri = ttk.LabelFrame(self, text="Input / Edit Transaksi Penjualan")
        frame_kiri.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(frame_kiri, text="Jasa:").grid(row=0, column=0, sticky="e", padx=10, pady=5)
        self.combo_jasa = ttk.Combobox(frame_kiri, width=27, state="readonly")
        self.combo_jasa.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(frame_kiri, text="Deskripsi:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.combo_deskripsi = ttk.Combobox(frame_kiri, width=27)
        self.combo_deskripsi.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(frame_kiri, text="Jumlah:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.entry_jumlah = ttk.Entry(frame_kiri, width=30)
        self.entry_jumlah.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        ttk.Button(frame_kiri, text="Tambah", command=self.tambah_transaksi).grid(
            row=3, column=0, columnspan=2, pady=10
        )

        # Treeview untuk daftar jasa yang ditambahkan
        self.tree_input = ttk.Treeview(
            frame_kiri,
            columns=("id", "nama", "deskripsi", "jumlah", "harga", "total"),
            show="headings",
            height=8
        )
        self.tree_input.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        for col, text in [
            ("id", "ID"),
            ("nama", "Jasa"),
            ("deskripsi", "Deskripsi"),
            ("jumlah", "Jumlah"),
            ("harga", "Harga (Rp)"),
            ("total", "Total (Rp)")
        ]:
            self.tree_input.heading(col, text=text, anchor="center")
            self.tree_input.column(col, anchor="center", width=120)

        ttk.Button(frame_kiri, text="Simpan Transaksi", command=self.simpan_transaksi).grid(
            row=5, column=0, columnspan=2, pady=10
        )

        ttk.Button(frame_kiri, text="Kembali ke Menu Utama",
                   command=lambda: controller.show_frame("Menu Utama Manager")
                   ).grid(row=6, column=0, columnspan=2, pady=5)

        # ================== FRAME KANAN ==================
        frame_kanan = ttk.LabelFrame(self, text="Daftar Transaksi Penjualan")
        frame_kanan.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.tree_data = ttk.Treeview(
            frame_kanan,
            columns=("id", "tanggal", "total"),
            show="headings",
            height=33
        )
        self.tree_data.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        for col, text in [
            ("id", "ID Transaksi"),
            ("tanggal", "Tanggal"),
            ("total", "Total (Rp)")
        ]:
            self.tree_data.heading(col, text=text, anchor="center")
            self.tree_data.column(col, anchor="center", width=150)

        # Tambahkan scrollbar ke tree_data
        scrollbar = ttk.Scrollbar(frame_kanan, orient="vertical", command=self.tree_data.yview)
        self.tree_data.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # ================== EVENT DAN DATA ==================
        self.combo_jasa.bind("<<ComboboxSelected>>", self.update_deskripsi)
        self.load_jasa()
        self.load_transaksi_data()

    # ---------------- Fungsi Tambahan ----------------
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

        self.combo_jasa["values"] = [f"{j[1]} - {format_rupiah(j[2])}" for j in self.jasa_data]

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

        self.tree_input.insert("", "end", values=(
            jasa_id, nama, deskripsi, jumlah, f"{format_rupiah(harga)}", f"{format_rupiah(total)}"
        ))

        self.combo_jasa.set("")
        self.combo_deskripsi.set("")
        self.entry_jumlah.delete(0, tk.END)

    def simpan_transaksi(self):
        transaksi_data = [self.tree_input.item(i)["values"] for i in self.tree_input.get_children()]
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

        # Hitung total keseluruhan
        total_semua = 0
        for row in transaksi_data:
            total_val = int(str(row[5]).replace(".", ""))
            total_semua += total_val

        # Simpan header transaksi
        c.execute(
            "INSERT INTO transaksi_penjualan (transaksi_penjualan_id, tanggal, total, kategori) VALUES (?, ?, ?, ?)",
            (transaksi_id, today, total_semua, "Pendapatan")
        )

        # Simpan detail transaksi
        count = 1
        for data in transaksi_data:
            jasa_id = data[0]
            jumlah = data[3]
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

        messagebox.showinfo("Sukses", f"Transaksi {transaksi_id} berhasil disimpan!\nTotal: Rp{format_rupiah(total_semua)}")

        # Bersihkan tabel input
        for i in self.tree_input.get_children():
            self.tree_input.delete(i)

        self.load_transaksi_data()

    def load_transaksi_data(self):
        # Bersihkan data lama
        for i in self.tree_data.get_children():
            self.tree_data.delete(i)

        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()
        c.execute("SELECT transaksi_penjualan_id, tanggal, total FROM transaksi_penjualan ORDER BY tanggal DESC")
        data = c.fetchall()
        conn.close()

        for row in data:
            transaksi_id, tanggal, total = row
            formatted_total = format_rupiah(total)
            self.tree_data.insert("", "end", values=(transaksi_id, tanggal, formatted_total))