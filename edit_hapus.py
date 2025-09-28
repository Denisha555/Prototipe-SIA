import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkcalendar import DateEntry
from datetime import datetime

class EditHapusPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.current_transaction_id = tk.StringVar()

        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 11), padding=6)
        style.configure("Title.TLabel", font=("Helvetica", 18, "bold"))

        ttk.Label(self, text="📄 Edit & Hapus Transaksi", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, pady=20
        )
        
        ttk.Label(self, text="ID Transaksi:").grid(row=1, column=0, sticky="e", pady=8)
        ttk.Label(self, textvariable=self.current_transaction_id, 
                  font=("Helvetica", 12, "bold"), foreground="blue").grid(
            row=1, column=1, pady=8, padx=10, sticky="w"
        )

        # Input Tanggal
        ttk.Label(self, text="Tanggal Baru").grid(row=2, column=0, sticky="e", pady=8)
        self.entry_tanggal = DateEntry(self, width=20, background='darkblue',
                                       foreground='white', borderwidth=2, 
                                       date_pattern="yyyy-mm-dd")
        self.entry_tanggal.grid(row=2, column=1, pady=8, padx=10, sticky="w")

        # Input Kategori
        ttk.Label(self, text="Kategori Baru").grid(row=3, column=0, sticky="e", pady=8)
        self.entry_kategori = ttk.Combobox(self, values=["Pemasukan", "Pengeluaran"], state="readonly", width=20)
        self.entry_kategori.grid(row=3, column=1, pady=8, padx=10, sticky="w")

        # Input Jumlah
        ttk.Label(self, text="Jumlah Baru (Rp)").grid(row=4, column=0, sticky="e", pady=8)
        self.entry_jumlah = ttk.Entry(self, width=23)
        self.entry_jumlah.grid(row=4, column=1, pady=8, padx=10, sticky="w")
        
        # Input Keterangan
        ttk.Label(self, text="Keterangan Baru").grid(row=5, column=0, sticky="e", pady=8)
        self.entry_keterangan = tk.Text(self, width=25, height=5)
        self.entry_keterangan.grid(row=5, column=1, pady=8, padx=10, sticky="w")

        # Tombol
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)

        self.btn_update = ttk.Button(btn_frame, text="✏️ Update Data", command=self._update_transaksi)
        self.btn_update.grid(row=0, column=0, padx=10)
        
        self.btn_hapus = ttk.Button(btn_frame, text="❌ Hapus Data", command=self._confirm_hapus, style="Danger.TButton")
        self.btn_hapus.grid(row=0, column=1, padx=10)
        
        ttk.Button(btn_frame, text="⬅️ Kembali ke Menu",
                   command=lambda: controller.show_frame("Menu")).grid(row=0, column=2, padx=10)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        style.configure("Danger.TButton", foreground="red")


    def load_data(self, id_transaksi, tanggal, jumlah, kategori, keterangan):
        self.current_transaction_id.set(id_transaksi)

        try:
            date_obj = datetime.strptime(tanggal, '%Y-%m-%d').date()
            self.entry_tanggal.set_date(date_obj)
        except ValueError:
            self.entry_tanggal.set_date(datetime.now().date())

        self.entry_kategori.set(kategori)
        
        self.entry_jumlah.delete(0, tk.END)
        self.entry_jumlah.insert(0, str(jumlah))
        
        self.entry_keterangan.delete('1.0', tk.END)
        self.entry_keterangan.insert('1.0', keterangan)


    def _update_transaksi(self):
        id_transaksi = self.current_transaction_id.get()
        if not id_transaksi:
            messagebox.showerror("Error", "ID Transaksi tidak ditemukan.")
            return

        tanggal = self.entry_tanggal.get_date().strftime('%Y-%m-%d')
        kategori = self.entry_kategori.get()
        jumlah_str = self.entry_jumlah.get().replace(",", "").strip()
        keterangan = self.entry_keterangan.get('1.0', tk.END).strip()
        
        if not (tanggal and kategori and jumlah_str.isdigit()):
            messagebox.showerror("Error", "Semua kolom harus diisi dengan benar.")
            return

        jumlah = int(jumlah_str)
        
        conn = sqlite3.connect('data_keuangan.db')
        c = conn.cursor()
        
        try:
            c.execute("""
                UPDATE transaksi SET tanggal=?, kategori=?, keterangan=?, jumlah=? 
                WHERE id=?
            """, (tanggal, kategori, keterangan, jumlah, id_transaksi))
            conn.commit()
            
            messagebox.showinfo("Sukses", f"Transaksi ID {id_transaksi} berhasil diperbarui.")
            
            self.controller.show_frame("Menu")

        except sqlite3.Error as e:
            messagebox.showerror("Error Database", f"Gagal mengupdate data: {e}")
        finally:
            conn.close()


    def _confirm_hapus(self):
        id_transaksi = self.current_transaction_id.get()
        if messagebox.askyesno("Konfirmasi Hapus", f"Anda yakin ingin menghapus transaksi dengan ID {id_transaksi}?"):
            self._hapus_transaksi(id_transaksi)


    def _hapus_transaksi(self, id_transaksi):
        conn = sqlite3.connect('data_keuangan.db')
        c = conn.cursor()
        
        try:
            c.execute("DELETE FROM transaksi WHERE id=?", (id_transaksi,))
            conn.commit()
            
            messagebox.showinfo("Sukses", f"Transaksi ID {id_transaksi} berhasil dihapus.")
            
            self.controller.show_frame("Menu")

        except sqlite3.Error as e:
            messagebox.showerror("Error Database", f"Gagal menghapus data: {e}")
        finally:
            conn.close()
            
    def load_transaksi_data(self):
        pass
