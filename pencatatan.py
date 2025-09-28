import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime, date

class PencatatanPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Styling
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 11), padding=6)
        style.configure("Title.TLabel", font=("Helvetica", 18, "bold"))

        # Judul
        ttk.Label(self, text="📒 Pencatatan Transaksi", style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=20)

        # Input Tanggal
        ttk.Label(self, text="Tanggal").grid(row=1, column=0, sticky="e", pady=8)
        self.entry_tanggal = DateEntry(self, width=20, background='darkblue',
                                       foreground='white', borderwidth=2, 
                                       date_pattern="yyyy-mm-dd")
        self.entry_tanggal.grid(row=1, column=1, pady=8, padx=10, sticky="w")

        # Input Kategori
        ttk.Label(self, text="Kategori").grid(row=2, column=0, sticky="e", pady=8)
        self.entry_kategori = ttk.Combobox(self, values=["Pemasukan", "Pengeluaran"], state="readonly")
        self.entry_kategori.grid(row=2, column=1, pady=8, padx=10, sticky="w")

        # Input Jumlah
        ttk.Label(self, text="Jumlah").grid(row=3, column=0, sticky="e", pady=8)
        def validate(P):
            return P.isdigit() or P == ""
        self.entry_jumlah = ttk.Entry(self, validate="key", width=23,
                                      validatecommand=(self.register(validate), '%P'))
        self.entry_jumlah.grid(row=3, column=1, pady=8, padx=10, sticky="w")

        # Input Keterangan
        ttk.Label(self, text="Keterangan").grid(row=4, column=0, sticky="e", pady=8)
        self.entry_keterangan = ttk.Entry(self, width=40)
        self.entry_keterangan.grid(row=4, column=1, pady=8, padx=10, sticky="w")

        # Fungsi simpan data
        def simpan_data():
            tanggal = self.entry_tanggal.get()
            kategori = self.entry_kategori.get()
            jumlah = self.entry_jumlah.get()
            keterangan = self.entry_keterangan.get()

            if not (tanggal and kategori and jumlah):
                messagebox.showerror("Error", "Semua field harus diisi!")
                return

            conn = sqlite3.connect('data_keuangan.db')
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS transaksi
                         (id TEXT PRIMARY KEY,
                          tanggal DATE,
                          kategori TEXT,
                          keterangan TEXT,
                          jumlah INTEGER)''')

            label_kategori = "M" if kategori == "Pemasukan" else "K"
            label_tanggal = tanggal.replace("-", "")

            c.execute("SELECT COUNT(*) FROM transaksi WHERE tanggal=?", (tanggal,))
            count = c.fetchone()[0]

            nomor_urut = count + 1
            id_transaksi = f"{label_kategori}{label_tanggal}{nomor_urut:03d}"

            c.execute("INSERT INTO transaksi (id, tanggal, kategori, keterangan, jumlah) VALUES (?, ?, ?, ?, ?)",
                      (id_transaksi, tanggal, kategori, keterangan, int(jumlah)))
            conn.commit()
            conn.close()

            messagebox.showinfo("Sukses", f"Data berhasil disimpan dengan ID {id_transaksi}!")

            # Reset form
            self.entry_tanggal.set_date(date.today())
            self.entry_kategori.set('')
            self.entry_jumlah.delete(0, tk.END)

        # Tombol Aksi
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="💾 Simpan", command=simpan_data).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="⬅️ Kembali ke Menu Utama",
                   command=lambda: controller.show_frame("Menu")).grid(row=0, column=1, padx=10)

        # Biar form lebih rapat di tengah
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
