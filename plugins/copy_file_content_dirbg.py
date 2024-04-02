import os, pyperclip

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
    pyperclip.copy("\n\n".join([f"{key}\n```\n{value.strip()}\n```" for key, value in content.items()]))


if __name__ == "__main__":
    driver(["."], {})
