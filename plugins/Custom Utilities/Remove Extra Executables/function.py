from tkinter import messagebox
import os
from send2trash import send2trash
from tkinter import ttk
import tkinter as tk


def driver(items: list[str] = [], params: str = ""):
    try:
        dict_of_files = {}
        allowed = ["cpp", "c"]
        for folder in items:
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.split(".")[-1] in allowed and os.path.exists(os.path.join(root, file.split(".")[0] + ".exe")):
                        dict_of_files[os.path.join(root, file.split(".")[0] + ".exe")] = file.split(".")[0] + ".exe"
        if dict_of_files == {}:
            messagebox.showinfo("No files to remove", "No files to remove")
        else:
            for file in filter_window(dict_of_files.keys()):
                send2trash(file)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def filter_window(folders):
    def close_window(status_code):
        global close_status
        close_status = status_code
        root.destroy()

    root = tk.Tk()
    root.title("Select Folders")
    root.protocol("WM_DELETE_WINDOW", lambda: close_window(1))
    root.bind("<Return>", lambda _: close_window(0))
    selected_folders = []

    def update_selection():
        selected_folders.clear()
        for folder, var in zip(folders, folder_vars):
            if var.get():
                selected_folders.append(folder)

    def select_all():
        for var in folder_vars:
            var.set(True)
        update_selection()

    def deselect_all():
        for var in folder_vars:
            var.set(False)
        update_selection()

    upper_frame = ttk.Frame(root)
    upper_frame.pack(fill="x")
    middle_frame = ttk.Frame(root)
    middle_frame.pack(fill="both", expand=True)
    bottom_frame = ttk.Frame(root)
    bottom_frame.pack(fill="x")

    ttk.Button(upper_frame, text="Select All", command=select_all).pack(side="left", padx=10, pady=10)
    ttk.Button(upper_frame, text="Deselect All", command=deselect_all).pack(side="left", pady=10)

    folder_vars = []
    for folder in folders:
        var = tk.BooleanVar(value=True)
        folder_vars.append(var)
        folder_name = folder.split("/")[-1]
        check_button = ttk.Checkbutton(middle_frame, text=folder_name, variable=var, command=update_selection)
        check_button.pack(anchor="w", padx=10)
    update_selection()

    ttk.Button(bottom_frame, text="Confirm", command=lambda: close_window(0)).pack(padx=10, pady=10, side="right")

    root.mainloop()
    if close_status == 0:
        return selected_folders
    else:
        return []
