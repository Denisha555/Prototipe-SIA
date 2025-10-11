import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


class BukuBesarPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # --- Konfigurasi layout utama ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Judul Halaman ---
        ttk.Label(
            self,
            text="📘 Buku Besar",
            font=("Helvetica", 18, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(15, 5))

        bulan_list = [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]

        ttk.Label(self, text="Bulan:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.combo_bulan = ttk.Combobox(self, width=27, state="readonly", values=bulan_list)
        self.combo_bulan.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(self, text="Tahun:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_tahun = ttk.Entry(self, width=30)
        self.entry_tahun.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Button(self, text="Tampilkan", command=self.load_laporan).grid(
            row=3, column=0, padx=10, pady=5, columnspan=2
        )

        # --- Tombol kembali ---
        ttk.Button(
            self,
            text="Kembali ke Menu Utama",
            command=lambda: controller.show_frame("Menu Utama Manager")
        ).grid(row=4, column=0, columnspan=2, pady=(0, 10))

        # --- Scrollable area untuk tabel akun ---
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        # supaya scroll jalan
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=5, column=0, columnspan=1, sticky="nsew", padx=(15, 0), pady=10)
        scrollbar.grid(row=5, column=1, sticky="ns", padx=(0, 15))

        # # biar scroll area ikut resize
        # self.grid_rowconfigure(3, weight=1)

    # --- Fungsi utama untuk load laporan ---
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

        # Bersihkan frame dari tabel sebelumnya
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # --- Ambil data dari database ---
        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()

        # Kas masuk (penjualan)
        c.execute("""
            SELECT tanggal, kategori, total
            FROM transaksi_penjualan
            WHERE strftime('%m', tanggal)=? AND strftime('%Y', tanggal)=?
        """, (bulan_angka, tahun))
        kas_masuk = c.fetchall()

        # Kas keluar (pembelian)
        c.execute("""
            SELECT tanggal, kategori, total
            FROM transaksi_pembelian
            WHERE strftime('%m', tanggal)=? AND strftime('%Y', tanggal)=?
        """, (bulan_angka, tahun))
        kas_keluar = c.fetchall()

        conn.close()

        # --- Siapkan akun-akun utama ---
        akun_dict = {
            "Kas": [],
            "Pendapatan": [],
            "Peralatan": [],
            "Perlengkapan": [],
            "Biaya": [],
            "Beban": []
        }

        # Penjualan → Kas & Pendapatan
        for tanggal, kategori, total in kas_masuk:
            akun_dict["Kas"].append((tanggal, "Pendapatan", total, 0))
            akun_dict["Pendapatan"].append((tanggal, "Kas", 0, total))

        # Pembelian → Kas & akun terkait
        for tanggal, kategori, total in kas_keluar:
            if kategori in akun_dict:
                akun_dict[kategori].append((tanggal, "Kas", total, 0))
            else:
                akun_dict["Beban"].append((tanggal, "Kas", total, 0))
            akun_dict["Kas"].append((tanggal, kategori, 0, total))

        # --- Tampilkan ke layar (setiap akun punya tabel sendiri) ---
        ada_data = False

        for akun, transaksi in akun_dict.items():
            if not transaksi:
                continue

            ada_data = True
            ttk.Label(
                self.scrollable_frame,
                text=f"Akun: {akun}",
                font=("Helvetica", 14, "bold")
            ).pack(anchor="w", pady=(10, 0), padx=10)

            tree = ttk.Treeview(
                self.scrollable_frame,
                columns=("tanggal", "keterangan", "debit", "kredit", "saldo"),
                show="headings",
                height=8
            )
            tree.pack(fill="x", padx=10, pady=5)

            for col, text in zip(
                ("tanggal", "keterangan", "debit", "kredit", "saldo"),
                ("Tanggal", "Keterangan", "Debit (Rp)", "Kredit (Rp)", "Saldo (Rp)")
            ):
                tree.heading(col, text=text)
                tree.column(col, anchor="center", width=120)

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

        if not ada_data:
            messagebox.showinfo("Info", "Tidak ada transaksi untuk bulan dan tahun ini.")


# --- Untuk testing mandiri ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Buku Besar")
    root.geometry("950x700")

    class DummyController:
        def show_frame(self, page_name):
            print(f"Kembali ke {page_name}")

    app = BukuBesarPage(root, DummyController())
    app.pack(fill="both", expand=True)
    root.mainloop()
