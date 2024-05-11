## Remove Empty Folders

### Description
The "Remove Empty Folders" plugin removes empty folders from the selected directory or directories. Users can specify the maximum subfolder level to search for empty folders.

### Plugin Info
- **Title:** Remove Empty Folders
- **Description:** Remove empty folders from the selected folder(s)
- **Type:** DIRECTORY_BACKGROUND, DIRECTORY
- **Menu Name:** abd Utils

### Usage
1. Select the folder or folders from which you want to remove empty folders.
2. Right-click on the selected directory or directories.
3. Choose the "Remove Empty Folders" option from the context menu.
4. A dialog window will prompt you to select the maximum subfolder level to search for empty folders. You can either specify a level or select to search all subfolders.
5. Click "Ok" to confirm the selection.
6. Any empty folders found within the specified subfolder level will be permanently deleted using the `send2trash` library.

### Notes
- If no empty folders are found within the specified subfolder level, a message will be displayed indicating that there are no empty folders to remove.
- The plugin utilizes a custom selector window to allow users to specify the maximum subfolder level. Users can also choose to select all subfolders for the search.