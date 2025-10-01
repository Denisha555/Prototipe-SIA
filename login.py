import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

from function.show_frame import show_frame


class LoginPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Prototype SIA")

        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry(f"{width}x{height}")

        # Container utama untuk frame-frame
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Tampilkan login frame dulu
        login_frame = tk.Frame(self.container)
        self.frames["Login"] = login_frame
        login_frame.grid(row=0, column=0, sticky="nsew")

        login_frame.grid_columnconfigure(0, weight=1)
        login_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(login_frame, text="🔑 Login", font=("Helvetica", 20, "bold")).grid(row=0, column=0, columnspan=2)

        ttk.Label(login_frame, text="Username:").grid(row=1, column=0, pady=5, padx=5, sticky="e")
        self.entry_username = ttk.Entry(login_frame, width=25)
        self.entry_username.grid(row=1, column=1, pady=5, sticky="w")
        ttk.Label(login_frame, text="Password:").grid(row=2, column=0, pady=5, padx=5, sticky="e")
        self.entry_password = ttk.Entry(login_frame, show="*", width=25)
        self.entry_password.grid(row=2, column=1, pady=5, sticky="w")

        ttk.Button(login_frame, text="Login", command=self.login).grid(row=3, columnspan=2, pady=15)

        self.show_frame("Login")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        conn = sqlite3.connect('data_keuangan.db')
        c = conn.cursor()
        c.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
        result = c.fetchone()
    
        if result:
            role = result[0]
            if role == "staff":
                show_frame(self, "Menu Utama Staff")
            elif role == "manager":
                show_frame(self, "Menu Utama Manager")
            messagebox.showinfo("Sukses", f"Login berhasil sebagai {role}.")
        else:
            messagebox.showerror("Gagal", "Username atau password salah.")

        conn.close()


if __name__ == "__main__":
    app = LoginPage()
    app.mainloop()
