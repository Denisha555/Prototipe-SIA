import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


class BukuBesarPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # --- Konfigurasi tata letak utama ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # === Judul Halaman ===
        ttk.Label(
            self,
            text="📘 Buku Besar",
            font=("Helvetica", 18, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(15, 10))

        # === Form Pilihan Bulan & Tahun ===
        form_frame = ttk.Frame(self)
        form_frame.grid(row=1, column=0, columnspan=2, pady=10)

        bulan_list = [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]

        ttk.Label(form_frame, text="Bulan:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.combo_bulan = ttk.Combobox(form_frame, width=27, state="readonly", values=bulan_list)
        self.combo_bulan.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(form_frame, text="Tahun:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.entry_tahun = ttk.Entry(form_frame, width=30)
        self.entry_tahun.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Button(
            form_frame,
            text="Tampilkan",
            command=self.load_laporan
        ).grid(row=2, column=0, columnspan=2, pady=(10, 0))

        # === Tombol Kembali ===
        ttk.Button(
            self,
            text="Kembali ke Menu Utama",
            command=lambda: controller.show_frame("Menu Utama Manager")
        ).grid(row=2, column=0, columnspan=2, pady=10)

        # === Area Scroll untuk Tabel ===
        container = ttk.Frame(self)
        container.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_inner = ttk.Frame(self.scrollable_frame)
        self.scrollable_inner.grid(row=0, column=0, columnspan=2, sticky="n")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=10)
        scrollbar.grid(row=5, column=1, sticky="ns", padx=(0, 15), columnspan=2)

    def load_laporan(self):
        bulan = self.combo_bulan.get().strip()
        tahun = self.entry_tahun.get().strip()

        nama_ke_angka = {
            "Januari": "01", "Februari": "02", "Maret": "03", "April": "04",
            "Mei": "05", "Juni": "06", "Juli": "07", "Agustus": "08",
            "September": "09", "Oktober": "10", "November": "11", "Desember": "12"
        }
        bulan_angka = nama_ke_angka.get(bulan)

        if not bulan_angka or not tahun:
            messagebox.showerror("Error", "Silakan pilih bulan dan isi tahun terlebih dahulu!")
            return

        # Bersihkan tabel lama
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # === Ambil data dari database ===
        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()

        # Penjualan (Kas Masuk)
        c.execute("""
            SELECT tanggal, kategori, total
            FROM transaksi_penjualan
            WHERE strftime('%m', tanggal)=? AND strftime('%Y', tanggal)=?
        """, (bulan_angka, tahun))
        kas_masuk = c.fetchall()

        # Pembelian (Kas Keluar)
        c.execute("""
            SELECT tanggal, kategori, total
            FROM transaksi_pembelian
            WHERE strftime('%m', tanggal)=? AND strftime('%Y', tanggal)=?
        """, (bulan_angka, tahun))
        kas_keluar = c.fetchall()

        conn.close()

        # === Siapkan struktur akun ===
        akun_dict = {
            "Kas": [],
            "Pendapatan": [],
            "Peralatan": [],
            "Perlengkapan": [],
            "Biaya": [],
            "Beban": []
        }

        # --- Penjualan ---
        for tanggal, kategori, total in kas_masuk:
            akun_dict["Kas"].append((tanggal, "Pendapatan", total, 0))
            akun_dict["Pendapatan"].append((tanggal, "Kas", 0, total))

        # --- Pembelian ---
        for tanggal, kategori, total in kas_keluar:
            if kategori in akun_dict:
                akun_dict[kategori].append((tanggal, "Kas", total, 0))
            else:
                akun_dict["Beban"].append((tanggal, "Kas", total, 0))
            akun_dict["Kas"].append((tanggal, kategori, 0, total))

        # === Tampilkan data ke layar ===
        ada_data = False
        row = 0

        for akun, transaksi in akun_dict.items():
            if not transaksi:
                continue

            ada_data = True

            # Frame untuk tiap akun
            akun_frame = ttk.Frame(self.scrollable_frame)
            akun_frame.grid(row=row, column=1, padx=15, pady=15, sticky="n")

            ttk.Label(
                akun_frame,
                text=f"Akun: {akun}",
                font=("Helvetica", 14, "bold")
            ).pack(anchor="center", pady=(5, 5))

            tree = ttk.Treeview(
                akun_frame,
                columns=("tanggal", "keterangan", "debit", "kredit", "saldo"),
                show="headings",
                height=8
            )
            tree.pack(padx=10, pady=5)

            for col_name, text in zip(
                ("tanggal", "keterangan", "debit", "kredit", "saldo"),
                ("Tanggal", "Keterangan", "Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)")
            ):
                tree.heading(col_name, text=text)
                tree.column(col_name, anchor="center", width=130)

            # Hitung saldo dan total
            saldo = 0
            total_debit = 0
            total_kredit = 0

            for tgl, ket, debit, kredit in transaksi:
                saldo += debit - kredit
                total_debit += debit
                total_kredit += kredit

                tree.insert("", "end", values=(
                    tgl,
                    ket,
                    f"{debit:,.0f}" if debit else "",
                    f"{kredit:,.0f}" if kredit else "",
                    f"{saldo:,.0f}"
                ))

            # Baris total
            tree.insert("", "end", values=(
                "", "Total", f"{total_debit:,.0f}", f"{total_kredit:,.0f}", f"{saldo:,.0f}"
            ))

            row += 1  # tabel berikutnya di baris bawah

        if not ada_data:
            messagebox.showinfo("Info", "Tidak ada transaksi untuk bulan dan tahun ini.")


# === TESTING MANDIRI ===
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Buku Besar")
    root.geometry("1000x700")

    class DummyController:
        def show_frame(self, page_name):
            print(f"Kembali ke {page_name}")

    app = BukuBesarPage(root, DummyController())
    app.pack(fill="both", expand=True)
    root.mainloop()
