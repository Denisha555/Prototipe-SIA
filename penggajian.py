import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
from datetime import date

class PenggajianPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.current_gaji_id = tk.StringVar(value="")

        style = ttk.Style()
        style.configure("Title.TLabel", font=("Helvetica", 18, "bold"))
        style.configure("TLabel", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 11), padding=6)
        style.configure("Danger.TButton", foreground="red") 

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(self, text="💵 Pencatatan & Manajemen Penggajian", style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=20)

        input_frame = ttk.LabelFrame(self, text="Input Data Gaji", padding=15)
        input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsw")
        
        # Label ID Edit
        ttk.Label(input_frame, text="ID Data:").grid(row=0, column=0, sticky="e", pady=5, padx=5)
        ttk.Label(input_frame, textvariable=self.current_gaji_id, 
                  font=("Helvetica", 10, "bold"), foreground="blue").grid(row=0, column=1, pady=5, sticky="w")
        
        # Input Tanggal
        ttk.Label(input_frame, text="Tanggal Gaji").grid(row=1, column=0, sticky="e", pady=8, padx=5)
        self.entry_tanggal = DateEntry(input_frame, width=20, background='darkblue',
                                       foreground='white', borderwidth=2, 
                                       date_pattern="yyyy-mm-dd")
        self.entry_tanggal.grid(row=1, column=1, pady=8, padx=10, sticky="w")
        self.entry_tanggal.set_date(date.today())

        # Input Nama Karyawan
        ttk.Label(input_frame, text="Nama Karyawan").grid(row=2, column=0, sticky="e", pady=8, padx=5)
        # Contoh daftar karyawan
        self.entry_nama = ttk.Combobox(input_frame, values=["Amun (Manager)", "Anto (Staf)", "Denisha (Kasir)", "Yanto (Operator)"], 
                                       state="readonly", width=20)
        self.entry_nama.grid(row=2, column=1, pady=8, padx=10, sticky="w")

        # Input Gaji Bersih
        ttk.Label(input_frame, text="Gaji Bersih (Rp)").grid(row=3, column=0, sticky="e", pady=8, padx=5)
        def validate(P):
            return P.isdigit() or P == ""
        self.entry_gaji = ttk.Entry(input_frame, validate="key", width=23,
                                      validatecommand=(self.register(validate), '%P'))
        self.entry_gaji.grid(row=3, column=1, pady=8, padx=10, sticky="w")
        
        btn_form_frame = ttk.Frame(input_frame)
        btn_form_frame.grid(row=4, column=0, columnspan=2, pady=15)

        self.btn_simpan_update = ttk.Button(btn_form_frame, text="💾 Simpan/Update Gaji", command=self._save_or_update_gaji)
        self.btn_simpan_update.grid(row=0, column=0, padx=5)
        
        ttk.Button(btn_form_frame, text="🔄 Reset Form", command=self._reset_form).grid(row=0, column=1, padx=5)
        
        self.btn_hapus = ttk.Button(input_frame, text="❌ Hapus Data", 
                                     command=self._confirm_delete, style="Danger.TButton", state=tk.DISABLED)
        self.btn_hapus.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(input_frame, text="⬅️ Kembali ke Menu",
                   command=lambda: controller.show_frame("Menu")).grid(row=6, column=0, columnspan=2, pady=5)


        self.report_frame = ttk.LabelFrame(self, text="Data Penggajian (Double-klik untuk Edit)", padding="10")
        self.report_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        self.report_frame.columnconfigure(0, weight=1)
        self.report_frame.rowconfigure(0, weight=1)
        
        self.tree_gaji = self._setup_treeview(self.report_frame)
        self.tree_gaji.bind('<Double-1>', self._load_data_to_form)

        self.grid_rowconfigure(1, weight=1)
        
        self.load_transaksi_data()

    def _format_rupiah(self, value):
        """Memformat angka menjadi string Rupiah dengan pemisah titik."""
        try:
            value = int(value)
            return "Rp{:,.0f}".format(value).replace(",", "#").replace(".", ",").replace("#", ".")
        except:
            return "Rp0"

    def _reset_form(self):
        self.current_gaji_id.set("")
        self.entry_tanggal.set_date(date.today())
        self.entry_nama.set('')
        self.entry_gaji.delete(0, tk.END)
        self.btn_hapus.config(state=tk.DISABLED)
        messagebox.showinfo("Informasi", "Form telah direset ke mode pencatatan baru.")


    def _load_data_to_form(self, event):
        selected_item = self.tree_gaji.selection()
        if not selected_item:
            return

        values = self.tree_gaji.item(selected_item, 'values')
        
        gaji_id = values[0]
        tanggal = values[1]
        nama = values[2]
        gaji_str = values[3].replace('Rp', '').replace('.', '').strip() 

        self.current_gaji_id.set(gaji_id)
        self.entry_tanggal.set_date(tanggal)
        self.entry_nama.set(nama)
        self.entry_gaji.delete(0, tk.END)
        self.entry_gaji.insert(0, gaji_str)
        
        self.btn_hapus.config(state=tk.NORMAL)
        messagebox.showinfo("Edit Data", f"Data Gaji ID {gaji_id} dimuat untuk diubah.")


    def _save_or_update_gaji(self):
        tanggal = self.entry_tanggal.get()
        nama = self.entry_nama.get()
        gaji = self.entry_gaji.get()
        gaji_id = self.current_gaji_id.get()

        if not (tanggal and nama and gaji and gaji.isdigit()):
            messagebox.showerror("Error", "Semua field harus diisi dan Gaji harus berupa angka!")
            return
        
        try:
            conn = sqlite3.connect('data_keuangan.db')
            c = conn.cursor()
            
            if gaji_id:
                c.execute("UPDATE penggajian SET tanggal=?, nama_karyawan=?, gaji_bersih=? WHERE id=?",
                          (tanggal, nama, int(gaji), gaji_id))
                message = f"Gaji ID {gaji_id} berhasil diperbarui!"
            else:
                c.execute("INSERT INTO penggajian (tanggal, nama_karyawan, gaji_bersih) VALUES (?, ?, ?)",
                          (tanggal, nama, int(gaji)))
                message = f"Gaji {nama} berhasil dicatat!"

            conn.commit()
            conn.close()

            messagebox.showinfo("Sukses", message)
            self._reset_form()
            self.load_transaksi_data()

        except Exception as e:
            messagebox.showerror("Error", f"Gagal memproses data: {e}")
            
    def _confirm_delete(self):
        gaji_id = self.current_gaji_id.get()
        if not gaji_id:
            messagebox.showerror("Error", "Pilih data yang akan dihapus terlebih dahulu.")
            return

        if messagebox.askyesno("Konfirmasi Hapus", f"Anda yakin ingin menghapus data gaji ID {gaji_id}?"):
            self._delete_gaji(gaji_id)

    def _delete_gaji(self, gaji_id):
        try:
            conn = sqlite3.connect('data_keuangan.db')
            c = conn.cursor()
            c.execute("DELETE FROM penggajian WHERE id=?", (gaji_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Sukses", f"Data gaji ID {gaji_id} berhasil dihapus.")
            self._reset_form()
            self.load_transaksi_data()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menghapus data: {e}")


    def _setup_treeview(self, parent_frame):
        columns = ("ID", "Tanggal", "Nama Karyawan", "Gaji Bersih")
        tree = ttk.Treeview(parent_frame, columns=columns, show="headings", height=15)
        
        tree.column("ID", width=0, stretch=tk.NO)
        tree.heading("ID", text="ID")
        tree.column("Tanggal", width=100, anchor=tk.CENTER)
        tree.heading("Tanggal", text="Tanggal")
        tree.column("Nama Karyawan", width=150, anchor=tk.W)
        tree.heading("Nama Karyawan", text="Nama Karyawan")
        tree.column("Gaji Bersih", width=150, anchor=tk.E)
        tree.heading("Gaji Bersih", text="Gaji Bersih (Rp)")
        
        vsb = ttk.Scrollbar(parent_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        return tree

    def load_transaksi_data(self):
        for i in self.tree_gaji.get_children():
            self.tree_gaji.delete(i)
            
        try:
            conn = sqlite3.connect('data_keuangan.db')
            c = conn.cursor()
            c.execute("SELECT id, tanggal, nama_karyawan, gaji_bersih FROM penggajian ORDER BY tanggal DESC, id DESC")
            data = c.fetchall()
            conn.close()
            
            for row in data:
                formatted_jumlah = self._format_rupiah(row[3])
                formatted_row = (row[0], row[1], row[2], formatted_jumlah)
                self.tree_gaji.insert("", tk.END, values=formatted_row)
        
        except sqlite3.OperationalError:
            pass
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat data gaji: {e}")
