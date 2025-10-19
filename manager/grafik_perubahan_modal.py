import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Asumsi bulan_map diimpor atau didefinisikan
try:
    from function.bulan_map import bulan_map
except ImportError:
    # Definisi dummy jika import gagal, sesuai dengan konteks file
    bulan_map = {
        "Januari": "01", "Februari": "02", "Maret": "03", 
        "April": "04", "Mei": "05", "Juni": "06",
        "Juli": "07", "Agustus": "08", "September": "09",
        "Oktober": "10", "November": "11", "Desember": "12"
    }

class GrafikModalPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="📈 Grafik Perubahan Modal Tahunan", font=("Helvetica", 18, "bold")).pack(pady=15)

        # Frame filter (Hanya Tahun)
        filter_frame = ttk.Frame(self)
        filter_frame.pack(pady=5)

        ttk.Label(filter_frame, text="Tahun:").grid(row=0, column=0, padx=5)
        self.entry_tahun = ttk.Entry(filter_frame, width=10)
        self.entry_tahun.grid(row=0, column=1, padx=5)

        ttk.Button(filter_frame, text="Tampilkan Grafik", command=self.tampilkan_grafik).grid(row=0, column=2, padx=10)

        ttk.Button(self, text="Kembali ke Menu Utama",
                   command=lambda: controller.show_frame("Menu Utama Manager")).pack(pady=10)

        # Canvas untuk grafik
        self.figure = plt.Figure(figsize=(8, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Default tahun
        current_year = datetime.now().strftime("%Y")
        self.entry_tahun.insert(0, current_year)
        
        # Tampilkan grafik default saat pertama kali dimuat
        self.tampilkan_grafik()

    def tampilkan_grafik(self):
        """Mengambil data modal bulanan dari rekap_modal dan menampilkan grafik garis."""
        tahun = self.entry_tahun.get()

        if not tahun.isdigit() or len(tahun) != 4:
            messagebox.showerror("Error", "Masukkan tahun yang valid (contoh: 2023)!")
            return

        try:
            conn = sqlite3.connect("data_keuangan.db")
            c = conn.cursor()

            # Mengambil semua modal_akhir dari rekap_modal di tahun tersebut, diurutkan
            # Kita hanya ambil tanggal dan modal_akhir
            c.execute("""
                SELECT strftime('%m', tanggal), modal_akhir 
                FROM rekap_modal
                WHERE strftime('%Y', tanggal) = ?
                ORDER BY tanggal ASC
            """, (tahun,))

            data = c.fetchall()
            conn.close()

            if not data:
                messagebox.showinfo("Info", f"Tidak ada data perubahan modal yang terekam untuk tahun {tahun}.\nPastikan Laporan Perubahan Modal sudah dibuat untuk bulan-bulan di tahun tersebut.")
                self.ax.clear()
                self.canvas.draw()
                return

            # Persiapan data untuk plotting
            # Map Angka Bulan ('01'...'12') ke Nama Bulan
            bulan_terisi = {v: k for k, v in bulan_map.items()} 
            
            # Buat dictionary untuk menampung modal akhir per bulan
            modal_akhir_bulanan = {} 
            
            for bulan_num, modal_akhir in data:
                # Ambil modal akhir dari rekap modal
                # Jika ada beberapa entry untuk bulan yang sama, ambil yang terakhir
                modal_akhir_bulanan[bulan_num] = modal_akhir

            # Urutan Bulan (dari 01 sampai 12)
            bulan_labels_order = sorted(list(bulan_map.values()))
            
            # Data yang akan diplot
            # Gunakan nama bulan dari bulan_map.keys()
            labels_plot = [bulan_terisi.get(num, num) for num in bulan_labels_order] # Nama Bulan
            # Ambil nilai modal akhir, jika bulan tidak ada data, gunakan 0
            values_plot = [modal_akhir_bulanan.get(num, 0) for num in bulan_labels_order] 

            # --- Gambar grafik garis ---
            self.ax.clear()
            
            # Grafik Garis (Line Chart)
            self.ax.plot(labels_plot, values_plot, marker='o', linestyle='-', color='#8B4513', linewidth=2, label="Modal Akhir")
            
            # Tambahkan label nilai di atas titik
            for i, val in enumerate(values_plot):
                # Hanya tampilkan label untuk nilai > 0
                if val > 0:
                    self.ax.text(labels_plot[i], val, f'Rp{int(val):,}', ha='center', va='bottom', fontsize=8)

            self.ax.set_title(f"Grafik Perubahan Modal Pemilik Tahun {tahun}", fontsize=12, fontweight="bold")
            self.ax.set_xlabel("Bulan")
            self.ax.set_ylabel("Saldo Modal (Rp)")
            
            # Rotasi label X agar tidak tumpang tindih
            plt.setp(self.ax.get_xticklabels(), rotation=45, ha="right")
            
            self.ax.grid(axis='y', linestyle='--', alpha=0.7)
            self.ax.ticklabel_format(axis='y', style='plain') # Cegah notasi ilmiah pada sumbu Y
            self.figure.tight_layout(pad=3.0) # Sesuaikan layout
            self.canvas.draw()

        except sqlite3.Error as e:
            messagebox.showerror("Error Database", f"Gagal mengambil data Modal: {e}")

if __name__ == "__main__":
    # Contoh koneksi database dummy untuk testing mandiri
    def create_dummy_db():
        conn = sqlite3.connect('data_keuangan.db')
        c = conn.cursor()
        
        # Asumsikan tabel rekap_modal sudah ada (sesuai skema database)
        # Hapus dan buat ulang untuk testing
        c.execute("DROP TABLE IF EXISTS rekap_modal")
        c.execute("""
            CREATE TABLE rekap_modal(                   
                id INTEGER PRIMARY KEY AUTOINCREMENT,                   
                tanggal DATE,                   
                modal_awal INTEGER,                   
                modal_akhir INTEGER)
        """)
        
        # Data dummy untuk tahun 2024
        # Ini adalah data MODAL AKHIR BULAN
        c.execute("INSERT INTO rekap_modal VALUES (NULL, '2024-01-31', 10000000, 10500000)")
        c.execute("INSERT INTO rekap_modal VALUES (NULL, '2024-02-29', 10500000, 11200000)")
        c.execute("INSERT INTO rekap_modal VALUES (NULL, '2024-03-31', 11200000, 10900000)")
        c.execute("INSERT INTO rekap_modal VALUES (NULL, '2024-04-30', 10900000, 12000000)")
        c.execute("INSERT INTO rekap_modal VALUES (NULL, '2024-05-31', 12000000, 12500000)")
        c.execute("INSERT INTO rekap_modal VALUES (NULL, '2024-06-30', 12500000, 13100000)")

        conn.commit()
        conn.close()

    create_dummy_db()
    
    root = tk.Tk()
    root.title("Grafik Perubahan Modal")
    
    # Class Controller Dummy
    class ControllerDummy:
        def show_frame(self, page_name):
            print(f"Pindah ke halaman: {page_name}")
            
    frame = GrafikModalPage(root, ControllerDummy())
    frame.pack(expand=True, fill="both")
    root.mainloop()