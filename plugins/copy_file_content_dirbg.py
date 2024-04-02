import os, pyperclip
from tkinter import ttk
import tkinter as tk

plugin_info = {
    "title": "Copy File Content",
    "description": "Copy the content of all files in the current directory to the clipboard.",
    "type": ["DIRECTORY_BACKGROUND"],
    "manu_name": "abd Utils",
}


def driver(folders, params):
    content = {}
    for folder in folders:
        for file in os.listdir(folder):
            if os.path.isfile(os.path.join(folder, file)):
                with open(os.path.join(folder, file), "r") as f:
                    content[file] = f.read()
    pyperclip.copy("\n\n".join([f"{key}\n```\n{content[key].strip()}\n```" for key in filter_window(content.keys())]))


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


if __name__ == "__main__":
    driver(["."], {})
