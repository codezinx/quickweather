import tkinter as tk
from tkinter import ttk

class Something:
    def __init__(self):
        root = tk.Tk()
        var = tk.StringVar(value="asfsafadsfs")
        ttk.Label(root, textvariable=var).pack()

Something()
tk.mainloop()