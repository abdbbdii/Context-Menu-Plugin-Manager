from tkinter import messagebox

plugin_info = {
    "title": "Test Plugin",
    "description": "This is a test plugin",
    "type": ["DIRECTORY", "DIRECTORY_BACKGROUND"],
    "menu_name": "abd Utils",
}

def driver(folders, params):
    # Your custom functionality goes here
    messagebox.showinfo("Test Plugin", "This is a test plugin")