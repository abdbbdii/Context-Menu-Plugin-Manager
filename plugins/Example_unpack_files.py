from tkinter import messagebox
import os, shutil

plugin_info = {
    "title": "Unpack Files From Folder",
    "description": "Unpack all files in the selected folder(s) to the parent folder(s)",
    "type": ["DIRECTORY"],
    "manu_name": "Plugin Manager",
}


def driver(folders, params):
    if not messagebox.askyesno("Unpack Files", "Do you want to unpack all files in the selected folder(s)?"):
        return
    count = 0
    for folder in folders:
        for file in os.listdir(folder):
            print("Unpacking: ", file)
            shutil.move(os.path.join(folder, file), os.path.join(os.path.dirname(folder), file))
            count += 1
    if count == 0:
        messagebox.showinfo("No file to unpack", "No file to unpack")
    else:
        messagebox.showinfo("File(s) unpacked", str(count) + " file(s) unpacked.")
