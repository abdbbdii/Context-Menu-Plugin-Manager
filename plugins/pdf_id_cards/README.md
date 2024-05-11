## Make PDF For ID Cards

### Description
The "Make PDF For ID Cards" plugin generates a PDF file for ID cards based on Figma design templates. It converts SVG templates with placeholders for images into PDF format, incorporating the images specified for the front and back sides of the ID cards.

### Plugin Info
- **Title:** Make PDF For ID Cards
- **Description:** Make PDF For ID Cards from figma design
- **Type:** DIRECTORY_BACKGROUND
- **Menu Name:** abd Utils

### Usage
1. Ensure that the folder contains `front.jpg` and `back.jpg` images for the front and back sides of the ID cards, respectively.
2. Right-click on the desired directory.
3. Select the "Make PDF For ID Cards" option from the context menu.
4. The plugin will create an `id_card.pdf` file in the same directory, containing the ID cards based on the provided images and the Figma design template.

### Requirements
- Ensure that the Figma API key is set in the `.env` file as `FIGMA_API_KEY`.
- SVG templates for ID cards must be available in the `svg_templates` directory.

### Notes
- If the required images or SVG templates are not found, the plugin will raise a `FileNotFoundError`.
- The generated PDF file will be opened automatically after creation using the default system application for PDF files.