import io
import sqlite3
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk, messagebox, filedialog


class ProdukPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.current_produk_id = None  # untuk melacak produk yang sedang diedit

        # Atur layout grid utama
        self.grid_columnconfigure(0, weight=1, uniform="col")
        self.grid_columnconfigure(1, weight=2, uniform="col")
        self.grid_rowconfigure(1, weight=1)

        # === TITLE ===
        ttk.Label(self, text="📦 Manajemen Produk", font=("Helvetica", 18, "bold")).grid(
            row=0, column=0, columnspan=2, pady=15
        )

        # === FRAME KIRI (Input) ===
        input_frame = ttk.LabelFrame(self, text="Input / Edit Produk", padding=15)
        input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        ttk.Label(input_frame, text="Nama Produk:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_nama = ttk.Entry(input_frame, width=30)
        self.entry_nama.grid(row=0, column=1, pady=5)

        ttk.Label(input_frame, text="Harga:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_harga = ttk.Entry(input_frame, width=30)
        self.entry_harga.grid(row=1, column=1, pady=5)

        ttk.Label(input_frame, text="Stok:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_stok = ttk.Entry(input_frame, width=30)
        self.entry_stok.grid(row=2, column=1, pady=5)

        ttk.Label(input_frame, text="Gambar:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_gambar = ttk.Entry(input_frame, width=30)
        self.entry_gambar.grid(row=3, column=1, pady=5)
        ttk.Button(input_frame, text="Pilih Gambar", command=self.pilih_gambar).grid(row=3, column=2, padx=5)

        ttk.Button(input_frame, text="Simpan", command=self.simpan_produk).grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(input_frame, text="Hapus", command=self.hapus_produk).grid(row=4, column=1, columnspan=2, pady=5)

        ttk.Button(input_frame, text="Kembali ke menu utama", width=30, command=lambda: controller.show_frame("Menu Utama Staff")).grid(row=5, column=0, columnspan=3, pady=10)

       # === FRAME KANAN (Tabel Data) ===
        table_frame = ttk.LabelFrame(self, text="Daftar Produk", padding=10)
        table_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")

        self.tree = ttk.Treeview(
            table_frame,
            columns=("nama", "harga", "stok"),
            show="tree headings"  # supaya kolom gambar muncul
        )
        self.tree.heading("#0", text="Gambar")
        self.tree.heading("nama", text="Nama Produk")
        self.tree.heading("harga", text="Harga")
        self.tree.heading("stok", text="Stok")

        self.tree.column("#0", width=60, anchor="center")
        self.tree.column("nama", width=150, anchor="center")
        self.tree.column("harga", width=100, anchor="center")
        self.tree.column("stok", width=60, anchor="center")

        self.tree.bind("<Double-1>", self.on_tree_double_click)
        self.tree.pack(fill="both", expand=True)

        # Load data saat pertama kali
        self.load_data()

    # === PILIH GAMBAR ===
    def pilih_gambar(self):
        file_path = filedialog.askopenfilename(
            title="Pilih Gambar",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if file_path:
            self.entry_gambar.delete(0, tk.END)
            self.entry_gambar.insert(0, file_path)

    # === SIMPAN PRODUK (Tambah / Edit) ===
    def simpan_produk(self):
        nama = self.entry_nama.get()
        harga = self.entry_harga.get()
        stok = self.entry_stok.get()
        gambar_path = self.entry_gambar.get()

        if not nama or not harga or not stok or not gambar_path:
            messagebox.showerror("Error", "Semua field harus diisi!")
            return

        try:
            harga = float(harga)
            stok = int(stok)
        except ValueError:
            messagebox.showerror("Error", "Harga harus angka, stok harus bilangan bulat!")
            return

        try:
            with open(gambar_path, "rb") as f:
                gambar_blob = f.read()
        except Exception:
            messagebox.showerror("Error", "Gagal membaca file gambar.")
            return

        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()

        if self.current_produk_id:
            # UPDATE data
            c.execute("""
                UPDATE produk 
                SET nama_produk=?, harga=?, stok=?, gambar=? 
                WHERE rowid=?
            """, (nama, harga, stok, gambar_blob, self.current_produk_id))
            messagebox.showinfo("Sukses", "Produk berhasil diperbarui.")
        else:
            # INSERT data baru
            c.execute("""
                INSERT INTO produk (nama_produk, harga, stok, gambar) 
                VALUES (?, ?, ?, ?)
            """, (nama, harga, stok, gambar_blob))
            messagebox.showinfo("Sukses", "Produk berhasil ditambahkan.")

        conn.commit()
        conn.close()
        self.load_data()
        self.reset_form()

    # === MUAT DATA KE TABEL ===
    def load_data(self):
        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()
        c.execute("SELECT rowid, nama_produk, harga, stok, gambar FROM produk")
        rows = c.fetchall()
        conn.close()

        # Bersihkan isi tabel dulu
        for i in self.tree.get_children():
            self.tree.delete(i)

        # simpan cache gambar supaya tidak hilang dari memori
        self.image_cache = {}

        for row in rows:
            produk_id = row[0]
            nama, harga, stok, gambar_blob = row[1:]

            if gambar_blob:
                try:
                    image = Image.open(io.BytesIO(gambar_blob))
                    image.thumbnail((50, 50))
                    photo = ImageTk.PhotoImage(image)
                    # simpan referensi gambar biar nggak hilang
                    self.image_cache[produk_id] = photo  
                    self.tree.insert("", "end", iid=produk_id, image=photo, values=(nama, harga, stok))
                except Exception as e:
                    print(f"Gagal memuat gambar untuk {nama}: {e}")
                    self.tree.insert("", "end", iid=produk_id, values=(nama, harga, stok))
            else:
                self.tree.insert("", "end", iid=produk_id, values=(nama, harga, stok))

    # === KETIKA DOUBLE CLICK TABEL ===
    def on_tree_double_click(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        produk_id = selected_item[0]

        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()
        c.execute("SELECT nama_produk, harga, stok FROM produk WHERE rowid=?", (produk_id,))
        produk = c.fetchone()
        conn.close()

        if produk:
            self.current_produk_id = produk_id
            self.entry_nama.delete(0, tk.END)
            self.entry_nama.insert(0, produk[0])

            self.entry_harga.delete(0, tk.END)
            self.entry_harga.insert(0, produk[1])

            self.entry_stok.delete(0, tk.END)
            self.entry_stok.insert(0, produk[2])

            self.entry_gambar.delete(0, tk.END)
            self.entry_gambar.insert(0, f"gambar {produk[0]}")

    # === HAPUS PRODUK ===
    def hapus_produk(self):
        if not self.current_produk_id:
            messagebox.showerror("Error", "Pilih produk terlebih dahulu!")
            return

        confirm = messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus produk ini?")
        if confirm:
            conn = sqlite3.connect("data_keuangan.db")
            c = conn.cursor()
            c.execute("DELETE FROM produk WHERE rowid=?", (self.current_produk_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sukses", "Produk berhasil dihapus.")
            self.load_data()
            self.reset_form()

    # === RESET FORM ===
    def reset_form(self):
        self.current_produk_id = None
        self.entry_nama.delete(0, tk.END)
        self.entry_harga.delete(0, tk.END)
        self.entry_stok.delete(0, tk.END)
        self.entry_gambar.delete(0, tk.END)
