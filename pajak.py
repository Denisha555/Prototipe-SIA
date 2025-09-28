import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
from datetime import date

class PajakPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.current_pajak_id = tk.StringVar(value="")

        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 11), padding=6)
        style.configure("Title.TLabel", font=("Helvetica", 18, "bold"))
        style.configure("Danger.TButton", foreground="red")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(self, text="🧾 Pencatatan & Manajemen Pajak", style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=20)

        input_frame = ttk.LabelFrame(self, text="Input Data Pajak", padding=15)
        input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsw")
        
        # Label ID Edit
        ttk.Label(input_frame, text="ID Data:").grid(row=0, column=0, sticky="e", pady=5, padx=5)
        ttk.Label(input_frame, textvariable=self.current_pajak_id, 
                  font=("Helvetica", 10, "bold"), foreground="blue").grid(row=0, column=1, pady=5, sticky="w")
        
        # Input Tanggal
        ttk.Label(input_frame, text="Tanggal Setor").grid(row=1, column=0, sticky="e", pady=8, padx=5)
        self.entry_tanggal = DateEntry(input_frame, width=20, background='darkblue',
                                       foreground='white', borderwidth=2, 
                                       date_pattern="yyyy-mm-dd")
        self.entry_tanggal.grid(row=1, column=1, pady=8, padx=10, sticky="w")
        self.entry_tanggal.set_date(date.today())

        # Input Jenis Pajak
        ttk.Label(input_frame, text="Jenis Pajak").grid(row=2, column=0, sticky="e", pady=8, padx=5)
        self.entry_jenis = ttk.Combobox(input_frame, values=["PPN", "PPh 21", "PPh 23", "Pajak Daerah"], 
                                       state="readonly", width=20)
        self.entry_jenis.grid(row=2, column=1, pady=8, padx=10, sticky="w")

        # Input Jumlah
        ttk.Label(input_frame, text="Jumlah Setor (Rp)").grid(row=3, column=0, sticky="e", pady=8, padx=5)
        def validate(P):
            return P.isdigit() or P == ""
        self.entry_jumlah = ttk.Entry(input_frame, validate="key", width=23,
                                      validatecommand=(self.register(validate), '%P'))
        self.entry_jumlah.grid(row=3, column=1, pady=8, padx=10, sticky="w")
        
        btn_form_frame = ttk.Frame(input_frame)
        btn_form_frame.grid(row=4, column=0, columnspan=2, pady=15)

        self.btn_simpan_update = ttk.Button(btn_form_frame, text="💾 Simpan/Update Pajak", command=self._save_or_update_pajak)
        self.btn_simpan_update.grid(row=0, column=0, padx=5)
        
        ttk.Button(btn_form_frame, text="🔄 Reset Form", command=self._reset_form).grid(row=0, column=1, padx=5)
        
        self.btn_hapus = ttk.Button(input_frame, text="❌ Hapus Data", 
                                     command=self._confirm_delete, style="Danger.TButton", state=tk.DISABLED)
        self.btn_hapus.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(input_frame, text="⬅️ Kembali ke Menu",
                   command=lambda: controller.show_frame("Menu")).grid(row=6, column=0, columnspan=2, pady=5)

        self.report_frame = ttk.LabelFrame(self, text="Data Setoran Pajak (Double-klik untuk Edit)", padding="10")
        self.report_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        self.report_frame.columnconfigure(0, weight=1)
        self.report_frame.rowconfigure(0, weight=1)
        
        self.tree_pajak = self._setup_treeview(self.report_frame)
        self.tree_pajak.bind('<Double-1>', self._load_data_to_form)

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
        self.current_pajak_id.set("")
        self.entry_tanggal.set_date(date.today())
        self.entry_jenis.set('')
        self.entry_jumlah.delete(0, tk.END)
        self.btn_hapus.config(state=tk.DISABLED)
        messagebox.showinfo("Informasi", "Form telah direset ke mode pencatatan baru.")


    def _load_data_to_form(self, event):
        selected_item = self.tree_pajak.selection()
        if not selected_item:
            return

        values = self.tree_pajak.item(selected_item, 'values')
        
        pajak_id = values[0]
        tanggal = values[1]
        jenis = values[2]
        jumlah_str = values[3].replace('Rp', '').replace('.', '').strip() 

        self.current_pajak_id.set(pajak_id)
        self.entry_tanggal.set_date(tanggal)
        self.entry_jenis.set(jenis)
        self.entry_jumlah.delete(0, tk.END)
        self.entry_jumlah.insert(0, jumlah_str)
        
        self.btn_hapus.config(state=tk.NORMAL)
        messagebox.showinfo("Edit Data", f"Data Pajak ID {pajak_id} dimuat untuk diubah.")


    def _save_or_update_pajak(self):
        tanggal = self.entry_tanggal.get()
        jenis = self.entry_jenis.get()
        jumlah = self.entry_jumlah.get()
        pajak_id = self.current_pajak_id.get()

        if not (tanggal and jenis and jumlah and jumlah.isdigit()):
            messagebox.showerror("Error", "Semua field harus diisi dan Jumlah harus berupa angka!")
            return
        
        try:
            conn = sqlite3.connect('data_keuangan.db')
            c = conn.cursor()
            
            if pajak_id:
                c.execute("UPDATE pajak SET tanggal=?, jenis_pajak=?, jumlah=? WHERE id=?",
                          (tanggal, jenis, int(jumlah), pajak_id))
                message = f"Data Pajak ID {pajak_id} berhasil diperbarui!"
            else:
                c.execute("INSERT INTO pajak (tanggal, jenis_pajak, jumlah) VALUES (?, ?, ?)",
                          (tanggal, jenis, int(jumlah)))
                message = f"Setoran Pajak {jenis} berhasil dicatat!"

            conn.commit()
            conn.close()

            messagebox.showinfo("Sukses", message)
            self._reset_form()
            self.load_transaksi_data()

        except Exception as e:
            messagebox.showerror("Error", f"Gagal memproses data: {e}")
            

    def _confirm_delete(self):
        pajak_id = self.current_pajak_id.get()
        if not pajak_id:
            messagebox.showerror("Error", "Pilih data yang akan dihapus terlebih dahulu.")
            return

        if messagebox.askyesno("Konfirmasi Hapus", f"Anda yakin ingin menghapus data pajak ID {pajak_id}?"):
            self._delete_pajak(pajak_id)

    def _delete_pajak(self, pajak_id):
        try:
            conn = sqlite3.connect('data_keuangan.db')
            c = conn.cursor()
            c.execute("DELETE FROM pajak WHERE id=?", (pajak_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Sukses", f"Data pajak ID {pajak_id} berhasil dihapus.")
            self._reset_form()
            self.load_transaksi_data()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menghapus data: {e}")


    def _setup_treeview(self, parent_frame):
        columns = ("ID", "Tanggal", "Jenis Pajak", "Jumlah")
        tree = ttk.Treeview(parent_frame, columns=columns, show="headings", height=15)
        
        tree.column("ID", width=0, stretch=tk.NO)
        tree.heading("ID", text="ID")
        tree.column("Tanggal", width=100, anchor=tk.CENTER)
        tree.heading("Tanggal", text="Tanggal Setor")
        tree.column("Jenis Pajak", width=150, anchor=tk.W)
        tree.heading("Jenis Pajak", text="Jenis Pajak")
        tree.column("Jumlah", width=150, anchor=tk.E)
        tree.heading("Jumlah", text="Jumlah (Rp)")
        
        vsb = ttk.Scrollbar(parent_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        return tree

    def load_transaksi_data(self):
        for i in self.tree_pajak.get_children():
            self.tree_pajak.delete(i)
            
        try:
            conn = sqlite3.connect('data_keuangan.db')
            c = conn.cursor()
            c.execute("SELECT id, tanggal, jenis_pajak, jumlah FROM pajak ORDER BY tanggal DESC, id DESC")
            data = c.fetchall()
            conn.close()
            
            for row in data:
                formatted_jumlah = self._format_rupiah(row[3])
                formatted_row = (row[0], row[1], row[2], formatted_jumlah)
                self.tree_pajak.insert("", tk.END, values=formatted_row)
        
        except sqlite3.OperationalError:
            pass 
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat data pajak: {e}")
