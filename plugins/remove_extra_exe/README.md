## Remove Extra Executables

### Description
The "Remove Extra Executables" plugin removes additional C/C++ executable files (.exe) that are present alongside the corresponding source files (.cpp or .c) within the selected directory or directories.

### Plugin Info
- **Title:** Remove Extra Executables
- **Description:** Remove extra C/C++ executables from the selected folder(s)
- **Type:** DIRECTORY_BACKGROUND, DIRECTORY
- **Menu Name:** abd Utils

### Usage
1. Select the folder or folders from which you want to remove extra executables.
2. Right-click on the selected directory or directories.
3. Choose the "Remove Extra Executables" option from the context menu.
4. A window will appear displaying a list of folders containing extra executable files alongside their corresponding source files.
5. Review the list and select the folders from which you want to remove the extra executables.
6. Click "Confirm" to proceed with the removal process.
7. Any selected executable files will be permanently deleted using the `send2trash` library.

### Notes
- If no extra executable files are found within the selected folders, a message will be displayed indicating that there are no files to remove.
- The plugin utilizes a custom filter window to allow users to select the folders containing extra executables for removal. Users can choose to select all folders or manually deselect specific folders before confirming the action.