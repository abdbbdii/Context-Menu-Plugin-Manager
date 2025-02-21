from tkinter import messagebox, Tk, ttk, IntVar, BooleanVar
import tkinter as tk
import os
from send2trash import send2trash


def driver(items: list[str] = [], params: str = ""):
    try:
        level = selector_window()
        folders_to_remove = []
        count = 0
        for folder in items:
            for root, dirs, _ in os.walk(folder, topdown=False):
                for directory in dirs:
                    directory_path = os.path.join(root, directory)
                    try:
                        if not os.listdir(directory_path):
                            if directory_path.count(os.sep) - folder.count(os.sep) - 1 <= level:
                                folders_to_remove.append(directory_path)
                                count += 1
                    except PermissionError as e:
                        messagebox.askokcancel("Permission Error", str(e))
        if count == 0:
            messagebox.showinfo("No empty folder", "No empty folder to remove")
        else:
            for folder in filter_window(folders_to_remove):
                send2trash(folder)
    except Exception as e:
        messagebox.askokcancel("Error", str(e))


def selector_window():
    root = Tk()
    root.title("Select subfolder level")
    left = (root.winfo_screenwidth() - 200) // 2
    top = (root.winfo_screenheight() - 200) // 2
    root.geometry(f"300x100+{left}+{top}")
    root.resizable(False, False)
    root.bind("<Return>", lambda _: root.destroy())

    input_frame = ttk.Frame(root)
    input_frame.pack(fill="x")

    spinbox_var = IntVar(value=0)
    spinbox = ttk.Spinbox(input_frame, from_=0, to=float("inf"), textvariable=spinbox_var)
    spinbox.pack(padx=10, pady=10, fill="x", side="left", expand=True)

    check_var = BooleanVar(value=False)
    ttk.Checkbutton(input_frame, text="Select all subfolders", variable=check_var, command=lambda: spinbox.configure(state="disabled") if check_var.get() else spinbox.configure(state="normal")).pack(padx=10, pady=10, side="left")

    ttk.Button(root, text="Ok", command=root.destroy).pack(padx=10, pady=10)

    root.mainloop()
    return float("inf") if check_var.get() else spinbox_var.get()


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

    select_frame = ttk.Frame(root)
    select_frame.pack(fill="x")

    ttk.Button(select_frame, text="Select All", command=select_all).pack(side="left", padx=10, pady=10)
    ttk.Button(select_frame, text="Deselect All", command=deselect_all).pack(side="left", padx=10, pady=10)

    folder_vars = []
    for folder in folders:
        var = tk.BooleanVar(value=True)
        folder_vars.append(var)
        folder_name = folder.split("/")[-1]
        check_button = ttk.Checkbutton(root, text=folder_name, variable=var, command=update_selection)
        check_button.pack(anchor="w", padx=10)

    # Button to confirm selection
    confirm_button = ttk.Button(root, text="Confirm", command=lambda: close_window(0))
    confirm_button.pack(padx=10, pady=10)

    root.mainloop()
    if close_status == 0:
        return selected_folders
    else:
        return []
