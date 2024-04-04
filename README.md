# Context Menu Plugin Manager

This project manages context menu plugins to extend functionality in various directories. It allows dynamic addition and removal of context menu items using Python scripts.

## Usage
1. Place plugin scripts in the `plugins` directory.
2. Modify plugins according to the provided template.
3. Run `main.py` to manage and load plugins.

## Features
- **Plugin Development:** Easily create plugins with metadata and functionality.
- **Dynamic Menu Modification:** Add or remove context menu items on the fly.
- **Extensible:** Customize and extend functionality by creating new plugins.

## Installation
1. Clone the repository:
    ```
    git clone https://github.com/abdbbdii/context-menu-plugin-manager.git
    ```

2. Go inside the repository:
    ```
    cd context-menu-plugin-manager
    ```

3. Create a virtual environment:
    ```
    python3 -m venv env
    ```
    For Windows
    ```
    env\Scripts\activate
    ```
    For Linux
    ```
    env/bin/activate
    ```

4. Install the requirements
    ```
    pip3 install -r requirements.txt
    ```

5. Specify your Figma API key (optional):
    > **_NOTE:_** How to get your figma API key:
    >   1. From the file browser, click the account menu in the top-left corner and select Settings.
    >   2. Scroll to the Personal access tokens section.
    >   3. Enter a name for your new token and press Enter.
    >   4. Copy the token that is generated and replace **your_api_key** with your FIGMA API key
    ```
    echo FIGMA_API_KEY="your_api_key" > .env
    ```

6. Run the program
    ```
    python3 main.py
    ```

## Warning
   - **Folder Relocation or Renaming**: If you move the project folder to a different location or rename it, you'll need to rerun `main.py`. Else the options will no longer work.
   - **Figma API Key**: The Figma API key is optional. If you choose to use it, ensure that you keep it secure. It's required to download up-to-date template for PDF ID Cards Example plugin.

## Creating a Plugin
1. **Create Python Script**:
    - Create a new Python script in the `plugins` directory.
    - Name the script appropriately, e.g., `my_plugin.py`.

2. **Define Metadata**:
    - Define a dictionary named `plugin_info` containing metadata about the plugin.
    - Metadata includes `title`, `description` (optional), `type`, and `menu_name`.
      - `title` is the name of the script that is desplayed as an item in context menu.
      - `description` (optional) is the description of the script.
      - `type` is the type of the plugin. It can be one or more of:
        - `DIRECTORY` for opening on a directory.
        - `DIRECTORY_BACKGROUND` for opening on the background of the directory.
        - `DRIVE` for opening on the drives(think USBs).
        - `FILES` for opening on a file.
      - `menu_name` is the name of the menu item that will be displayed in the context menu.
    - Example:
    ```python
    plugin_info = {
        "title": "My Plugin Title",
        "description": "Description of my plugin.",
        "type": ["DIRECTORY_BACKGROUND"],
        "menu_name": "My Plugin Menu",
    }
    ```

3. **Implement Functionality**:
    - Implement the `driver` function to define the plugin's behavior.
    - The `driver` function takes two parameters: `folders` (selected directories) and `params` (additional parameters).
    - Example:
    ```python
    def driver(folders, params):
        for folder in folders:
            print("Processing folder:", folder)
    ```

4. **Run the Project**:
    - Run `main.py` to load and manage plugins.
    - Test your plugin by right-clicking on an empty space within a folder.

## Example Plugins
- **PDF ID Cards:** Generate PDFs for ID cards from Figma designs.
- **Shop Menu Maker:** Create a menu for a shop from a json file.
- **Remove Empty Folders:** Recursively remove empty folders within directories.
- **Remove Extra Executables:** Delete redundant C/C++ executable files.
- **Unpack Files From Folder:** Move files from subfolders to parent directories.
- **Copy File Content:** Copy the content of all files in the current directory to the clipboard.

## License
This project is licensed under the [BSD License](https://github.com/abdbbdii/context-menu-plugin-manager/blob/main/LICENSE).

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests to improve this project.

## Credits
Shout out to [@saleguas](https://github.com/saleguas) for making [`context-menu`](https://github.com/saleguas/context_menu) python package.
