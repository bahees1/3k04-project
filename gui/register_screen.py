import tkinter as tk
from tkinter import messagebox
from gui.login_screen import register_user  


# -----------------------------------------------------------------------------
# main class for the register screen frame
# -----------------------------------------------------------------------------
class RegisterFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Center container
        container = tk.Frame(self)
        container.grid(row=0, column=0, sticky="nsew")

        tk.Label(
            container,
            text="Register New User",
            font=("Arial", 18, "bold"),
        ).pack(pady=30)

        tk.Label(container, text="Username:").pack()
        self.username_entry = tk.Entry(container, bg="#f5f5f5", fg="black", width=25)
        self.username_entry.pack(pady=5)

        tk.Label(container, text="Password:").pack()
        self.password_entry = tk.Entry(container, show="*", bg="#f5f5f5", fg="black", width=25)
        self.password_entry.pack(pady=5)

        tk.Button(container, text="Register", command=self.register, width=15, bg="#f5f5f5").pack(pady=10)
        tk.Button(container, text="Back", command=self.go_back, width=15, bg="#f5f5f5").pack()

    # -----------------------------------------------------------------------------
    # Helper functions - for registering a new user and going back to the home screen
    # -----------------------------------------------------------------------------
    def go_back(self):
        self.controller.show_frame("Login")  # take user back to the login home screen

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        success, message = register_user(
            self.controller.data["users"], username, password, self.controller.data_path  # attempt to register user
        )

        if success:
            messagebox.showinfo("Success", message)  # if register successful, then user is taken to login page
            self.controller.show_frame("Login")
        else:
            messagebox.showerror("Error", message)
