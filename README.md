# Context Menu Plugin Manager

![alt text](<assets/mockup (2).png>)

This project manages context menu plugins to extend functionality in various directories. It allows dynamic addition and removal of context menu items using Python scripts.

## Usage
1. Place plugin scripts in the `plugins` directory.
2. Run `main.py` to manage and load plugins.

## Features
- **Plugin Development:** Easily create plugins with metadata and functionality.
- **Dynamic Menu Modification:** Add or remove context menu items on the fly.
- **Extensible:** Customize and extend functionality by creating new plugins.

---

## Installation
First make sure you have Python 3.12.2 or above installed. If not, you can download it from [here](https://www.python.org/downloads/).
1. Clone the repository:
  ```
  git clone https://github.com/abdbbdii/context-menu-plugin-manager.git
  ```

2. Go inside the repository:
  ```
  cd context-menu-plugin-manager
  ```

3. Install the requirements
  ```
  pip3 install -r requirements.txt
  ```

4. Run the program
  ```
  python main.py
  ```

---

## Creating a Plugin

### **Create Python Script**:
- Create a new Python script in the `plugins` directory.
- The script should contain the following structure:

```python
plugin_info = {
    "title": str,
    "description": str,
    "menu_name": str,
    "type": ["FILES", "DIRECTORY", "DIRECTORY_BACKGROUND", "DRIVE"],
}

def driver(folders, params):
    ...
```

### **`plugin_info` variable**:
Define a variable named `plugin_info` containing the following keys.
  - `title` is the name of the script that is displayed as an item in context menu.
  - `description` (optional) is the description of the script.
  - `menu_name` is the name of the menu item that will be displayed in the context menu.
  - `type` is the type of the plugin. It is the list of one or more of `DIRECTORY`, `DIRECTORY_BACKGROUND`, `DRIVE`, `FILES`. See the table below for more information.

### **`type` values**:
| Type                   | Description                                     |
| ---------------------- | ----------------------------------------------- |
| `DIRECTORY`            | For opening on a directory.                     |
| `DIRECTORY_BACKGROUND` | For opening on the background of the directory. |
| `DRIVE`                | For opening on the drives like USB drive.       |
| `FILES`                | For opening on a file.                          |

### **`driver` function**:
Implement the `driver` function and pass two parameters:
  - `folders` (selected directories)
  - `params` (additional parameters).

---

### **Run the Project**:
  - Run `main.py` to load and manage plugins.
  - Test your plugin by right-clicking on an empty space within a folder.

### Example:
```python
plugin_info = {
    "title": "My Plugin Title",
    "description": "Description of my plugin.",
    "menu_name": "My Plugin Menu",
    "type": ["DIRECTORY_BACKGROUND"],
}
def driver(folders, params):
    for folder in folders:
        print("Processing folder:", folder)
```

---

## Example Plugins
- **Remove Empty Folders:** Recursively remove empty folders within directories.
- **Unpack Files From Folder:** Move files from subfolders to parent directories.
- **Copy File Content:** Copy the content of all files in the current directory to the clipboard.
- *For more examples, see my other [plugins](https://github.com/abdbbdii/plugins)*.

## License
This project is licensed under the [BSD License](https://github.com/abdbbdii/context-menu-plugin-manager/blob/main/LICENSE).

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests to improve this project.

## Credits
Shout out to [@saleguas](https://github.com/saleguas) for making [`context-menu`](https://github.com/saleguas/context_menu) python package.
