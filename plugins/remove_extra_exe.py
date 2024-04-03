from tkinter import messagebox
import os
from send2trash import send2trash

plugin_info = {
    "title": "Remove Extra C/C++ Executables",
    "description": "Remove extra C/C++ executables from the selected folder(s)",
    "type": ["DIRECTORY_BACKGROUND", "DIRECTORY"],
    "manu_name": "abd Utils",
}


def driver(folders, params):
    try:
        dict_of_files = {}
        allowed = ["cpp", "c"]
        for folder in folders:
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.split(".")[-1] in allowed and os.path.exists(os.path.join(root, file.split(".")[0] + ".exe")):
                        dict_of_files[os.path.join(root, file.split(".")[0] + ".exe")] = file.split(".")[0] + ".exe"
        if dict_of_files == {}:
            messagebox.showinfo("No files to remove", "No files to remove")
        elif messagebox.askyesno("Files to be removed", "\n".join(dict_of_files.values()) + "\n\nDo you want to continue?"):
            for file in dict_of_files.keys():
                print("Removing: ", file)
                send2trash(file)
    except Exception as e:
        messagebox.showerror("Error", str(e))