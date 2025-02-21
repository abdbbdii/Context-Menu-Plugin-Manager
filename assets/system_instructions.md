### Python Function

- Python function should contain the driver function as a starting point.
- Here is the code snippet that you can use to start with.
- The driver function should accept two arguments:
  - `folders`: list of strings
  - `params`: string

```
import json


def driver(items: list[str] = [], params: str = ""):
    json_data = json.loads(params) if params else {}

    print("Folders/Files:")
    for folder in items:
        print(folder)

    print("Params:")
    for key, value in json_data.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    driver(["."])
```

### `folders`

- The folders argument should contain the list of folders and files.
- The of folders should behave as follows:
  - DIRECTORY_BACKGROUND: The list contains the path of the parent folder.
  - DIRECTORY: The list contains the path of the selected folder.
  - FILES: The list contains the path of the selected file.
  - DRIVE: The list contains the path of the selected drive.
  - DESKTOP: The list contains the path of the desktop.

### `params`

- The params argument should contain the JSON string.
- The JSON string should contain the key-value pairs.
  - The key should be a string name as set in the configs object.
  - The value should be the user input value or default value.

### General Instructions

- Note that when user runs the plugin from context menu, if the info is printed in the terminal, it will be immidiately closed. So, it is recommended to use `input()` function to hold the terminal open.
- User can access the configs in the "Congigure Plugin" tab.