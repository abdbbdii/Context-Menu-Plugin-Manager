## Display Folder Tree

This plugin is designed to display the folder structure in the current directory in a tree format.

## Features

- Displays the directory structure in a readable tree format.
- Ignores directories like `.git`, `__pycache__`, `env`, and `.vscode`.
- Copies the content of batch files to the clipboard (extendable).

## How to Use

1. Navigate to the directory containing the files you want to copy.
2. Invoke the plugin from the menu or context menu.
3. Confirm the selection to copy the content to the clipboard.

## Example Output

A tree structure of the directory will be displayed, for example:

```
├─ file1.txt
├─ folder1/
│  ├─ file2.txt
└─ folder2/
   └─ file3.txt
```