import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GrafikKomposisiAsetPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # ===============================
        # STYLE
        # ===============================
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Helvetica", 18, "bold"))
        style.configure("Primary.TButton",
                        font=("Helvetica", 12, "bold"),
                        padding=10)
        style.configure("Danger.TButton",
                        font=("Helvetica", 12, "bold"),
                        padding=10)

        # ===============================
        # TITLE
        # ===============================
        ttk.Label(self, text="⚗️ Grafik Komposisi Aset", style="Title.TLabel").pack(pady=(20, 10))

        ttk.Button(self, text="Tampilkan Grafik",
                   command=self.tampilkan_grafik).pack(pady=10)
        
        # ===============================
        # TOMBOL KEMBALI
        # ===============================
        ttk.Button(self, text="Kembali ke Menu Utama",
                   command=lambda: controller.show_frame("Menu Utama Manager")
                   ).pack(pady=(10, 25))

        # ===============================
        # CANVAS MATPLOTLIB
        # ===============================
        self.figure = plt.Figure(figsize=(6, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.canvas.draw()

        self.tampilkan_grafik()

    def tampilkan_grafik(self):
        try:
            conn = sqlite3.connect("data_keuangan.db")
            c = conn.cursor()

            # Ambil akun kategori "Aset"
            c.execute("SELECT kode_akun, nama_akun FROM akun WHERE kategori = 'Aset'")
            aset_akun = c.fetchall()

            labels = []
            values = []

            # Hitung saldo akhir tiap akun aset (termasuk penyesuaian)
            for kode_akun, nama_akun in aset_akun:
                c.execute("""
                    SELECT 
                        COALESCE(SUM(debit), 0) - COALESCE(SUM(kredit), 0)
                    FROM jurnal_umum_detail
                    WHERE kode_akun = ?
                      AND jenis_jurnal IN ('UMUM', 'PENYESUAIAN')
                """, (kode_akun,))
                saldo = c.fetchone()[0]
                if saldo != 0:
                    labels.append(nama_akun)
                    values.append(saldo)

            conn.close()

            # Tidak ada data
            self.ax.clear()
            if not values:
                self.ax.axis('off')
                self.ax.text(0.5, 0.5, "Tidak ada data aset untuk ditampilkan.",
                             ha='center', va='center', fontsize=11, color='gray')
                self.canvas.draw()
                return

            # Gambar pie chart
            labels_with_saldo = []
            for nama, saldo in zip(labels, values):
                formatted_saldo = f"{saldo:,.0f}".replace(",", "#").replace(".", ",").replace("#", ".") # Format titik
                labels_with_saldo.append(f"{nama}\nRp {formatted_saldo}")

            self.ax.pie(
                values,
                labels=labels_with_saldo,
                autopct='%1.1f%%',
                startangle=140,
                textprops={'fontsize': 10}
            )

            self.ax.axis('equal')
            self.ax.set_title("Komposisi Aset Berdasarkan Akun", fontsize=14, fontweight="bold")

            self.canvas.draw()

        except sqlite3.Error as e:
            messagebox.showerror("Error Database", f"Gagal mengambil data aset: {e}")


