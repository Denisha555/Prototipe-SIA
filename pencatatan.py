import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime, date
import uuid # Untuk menghasilkan ID transaksi unik

class PencatatanPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.current_transaction_id = tk.StringVar(value="")
        
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Helvetica", 18, "bold"))
        style.configure("TLabel", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 11), padding=6)
        style.configure("Danger.TButton", foreground="red") 

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(self, text="📒 Pencatatan & Manajemen Transaksi", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, pady=20
        )

        input_frame = ttk.LabelFrame(self, text="Input Data Transaksi", padding=15)
        input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsw")
        
        ttk.Label(input_frame, text="ID Transaksi:").grid(row=0, column=0, sticky="e", pady=5, padx=5)
        ttk.Label(input_frame, textvariable=self.current_transaction_id, 
                  font=("Helvetica", 10, "bold"), foreground="blue").grid(row=0, column=1, pady=5, sticky="w")
        
        # Input Tanggal
        ttk.Label(input_frame, text="Tanggal").grid(row=1, column=0, sticky="e", pady=8, padx=5)
        self.entry_tanggal = DateEntry(input_frame, width=20, background='darkblue',
                                       foreground='white', borderwidth=2, 
                                       date_pattern="yyyy-mm-dd")
        self.entry_tanggal.grid(row=1, column=1, pady=8, padx=10, sticky="w")
        self.entry_tanggal.set_date(date.today())

        # Input Kategori
        ttk.Label(input_frame, text="Kategori").grid(row=2, column=0, sticky="e", pady=8, padx=5)
        self.entry_kategori = ttk.Combobox(input_frame, values=["Pemasukan", "Pengeluaran"], state="readonly", width=20)
        self.entry_kategori.grid(row=2, column=1, pady=8, padx=10, sticky="w")
        self.entry_kategori.set("Pemasukan")

        # Input Jumlah
        ttk.Label(input_frame, text="Jumlah (Rp)").grid(row=3, column=0, sticky="e", pady=8, padx=5)
        def validate_jumlah(P):
            return P.isdigit() or P == ""
        self.entry_jumlah = ttk.Entry(input_frame, validate="key", width=23,
                                      validatecommand=(self.register(validate_jumlah), '%P'))
        self.entry_jumlah.grid(row=3, column=1, pady=8, padx=10, sticky="w")
        
        # Input Keterangan
        ttk.Label(input_frame, text="Keterangan (Opsional)").grid(row=4, column=0, sticky="e", pady=8, padx=5)
        self.entry_keterangan = tk.Text(input_frame, width=25, height=5)
        self.entry_keterangan.grid(row=4, column=1, pady=8, padx=10, sticky="w")

        # Tombol
        btn_form_frame = ttk.Frame(input_frame)
        btn_form_frame.grid(row=5, column=0, columnspan=2, pady=15)

        self.btn_simpan_update = ttk.Button(btn_form_frame, text="💾 Simpan/Update", command=self._save_or_update_data)
        self.btn_simpan_update.grid(row=0, column=0, padx=5)
        
        ttk.Button(btn_form_frame, text="🔄 Reset Form", command=self._reset_form).grid(row=0, column=1, padx=5)
        
        self.btn_hapus = ttk.Button(input_frame, text="❌ Hapus Data", 
                                     command=self._confirm_delete, style="Danger.TButton", state=tk.DISABLED)
        self.btn_hapus.grid(row=6, column=0, columnspan=2, pady=10)
        ttk.Button(input_frame, text="📑 Laporan",
                   command=lambda: controller.show_frame("Pelaporan")).grid(row=7, column=0, columnspan=2, pady=5)
        ttk.Button(input_frame, text="⬅️ Kembali ke Menu",
                   command=lambda: controller.show_frame("Menu")).grid(row=8, column=0, columnspan=2, pady=5)

        self.report_frame = ttk.LabelFrame(self, text="Daftar Transaksi (Double-klik untuk Edit)", padding="10")
        self.report_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        self.report_frame.columnconfigure(0, weight=1)
        self.report_frame.rowconfigure(0, weight=1)
        
        self.tree_transaksi = self._setup_treeview(self.report_frame)
        self.tree_transaksi.bind('<Double-1>', self._load_data_from_treeview)
        self.grid_rowconfigure(1, weight=1)
        
        self.load_transaksi_data()

    # --- Fungsi baru untuk format Rupiah ---
    def _format_rupiah(self, value):
        """Memformat angka menjadi string Rupiah dengan pemisah titik."""
        try:
            # Menggunakan format string untuk menghasilkan pemisah koma default
            value = int(value)
            # Swap koma (default ribuan) dengan titik dan titik (default desimal) dengan koma
            return "Rp{:,.0f}".format(value).replace(",", "#").replace(".", ",").replace("#", ".")
        except:
            return "Rp0"

    def _reset_form(self):
        self.current_transaction_id.set("")
        self.entry_tanggal.set_date(date.today())
        self.entry_kategori.set('Pemasukan')
        self.entry_jumlah.delete(0, tk.END)
        self.entry_keterangan.delete('1.0', tk.END)
        self.btn_hapus.config(state=tk.DISABLED)


    def _load_data_from_treeview(self, event):
        selected_item = self.tree_transaksi.selection()
        if not selected_item:
            return
        values = self.tree_transaksi.item(selected_item, 'values')
        # Hapus format Rupiah sebelum memuat ke entry jumlah
        jumlah_str = values[2].replace('Rp', '').replace('.', '').strip() 
        self._load_data_to_form(values[0], values[1], jumlah_str, values[3], values[4])

    def _load_data_to_form(self, id_transaksi, tanggal, jumlah, kategori, keterangan):
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

        self.btn_hapus.config(state=tk.NORMAL)
        messagebox.showinfo("Edit Data", f"Transaksi ID {id_transaksi} dimuat untuk diubah. Tekan Simpan/Update atau Hapus.")
        
    def load_selected_transaction(self, data):
    
        self._load_data_to_form(data[0], data[1], data[2], data[3], data[4])
        self.controller.show_frame("Pencatatan")


    def _generate_transaction_id(self, tanggal, kategori):
        conn = sqlite3.connect('data_keuangan.db')
        c = conn.cursor()

        label_kategori = "M" if kategori == "Pemasukan" else "K"
        label_tanggal = tanggal.replace("-", "")

        c.execute("SELECT COUNT(*) FROM transaksi WHERE tanggal=?", (tanggal,))
        count = c.fetchone()[0]

        nomor_urut = count + 1
        id_transaksi = f"{label_kategori}{label_tanggal}{nomor_urut:03d}"
        
        conn.close()
        return id_transaksi


    def _save_or_update_data(self):
        id_transaksi = self.current_transaction_id.get()
        tanggal = self.entry_tanggal.get()
        kategori = self.entry_kategori.get()
        jumlah_str = self.entry_jumlah.get()
        keterangan = self.entry_keterangan.get('1.0', tk.END).strip() 

        if not (tanggal and kategori and jumlah_str.isdigit()):
            messagebox.showerror("Error", "Tanggal, Kategori, dan Jumlah harus diisi. (Pastikan Jumlah adalah Angka).")
            return

        jumlah = int(jumlah_str)

        conn = sqlite3.connect('data_keuangan.db')
        c = conn.cursor()
        
        try:
            is_update = bool(id_transaksi)
            
            if is_update:
                c.execute("""
                    UPDATE transaksi SET tanggal=?, kategori=?, keterangan=?, jumlah=? 
                    WHERE id=?
                """, (tanggal, kategori, keterangan, jumlah, id_transaksi))
                message = f"Transaksi ID {id_transaksi} berhasil diperbarui!"
            else:
                id_transaksi = self._generate_transaction_id(tanggal, kategori)
                c.execute("INSERT INTO transaksi (id, tanggal, kategori, keterangan, jumlah) VALUES (?, ?, ?, ?, ?)",
                          (id_transaksi, tanggal, kategori, keterangan, jumlah))
                message = f"Data berhasil disimpan dengan ID {id_transaksi}!"

            conn.commit()
            messagebox.showinfo("Sukses", message)
            self.load_transaksi_data()
            self._reset_form()
            

        except sqlite3.Error as e:
            messagebox.showerror("Error Database", f"Gagal memproses data: {e}")
        finally:
            conn.close()


    def _confirm_delete(self):
        id_transaksi = self.current_transaction_id.get()
        if not id_transaksi:
            messagebox.showerror("Error", "Pilih data yang akan dihapus terlebih dahulu.")
            return

        # Mengganti konfirmasi default dengan modal jika perlu, tapi kita gunakan askyesno untuk kesederhanaan
        if messagebox.askyesno("Konfirmasi Hapus", f"Anda yakin ingin menghapus transaksi dengan ID {id_transaksi}? Tindakan ini tidak dapat dibatalkan."):
            self._delete_data(id_transaksi)

    def _delete_data(self, id_transaksi):
        conn = sqlite3.connect('data_keuangan.db')
        c = conn.cursor()
        
        try:
            c.execute("DELETE FROM transaksi WHERE id=?", (id_transaksi,))
            conn.commit()
            
            messagebox.showinfo("Sukses", f"Transaksi ID {id_transaksi} berhasil dihapus.")
            self.load_transaksi_data()
            self._reset_form()
            

        except sqlite3.Error as e:
            messagebox.showerror("Error Database", f"Gagal menghapus data: {e}")
        finally:
            conn.close()


    def _setup_treeview(self, parent_frame):
        columns = ("ID", "Tanggal", "Jumlah", "Kategori", "Keterangan")
        tree = ttk.Treeview(parent_frame, columns=columns, show="headings", height=15)
        
        tree.column("ID", width=0, stretch=tk.NO)
        tree.heading("ID", text="ID")
        tree.column("Tanggal", width=90, anchor=tk.CENTER)
        tree.heading("Tanggal", text="Tanggal")
        tree.column("Jumlah", width=110, anchor=tk.E)
        tree.heading("Jumlah", text="Jumlah (Rp)")
        tree.column("Kategori", width=100, anchor=tk.CENTER)
        tree.heading("Kategori", text="Kategori")
        tree.column("Keterangan", width=200, anchor=tk.W)
        tree.heading("Keterangan", text="Keterangan")
        
        vsb = ttk.Scrollbar(parent_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        return tree

    def load_transaksi_data(self):
        for i in self.tree_transaksi.get_children():
            self.tree_transaksi.delete(i)
            
        try:
            conn = sqlite3.connect('data_keuangan.db')
            c = conn.cursor()
            c.execute("SELECT id, tanggal, jumlah, kategori, keterangan FROM transaksi ORDER BY tanggal DESC, id DESC")
            data = c.fetchall()
            conn.close()
            
            for row in data:
                # Memanggil _format_rupiah untuk memformat kolom Jumlah (index 2)
                formatted_jumlah = self._format_rupiah(row[2])
                formatted_row = (row[0], row[1], formatted_jumlah, row[3], row[4])
                self.tree_transaksi.insert("", tk.END, values=formatted_row)
        
        except sqlite3.OperationalError:
            pass
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat data transaksi: {e}")
