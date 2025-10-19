import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GrafikKomposisiAsetPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="📊 Grafik Komposisi Aset", font=("Helvetica", 18, "bold")).pack(pady=15)

        ttk.Button(self, text="Tampilkan", command=self.tampilkan_grafik).pack(pady=10)

        # Canvas matplotlib
        self.figure = plt.Figure(figsize=(7, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Button(self, text="Kembali ke Menu Utama",
                   command=lambda: controller.show_frame("Menu Utama Manager")).pack(pady=5)

    def tampilkan_grafik(self):
        try:
            conn = sqlite3.connect("data_keuangan.db")
            c = conn.cursor()

            # Ambil akun kategori "Aset"
            c.execute("SELECT kode_akun, nama_akun FROM akun WHERE kategori = 'Aset'")
            aset_akun = c.fetchall()

            labels = []
            values = []

            # Hitung saldo akhir tiap akun aset
            for kode_akun, nama_akun in aset_akun:
                c.execute("""
                    SELECT 
                        COALESCE(SUM(debit), 0) - COALESCE(SUM(kredit), 0)
                    FROM jurnal_umum_detail
                    WHERE kode_akun = ?
                    AND jenis_jurnal IN ('UMUM', 'PENYESUAIAN')
                """, (kode_akun,))
                saldo = c.fetchone()[0]
                if saldo != 0:  # hanya tampilkan kalau ada saldo
                    labels.append(nama_akun)
                    values.append(saldo)

            conn.close()

            if not values:
                messagebox.showinfo("Info", "Tidak ada data aset untuk ditampilkan.")
                self.ax.clear()
                self.canvas.draw()
                return

            # Gambar pie chart
            self.ax.clear()
            labels_with_saldo = [f"{nama}\nRp {saldo:,.0f}" for nama, saldo in zip(labels, values)]

            self.ax.pie(
                values,
                labels=labels_with_saldo,
                autopct='%1.1f%%',
                startangle=140,
                textprops={'fontsize': 10}
            )

            self.ax.set_title("Komposisi Aset", fontsize=14, fontweight="bold")
            self.canvas.draw()

        except sqlite3.Error as e:
            messagebox.showerror("Error Database", f"Gagal mengambil data aset: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    class dummy :
        def show_frame(self, name):
            pass
    app = GrafikKomposisiAsetPage(root, dummy())
    app.pack()
    app.mainloop()