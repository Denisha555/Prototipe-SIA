import tkinter as tk
from tkinter import ttk


class MenuStaffPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Menu Utama").grid(column=0, row=0, padx=10, pady=10)
        

        