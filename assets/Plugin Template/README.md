# Template Plugin

This is a template plugin to help you get started with creating your own plugins.

## Usage

The `driver` function receives two arguments:

- `items`: A list of strings representing the selected folders/files.
- `params`: A JSON string containing the configuration parameters.

You can access the configuration parameters in the 'Configure Plugin' tab.

## Example

```python
import json  # Import the JSON module to work with JSON data

"""
It receives a list of items and a JSON string as parameters.
It prints the items and the parameters to the console.
The `__name__ == "__main__"` block is for testing purposes only.
The `driver` function is the entry point for the Python script.
"""


def driver(items: list[str] = [], params: str = ""):
    json_data = json.loads(params) if params else {}  # Convert JSON string to dictionary

    print("Folders/Files:")
    for item in items:
        print(item)

    print("Params:")
    for key, value in json_data.items():
        print(f"{key}: {value}")

    input("Press Enter to exit")  # Keep the console open by waiting for user input


if __name__ == "__main__":  # For testing only
    driver(["file1.txt", "file2.txt"], '{"param1": "value1", "param2": "value2"}')
```