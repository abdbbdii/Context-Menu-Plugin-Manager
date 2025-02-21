from tkinter import messagebox
import os, shutil


def driver(items: list[str] = [], params: str = ""):
    for folder in items:
        for file in os.listdir(folder):
            print("Unpacking: ", file)
            shutil.move(os.path.join(folder, file), os.path.join(os.path.dirname(folder), file))


if __name__ == "__main__":
    for folder in os.listdir(r"C:\Users\ar69k\OneDrive - student.uet.edu.pk\Pictures\mama gallery\WhatsApp Images"):
        driver([r"C:\Users\ar69k\OneDrive - student.uet.edu.pk\Pictures\mama gallery\WhatsApp Images" + "\\" + folder])
