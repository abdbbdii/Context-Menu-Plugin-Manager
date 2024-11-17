from tkinter import messagebox
import os, shutil

plugin_info = {
    "title": "Unpack Files From Folder",
    "description": "Unpack all files in the selected folder(s) to the parent folder(s)",
    "type": ["DIRECTORY"],
    "menu_name": "abd Utils",
}


def driver(folders, params):
    count = 0
    for folder in folders:
        for file in os.listdir(folder):
            print("Unpacking: ", file)
            shutil.move(os.path.join(folder, file), os.path.join(os.path.dirname(folder), file))
            count += 1
    if count == 0:
        messagebox.showinfo("No file to unpack", "No file to unpack")
    # else:
    #     messagebox.showinfo("File(s) unpacked", str(count) + " file(s) unpacked.")

if __name__ == "__main__":
    for folder in os.listdir(r"C:\Users\ar69k\OneDrive - student.uet.edu.pk\Pictures\mama gallery\WhatsApp Images"):
        driver([r"C:\Users\ar69k\OneDrive - student.uet.edu.pk\Pictures\mama gallery\WhatsApp Images"+'\\'+folder], {})