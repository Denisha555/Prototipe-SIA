import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

from initialize_db import initialize_db


class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        initialize_db(self)

        self.title = "Login Page"
        self.controller = controller

        ttk.Label(self, text="🔑 Login", font=("Helvetica", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=20)

        # Username
        ttk.Label(self, text="Username:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.entry_username = ttk.Entry(self, width=25)
        self.entry_username.grid(row=1, column=1, pady=5, sticky="w")

        # Password
        ttk.Label(self, text="Password:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.entry_password = ttk.Entry(self, show="*", width=25)
        self.entry_password.grid(row=2, column=1, pady=5, sticky="w")

        # Tombol
        ttk.Button(self, text="Login", command=self.login).grid(row=3, column=0, columnspan=2, pady=15)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        if not username or not password:
            messagebox.showerror("Error", "Isi semua field!")
            return

        conn = sqlite3.connect("data_keuangan.db")
        cursor = conn.cursor()

        cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
        result = cursor.fetchone()
        conn.close()

        if result:
            role = result[0]
            messagebox.showinfo("Sukses", f"Login berhasil sebagai {role}")
            self.controller.current_role = role
            self.controller.show_frame("Menu")  # masuk ke menu utama
        else:
            messagebox.showerror("Error", "Username atau password salah!")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Login Page")
    login_page = LoginPage(root, None)
    login_page.pack(fill="both", expand=True)
    root.mainloop()