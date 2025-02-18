import json
from pprint import pprint


def driver(folders: list[str] = [], params: str = ""):
    input("Press Enter to continue...")
    print("Hello from the plugin!")
    pprint(folders)
    pprint(params)
    input("Press Enter to continue...")
    json_data = json.loads(params) if params else {}
    pprint(json_data)
    input("Press Enter to continue...")


if __name__ == "__main__":
    driver(["."])
