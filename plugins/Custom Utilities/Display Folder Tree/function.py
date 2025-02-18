from pathlib import Path
import os
from tkinter import messagebox


def driver(folders, params):
    try:
        # Get the path of the current directory
        skip_folders = [".git", "__pycache__", "env", ".vscode"]
        print("Skip folders: ", skip_folders)
        if more_skip_folders := input("Enter more folders to skip separated by comma: "):
            skip_folders.extend(more_skip_folders.split(","))

        paths = DisplayablePath.make_tree(Path(folders[0]), criteria=lambda path: True if path.name not in skip_folders else False)
        for path in paths:
            print(path.displayable())
        os.system("pause")
    except Exception as e:
        messagebox.showerror("Error", str(e))


class DisplayablePath(object):
    display_filename_prefix_middle = "├─"
    display_filename_prefix_last = "└─"
    display_parent_prefix_middle = "   "
    display_parent_prefix_last = "│  "

    def __init__(self, path, parent_path, is_last):
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + "/"
        return self.path.name

    @classmethod
    def make_tree(cls, root, parent=None, is_last=False, criteria=None):
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(list(path for path in root.iterdir() if criteria(path)), key=lambda s: str(s).lower())
        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir():
                yield from cls.make_tree(path, parent=displayable_root, is_last=is_last, criteria=criteria)
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, path):
        return True

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + "/"
        return self.path.name

    def displayable(self):
        if self.parent is None:
            return self.displayname

        _filename_prefix = self.display_filename_prefix_last if self.is_last else self.display_filename_prefix_middle

        parts = ["{!s} {!s}".format(_filename_prefix, self.displayname)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(self.display_parent_prefix_middle if parent.is_last else self.display_parent_prefix_last)
            parent = parent.parent

        return "".join(reversed(parts))


# # With a criteria (skip hidden files)
# def is_not_hidden(path):
#     return not path.name.startswith(".")

# paths = DisplayablePath.make_tree(Path('whatsappBotApp'), criteria=is_not_hidden)
# for path in paths:
#     print(path.displayable())
