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
    res = filter_window(content.keys())
    print(res)
    if res == {}:
        return
    backticks = "```" if res["wrap_in_backtick"] else ""
    pyperclip.copy("\n\n".join([f"{file_name+'\n'+backticks}{file_name.rsplit('.')[-1] if res['enable_file_extension'] else ''}\n{content[file_name].strip()+'\n'+backticks}" for file_name in res["selected_folders"]]))


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

    enable_file_extension_check_var = tk.BooleanVar(value=True)
    wrap_in_backtick_check_var = tk.BooleanVar(value=True)

    ttk.Checkbutton(bottom_frame, text="Enable File Extension", variable=enable_file_extension_check_var).pack(padx=10, pady=10, side="left")
    ttk.Checkbutton(bottom_frame, text="Wrap in Backtick", variable=wrap_in_backtick_check_var).pack(padx=10, pady=10, side="left")
    ttk.Button(bottom_frame, text="Confirm", command=lambda: close_window(0)).pack(padx=10, pady=10, side="right")

    root.mainloop()
    if close_status == 0:
        return {
            "selected_folders": selected_folders,
            "enable_file_extension": enable_file_extension_check_var.get(),
            "wrap_in_backtick": wrap_in_backtick_check_var.get(),
        }
    else:
        return {}


if __name__ == "__main__":
    driver(["."], {})
