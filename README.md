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
    git clone https://github.com/abdbbdii/abd_utils.git
    ```

2. Go inside the repository:
    ```
    cd abd_utils
    ```

3. Create a virtual environment:
    ```
    python -m venv env
    env\Scripts\activate
    ```

4. Install the requirements
    ```
    pip install -r requirements.txt
    ```

5. Specify your Figma API key (optional):
    > **_NOTE:_** How to get your figma API key:
    >   1. From the file browser, click the account menu in the top-left corner and select Settings.
    >   2. Scroll to the Personal access tokens section.
    >   3. Enter a name for your new token and press Enter.
    >   4. Copy the token that is generated and replace **your_api_key** with your API key
    ```
    echo API_KEY="your_api_key" > .env
    ```

6. Run the program
    ```
    python main.py
    ```

## Creating a Plugin
1. **Create Python Script**:
    - Create a new Python script in the `plugins` directory.
    - Name the script appropriately, e.g., `my_plugin.py`.

2. **Define Metadata**:
    - Define a dictionary named `plugin_info` containing metadata about the plugin.
    - Metadata includes `title`, `description`, `type`, and `menu_name`.
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
- **Remove Empty Folders:** Recursively remove empty folders within directories.
- **Remove Extra Executables:** Delete redundant C/C++ executable files.
- **Unpack Files From Folder:** Move files from subfolders to parent directories.

## License
This project is licensed under the [BSD License](https://github.com/abdbbdii/abd_utils/blob/main/LICENSE).

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests to improve ABD Utils.