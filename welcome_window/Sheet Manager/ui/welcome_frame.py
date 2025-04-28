import tkinter as tk

class WelcomeFrame(tk.Frame):
    """UI Frame for the Welcome module."""
    def __init__(self, parent, on_start=None):
        super().__init__(parent, bg="white", bd=0, highlightthickness=0)
        self.on_start = on_start
        self._create_widgets()

    def _create_widgets(self):
        header = tk.Frame(self, bg="#1976d2")
        header.pack(fill=tk.X)
        title = tk.Label(header, text="Sheets Manager", font=("Roboto", 20, "bold"), fg="white", bg="#1976d2", pady=18)
        title.pack()
        main = tk.Frame(self, bg="white", bd=0, highlightthickness=0)
        main.pack(padx=30, pady=30, fill=tk.BOTH, expand=True)
        welcome = tk.Label(main, text="Welcome!", font=("Roboto", 16, "bold"), bg="white")
        welcome.pack(anchor="w", pady=(0, 8))
        desc = tk.Label(main, text="This is the starting point for the Sheets Manager module. Use this interface to manage and interact with your Google Sheets data as part of the suite.", wraplength=400, font=("Roboto", 11), bg="white", justify="left")
        desc.pack(anchor="w", pady=(0, 18))
        start_btn = tk.Button(main, text="Get Started", bg="#1976d2", fg="white", font=("Roboto", 11, "bold"), relief=tk.FLAT, padx=20, pady=8, command=self._on_start)
        start_btn.pack(anchor="w")

    def _on_start(self):
        if self.on_start:
            self.on_start()
