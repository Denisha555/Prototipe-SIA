import tkinter as tk
from tkinter import ttk

class MenuManagerPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # ===============================
        # WRAPPER UNTUK SCROLL
        # ===============================
        canvas = tk.Canvas(self)
        canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")

        canvas.configure(yscrollcommand=scrollbar.set)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # FRAME isi yang bisa discroll
        content_frame = ttk.Frame(canvas)
        window = canvas.create_window((0, 0), window=content_frame, anchor="nw", tags="content_frame_window")

        # Auto-update scroll region
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        content_frame.bind("<Configure>", on_frame_configure)

        # Supaya lebar konten selalu ikut lebar canvas
        def on_canvas_configure(event):
            canvas.itemconfig(window, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)

        # Untuk memenuhi lebar content_frame di canvas
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # ===============================
        # GAYA (STYLE)
        # ===============================
        style = ttk.Style()
        style.configure("Menu.TButton",
                        font=("Helvetica", 13, "bold"),
                        padding=15,
                        background="#007BFF",
                        foreground="black")
        style.configure("Title.TLabel", font=("Helvetica", 20, "bold"))
        style.configure("Danger.TButton",
                        font=("Helvetica", 12, "bold"),
                        padding=10,
                        background="#DC3545",
                        foreground="black")

        # ===============================
        # FRAME UTAMA
        # ===============================
        ttk.Label(content_frame, text="🏛️ Menu Utama Manager", style="Title.TLabel", anchor="center").grid(
            column=0, row=0, columnspan=4, padx=10, pady=20, sticky="ew" # columnspan=4 untuk menengahkan
        )
        
        for i in range(4):
            content_frame.grid_columnconfigure(i, weight=1)

        # ===============================
        # FRAME 1: MANAJEMEN DATA
        # ===============================
        data_frame = ttk.LabelFrame(content_frame, text="Manajemen Data", padding=15)
        data_frame.grid(column=0, row=1, padx=5, pady=10, sticky="nsew")
        data_frame.grid_columnconfigure(0, weight=1)

        ttk.Button(data_frame, text="⚙️ Kelola Jasa", style="Menu.TButton",
                   command=lambda: controller.show_frame("Input Jasa Manager")).grid(
            column=0, row=0, padx=10, pady=10, sticky="ew")
        ttk.Button(data_frame, text="🛒 Kelola Penjualan", style="Menu.TButton",
                   command=lambda: controller.show_frame("Input Edit Penjualan")).grid(
            column=0, row=1, padx=10, pady=10, sticky="ew")
        ttk.Button(data_frame, text="💸 Kelola Pengeluaran", style="Menu.TButton",
                   command=lambda: controller.show_frame("Input Edit Kas Keluar")).grid(
            column=0, row=2, padx=10, pady=10, sticky="ew")
        ttk.Button(data_frame, text="📝 Penyesuaian", style="Menu.TButton",
                   command=lambda: controller.show_frame("Penyesuaian Manager")).grid(
            column=0, row=3, padx=10, pady=10, sticky="ew")

        # ===============================
        # FRAME 2: SIKLUS AKUNTANSI
        # ===============================
        siklus_frame = ttk.LabelFrame(content_frame, text="Siklus Akuntansi", padding=15)
        siklus_frame.grid(column=1, row=1, padx=5, pady=10, sticky="nsew")
        siklus_frame.grid_columnconfigure(0, weight=1)

        ttk.Button(siklus_frame, text="📘 Jurnal Umum", style="Menu.TButton",
                   command=lambda: controller.show_frame("Jurnal Umum")).grid(
            column=0, row=0, padx=10, pady=10, sticky="ew")
        ttk.Button(siklus_frame, text="📚 Buku Besar", style="Menu.TButton",
                   command=lambda: controller.show_frame("Buku Besar")).grid(
            column=0, row=1, padx=10, pady=10, sticky="ew")
        ttk.Button(siklus_frame, text="⚖️ Neraca Saldo", style="Menu.TButton",
                   command=lambda: controller.show_frame("Neraca Saldo")).grid(
            column=0, row=2, padx=10, pady=10, sticky="ew")
        ttk.Button(siklus_frame, text="🧮 Jurnal Penyesuaian", style="Menu.TButton",
                   command=lambda: controller.show_frame("Jurnal Penyesuaian")).grid(
            column=0, row=3, padx=10, pady=10, sticky="ew")
        ttk.Button(siklus_frame, text="📰 Neraca Lajur", style="Menu.TButton",
                   command=lambda: controller.show_frame("Worksheet")).grid(
            column=0, row=4, padx=10, pady=10, sticky="ew")

        # ===============================
        # FRAME 3: LAPORAN & PENUTUPAN
        # ===============================
        laporan_frame = ttk.LabelFrame(content_frame, text="Laporan & Penutupan", padding=15)
        laporan_frame.grid(column=2, row=1, padx=5, pady=10, sticky="nsew") # sticky="nsew" penting
        laporan_frame.grid_columnconfigure(0, weight=1)

        ttk.Button(laporan_frame, text="💰 Laporan Laba Rugi", style="Menu.TButton",
                   command=lambda: controller.show_frame("Laba Rugi")).grid(
            column=0, row=0, padx=10, pady=10, sticky="ew")
        ttk.Button(laporan_frame, text="💵 Laporan Perubahan Modal", style="Menu.TButton",
                   command=lambda: controller.show_frame("Laporan Perubahan Modal")).grid(
            column=0, row=1, padx=10, pady=10, sticky="ew")
        ttk.Button(laporan_frame, text="🏦 Neraca", style="Menu.TButton",
                   command=lambda: controller.show_frame("Neraca")).grid(
            column=0, row=2, padx=10, pady=10, sticky="ew")
        ttk.Button(laporan_frame, text="📖 Laporan Arus Kas", style="Menu.TButton",
                   command=lambda: controller.show_frame("Laporan Arus Kas")).grid(
            column=0, row=3, padx=10, pady=10, sticky="ew")
        ttk.Button(laporan_frame, text="🔄 Jurnal Penutup", style="Menu.TButton",
                   command=lambda: controller.show_frame("Jurnal Penutup")).grid(
            column=0, row=4, padx=10, pady=10, sticky="ew")
        ttk.Button(laporan_frame, text="🔐 Neraca Saldo Setelah Penutupan", style="Menu.TButton",
                   command=lambda: controller.show_frame("Neraca Saldo Setelah Penutupan")).grid(
            column=0, row=5, padx=10, pady=10, sticky="ew")
        
        # ===============================
        # FRAME 4: ANALISIS GRAFIK (kolom 3)
        # ===============================
        grafik_frame = ttk.LabelFrame(content_frame, text="Analisis Grafik", padding=15)
        grafik_frame.grid(column=3, row=1, padx=5, pady=10, sticky="nsew")
        grafik_frame.grid_columnconfigure(0, weight=1)

        ttk.Button(grafik_frame, text="📊 Grafik Pendapatan", style="Menu.TButton",
                   command=lambda: controller.show_frame("Grafik Pendapatan")).grid(
            column=0, row=0, padx=10, pady=10, sticky="ew")

        ttk.Button(grafik_frame, text="📉 Grafik Pengeluaran", style="Menu.TButton",
                   command=lambda: controller.show_frame("Jurnal Penutup")).grid(
            column=0, row=1, padx=10, pady=10, sticky="ew")

        ttk.Button(grafik_frame, text="⚗️ Grafik Komposisi Aset", style="Menu.TButton",
                   command=lambda: controller.show_frame("Jurnal Penutup")).grid(
            column=0, row=2, padx=10, pady=10, sticky="ew")
        
        ttk.Button(grafik_frame, text="📈 Grafik Pendapatan & Beban", style="Menu.TButton",
                   command=lambda: controller.show_frame("Jurnal Penutup")).grid(
            column=0, row=3, padx=10, pady=10, sticky="ew")
        
        ttk.Button(grafik_frame, text="📊 Grafik Perubahan Modal", style="Menu.TButton",
                   command=lambda: controller.show_frame("Jurnal Penutup")).grid(
            column=0, row=4, padx=10, pady=10, sticky="ew")

        # ===============================
        # TOMBOL KEMBALI KE LOGIN
        # ===============================
        ttk.Button(content_frame, text="◀️ Kembali ke Login",
                   command=lambda: controller.show_frame("Login"), style="Danger.TButton").grid(
            column=0, row=2, columnspan=4, padx=20, pady=30, sticky="n")

        # ===============================
        # FOOTER SPACER
        # ===============================
        ttk.Label(content_frame, text="").grid(column=0, row=3, columnspan=4, pady=40)

        # ===============================
        # SCROLL PAKAI MOUSE WHEEL
        # ===============================
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        content_frame.bind("<MouseWheel>", _on_mousewheel)
        
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
            
        canvas.tag_bind("content_frame_window", '<Enter>', _bind_mousewheel)
        canvas.tag_bind("content_frame_window", '<Leave>', _unbind_mousewheel)
        
        for widget in [content_frame, data_frame, siklus_frame, laporan_frame, grafik_frame]:
             widget.bind("<Enter>", _bind_mousewheel)
             widget.bind("<Leave>", _unbind_mousewheel)