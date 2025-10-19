import io
import sqlite3
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk, messagebox, filedialog

def format_rupiah(nominal):
    formatted = f"{int(nominal):,.0f}".replace(",", "#").replace(".", ",").replace("#", ".")
    return f"{formatted}"

class JasaPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.current_jasa_id = None
        self.image_cache = {}  # simpan gambar supaya tidak hilang dari memori

        # === Layout ===
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        ttk.Label(self, text="⚙️ Manajemen Jasa", font=("Helvetica", 18, "bold")).grid(
            row=0, column=0, columnspan=2, pady=15
        )

        # === FRAME INPUT ===
        input_frame = ttk.LabelFrame(self, text="Input / Edit Jasa", padding=15)
        input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        ttk.Label(input_frame, text="Nama Jasa:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_nama = ttk.Entry(input_frame, width=30)
        self.entry_nama.grid(row=0, column=1, pady=5)

        ttk.Label(input_frame, text="Deskripsi:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_deskripsi = ttk.Entry(input_frame, width=30)
        self.entry_deskripsi.grid(row=1, column=1, pady=5)

        ttk.Label(input_frame, text="Harga (Rp):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_harga = ttk.Entry(input_frame, width=30)
        self.entry_harga.grid(row=2, column=1, pady=5)

        ttk.Label(input_frame, text="Gambar:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_gambar = ttk.Entry(input_frame, width=30)
        self.entry_gambar.grid(row=3, column=1, pady=5)
        ttk.Button(input_frame, text="Pilih Gambar", command=self.pilih_gambar).grid(row=3, column=2, pady=5)

        ttk.Button(input_frame, text="Simpan", command=self.simpan_jasa).grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(input_frame, text="Hapus", command=self.hapus_jasa).grid(row=4, column=1, columnspan=2, pady=5)
        ttk.Button(input_frame, text="Kembali ke Menu Utama", width=30,
                   command=lambda: controller.show_frame("Menu Utama Staff")).grid(row=5, column=0, columnspan=3, pady=10)

        # === FRAME TABEL ===
        table_frame = ttk.LabelFrame(self, text="Daftar Jasa", padding=10)
        table_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")

        self.tree = ttk.Treeview(
            table_frame,
            columns=("nama", "deskripsi", "harga"),
            show="tree headings"
        )
        self.tree.heading("#0", text="Gambar")
        self.tree.heading("nama", text="Nama Jasa")
        self.tree.heading("deskripsi", text="Deskripsi")
        self.tree.heading("harga", text="Harga (Rp)")

        self.tree.column("#0", width=100, anchor="center")
        self.tree.column("nama", width=180, anchor="center")
        self.tree.column("deskripsi", width=180, anchor="center")
        self.tree.column("harga", width=100, anchor="center")

        self.tree.bind("<Double-1>", self.on_tree_double_click)
        self.tree.pack(fill="both", expand=True)

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

    # === SIMPAN JASA ===
    def simpan_jasa(self):
        nama = self.entry_nama.get().strip()
        harga = self.entry_harga.get().strip()
        deskripsi = self.entry_deskripsi.get().strip()
        gambar_path = self.entry_gambar.get().strip()

        if not nama or not harga or not gambar_path:
            messagebox.showerror("Error", "Nama jasa, harga, dan gambar harus diisi!")
            return

        try:
            cleaned_harga = ''.join(filter(str.isdigit, harga))
            harga = int(cleaned_harga)
            if harga < 0:
                messagebox.showerror("Error", "Harga tidak boleh negatif.")
                return
        except ValueError:
            messagebox.showerror("Error", "Harga harus berupa angka.")
            return

        try:
            with open(gambar_path, "rb") as f:
                gambar_blob = f.read()
        except Exception:
            messagebox.showerror("Error", "Gagal membaca file gambar.")
            return

        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()

        if self.current_jasa_id:
            c.execute("""
                UPDATE jasa 
                SET nama_jasa=?, harga=?, gambar=?, detail_jasa=? 
                WHERE rowid=?
            """, (nama, harga, gambar_blob, deskripsi,  self.current_jasa_id))
            messagebox.showinfo("Sukses", "Jasa berhasil diperbarui.")
        else:
            c.execute("""
                INSERT INTO jasa (nama_jasa, harga, gambar, detail_jasa)
                VALUES (?, ?, ?, ?)
            """, (nama, harga, gambar_blob, deskripsi))
            messagebox.showinfo("Sukses", "Jasa berhasil ditambahkan.")

        conn.commit()
        conn.close()

        self.load_data()
        self.reset_form()

    # === LOAD DATA KE TABEL ===
    def load_data(self):
        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()
        c.execute("SELECT rowid, nama_jasa, harga, gambar, detail_jasa FROM jasa")
        rows = c.fetchall()
        conn.close()

        # Hapus data lama
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.image_cache.clear()

        for row in rows:
            jasa_id, nama, harga, gambar_blob, deskripsi = row
            img = None
            if gambar_blob:
                try:
                    image = Image.open(io.BytesIO(gambar_blob))
                    image.thumbnail((60, 60))
                    img = ImageTk.PhotoImage(image)
                    self.image_cache[jasa_id] = img
                except Exception as e:
                    print(f"Gagal load gambar {nama}: {e}")

            self.tree.insert("", "end", iid=jasa_id, image=img, values=(nama, deskripsi, f"{format_rupiah(harga)}"))

    # === DOUBLE CLICK ===
    def on_tree_double_click(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        jasa_id = selected[0]
        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()
        c.execute("SELECT nama_jasa, harga, gambar, detail_jasa FROM jasa WHERE rowid=?", (jasa_id,))
        jasa = c.fetchone()
        conn.close()

        if jasa:
            self.current_jasa_id = jasa_id
            self.entry_nama.delete(0, tk.END)
            self.entry_nama.insert(0, jasa[0])

            self.entry_harga.delete(0, tk.END)
            self.entry_harga.insert(0, jasa[1])

            self.entry_deskripsi.delete(0, tk.END)
            self.entry_deskripsi.insert(0, jasa[3])

            # Simpan gambar ke file temporer agar bisa dilihat di entry
            temp_path = f"temp_{jasa_id}.png"
            with open(temp_path, "wb") as f:
                f.write(jasa[2])
            self.entry_gambar.delete(0, tk.END)
            self.entry_gambar.insert(0, temp_path)

    # === HAPUS JASA ===
    def hapus_jasa(self):
        if not self.current_jasa_id:
            messagebox.showerror("Error", "Pilih jasa yang ingin dihapus!")
            return

        confirm = messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus jasa ini?")
        if not confirm:
            return

        conn = sqlite3.connect("data_keuangan.db")
        c = conn.cursor()
        c.execute("DELETE FROM jasa WHERE rowid=?", (self.current_jasa_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Sukses", "Jasa berhasil dihapus.")
        self.load_data()
        self.reset_form()

    def reset_form(self):
        self.current_jasa_id = None
        self.entry_nama.delete(0, tk.END)
        self.entry_harga.delete(0, tk.END)
        self.entry_gambar.delete(0, tk.END)
        self.entry_deskripsi.delete(0, tk.END)
