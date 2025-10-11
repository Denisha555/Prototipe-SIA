import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

try:
    from function.bulan_map import bulan_map
except ImportError:
    bulan_map = {
        "Januari": "01", "Februari": "02", "Maret": "03", 
        "April": "04", "Mei": "05", "Juni": "06",
        "Juli": "07", "Agustus": "08", "September": "09",
        "Oktober": "10", "November": "11", "Desember": "12"
    }

def _connect_db():
    return sqlite3.connect('data_keuangan.db')

def _format_rupiah(amount):
    return f"Rp{amount:,.0f}"

class NeracaSaldoPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ttk.Label(
            self,
            text="🧾 Neraca Saldo (Sebelum Penyesuaian)",
            font=("Helvetica", 18, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(15, 10))

        form_frame = ttk.Frame(self)
        form_frame.grid(row=1, column=0, columnspan=2, pady=10)

        bulan_list = list(bulan_map.keys())
        current_month_name = datetime.now().strftime("%B")
        
        english_to_indo = {
            "January": "Januari", "February": "Februari", "March": "Maret", 
            "April": "April", "May": "Mei", "June": "Juni",
            "July": "Juli", "August": "Agustus", "September": "September",
            "October": "Oktober", "November": "November", "December": "Desember"
        }
        default_month = english_to_indo.get(current_month_name, "Januari")

        ttk.Label(form_frame, text="Bulan:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.combo_bulan = ttk.Combobox(form_frame, width=27, state="readonly", values=bulan_list)
        self.combo_bulan.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.combo_bulan.set(default_month)

        ttk.Label(form_frame, text="Tahun:").grid(row=0, column=2, padx=10, pady=5, sticky="e")
        self.entry_tahun = ttk.Entry(form_frame, width=10)
        self.entry_tahun.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.entry_tahun.insert(0, str(datetime.now().year))

        ttk.Button(form_frame, text="Tampilkan Neraca Saldo", command=self.load_neraca_saldo).grid(row=0, column=4, padx=15)

        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=("kode", "akun", "debit", "kredit"), show="headings", height=15)

        self.tree.column("kode", width=80, anchor="center")
        self.tree.heading("kode", text="Kode Akun")
        self.tree.column("akun", width=250, anchor="w")
        self.tree.heading("akun", text="Nama Akun")
        self.tree.column("debit", width=150, anchor="e")
        self.tree.heading("debit", text="Saldo Debit (Rp)")
        self.tree.column("kredit", width=150, anchor="e")
        self.tree.heading("kredit", text="Saldo Kredit (Rp)")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        ttk.Button(self, text="Kembali ke menu utama", command=lambda: controller.show_frame("Menu Utama Manager")).grid(row=3, column=0, columnspan=2, pady=10)


    def load_neraca_saldo(self):
        bulan_nama = self.combo_bulan.get()
        tahun = self.entry_tahun.get()

        if not bulan_nama or not tahun:
            messagebox.showerror("Error", "Bulan dan Tahun harus diisi.")
            return

        try:
            bulan_num = bulan_map[bulan_nama]
            int(tahun)
        except ValueError:
            messagebox.showerror("Error", "Tahun harus berupa angka.")
            return
        except KeyError:
             messagebox.showerror("Error", "Bulan tidak valid.")
             return

        for i in self.tree.get_children():
            self.tree.delete(i)

        conn = _connect_db()
        c = conn.cursor()

        total_debit_ns = 0
        total_kredit_ns = 0

        try:
            c.execute("SELECT kode_akun, nama_akun, saldo_normal FROM akun ORDER BY kode_akun ASC")
            semua_akun = c.fetchall()

            ada_data = False
            for kode_akun, nama_akun, saldo_normal in semua_akun:
                
                query_saldo = """
                    SELECT SUM(debit), SUM(kredit)
                    FROM jurnal_umum_detail
                    WHERE kode_akun = ?
                      AND strftime('%m', tanggal) = ?
                      AND strftime('%Y', tanggal) = ?
                      AND jenis_jurnal NOT IN ('PENYESUAIAN', 'PENUTUP') 
                """
                c.execute(query_saldo, (kode_akun, bulan_num, tahun))
                
                mutasi_debit, mutasi_kredit = c.fetchone()
                mutasi_debit = mutasi_debit if mutasi_debit is not None else 0
                mutasi_kredit = mutasi_kredit if mutasi_kredit is not None else 0
                
                net_balance = mutasi_debit - mutasi_kredit
                
                debit_saldo = 0
                kredit_saldo = 0

                if net_balance > 0:
                    debit_saldo = net_balance
                elif net_balance < 0:
                    kredit_saldo = abs(net_balance)

                if mutasi_debit > 0 or mutasi_kredit > 0:
                    ada_data = True
                    
                    self.tree.insert("", "end", values=(
                        kode_akun,
                        nama_akun,
                        _format_rupiah(debit_saldo) if debit_saldo > 0 else "",
                        _format_rupiah(kredit_saldo) if kredit_saldo > 0 else ""
                    ))

                    total_debit_ns += debit_saldo
                    total_kredit_ns += kredit_saldo
            
            if ada_data:
                self.tree.insert("", "end", values=(
                    "", 
                    "TOTAL NERACA SALDO", 
                    _format_rupiah(total_debit_ns), 
                    _format_rupiah(total_kredit_ns)
                ), tags=('total',))
                self.tree.tag_configure('total', font=('Helvetica', 10, 'bold'), background='#E0F7FA')
                
                if total_debit_ns != total_kredit_ns:
                    messagebox.showwarning("Peringatan", "Neraca Saldo TIDAK SEIMBANG! Mohon cek Jurnal Umum Anda.")
                else:
                    messagebox.showinfo("Sukses", "Neraca Saldo berhasil dimuat dan SEIMBANG.")

            else:
                messagebox.showinfo("Info", "Tidak ada data transaksi untuk periode ini.")


        except sqlite3.Error as e:
            messagebox.showerror("Error Database", f"Terjadi kesalahan saat memuat Neraca Saldo: {e}")
        finally:
            conn.close()