import tkinter as tk
import tkinter.messagebox as messagebox

class ConnectionFrame(tk.Frame):
    """UI Frame for the Connection module."""
    def __init__(self, parent, on_connect=None):
        super().__init__(parent, bg="white", bd=0, highlightthickness=0)
        self.on_connect = on_connect
        self._create_widgets()

    def _create_widgets(self):
        header = tk.Frame(self, bg="#388e3c")
        header.pack(fill=tk.X)
        title = tk.Label(header, text="Google Sheets Connection", font=("Roboto", 18, "bold"), fg="white", bg="#388e3c", pady=14)
        title.pack()
        main = tk.Frame(self, bg="white", bd=0, highlightthickness=0)
        main.pack(padx=30, pady=30, fill=tk.BOTH, expand=True)
        desc = tk.Label(main, text="Set up your connection to Google Sheets. Enter your credentials or test the connection.", wraplength=400, font=("Roboto", 11), bg="white", justify="left")
        desc.pack(anchor="w", pady=(0, 18))
        connect_btn = tk.Button(main, text="Test Connection", bg="#388e3c", fg="white", font=("Roboto", 11, "bold"), relief=tk.FLAT, padx=20, pady=8, command=self._on_connect)
        connect_btn.pack(anchor="w")

    def _on_connect(self):
        if self.on_connect:
            self.on_connect()
        else:
            messagebox.showinfo("Connection", "Connection test logic will go here.")
