## Make Shop Menu

### Description
The "Make Shop Menu" plugin generates shop menu PDFs based on a Figma design. It processes JSON files containing menu data and creates PDF files for various menu sizes (small, large, and flex) using corresponding Figma templates.

### Plugin Info
- **Title:** Make Shop Menu
- **Description:** Make Shop Menu from figma design
- **Type:** FILES
- **Menu Name:** abd Utils

### Usage
1. Select the JSON file containing the menu data.
2. Right-click on the selected file.
3. Choose the "Make Shop Menu" option from the context menu.
4. The plugin will read the JSON file and process the menu data.
5. PDF files for small, large, and flex menu sizes will be generated using corresponding Figma templates.
6. The generated PDF files will be opened automatically.

### Notes
- The plugin utilizes Figma templates stored as SVG files to generate the menu PDFs.
- For each menu size, the plugin fetches the corresponding Figma template if it does not exist locally.
- The menu data from the JSON file is used to fill in placeholders in the Figma templates before generating the PDFs.
- The generated PDF files will be opened using the default application associated with PDF files on your system.
- If any error occurs during the process, an error message will be displayed using the `messagebox` module.