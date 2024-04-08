from importlib.util import spec_from_file_location, module_from_spec
import os, json
from .context_menu import menus


def load_plugins_with_folder(plugin_dir):
    if os.path.exists(os.path.join(plugin_dir, '.pluginigonre')):
        with open(os.path.join(plugin_dir, '.pluginigonre')) as f:
            ignore = f.read().split("\n")
    else:
        ignore = []
    plugins = []
    for folder in os.listdir(plugin_dir):
        if not os.path.isdir(os.path.join(plugin_dir, folder)) or folder in ignore:
            continue
        for file in os.listdir(os.path.join(plugin_dir, folder)):
            if file.endswith(".py"):
                plugin_name = file.rstrip(".py")
                spec = spec_from_file_location(plugin_name, os.path.join(plugin_dir, folder, file))
                plugin = {"name": plugin_name, "folder": folder, "module": module_from_spec(spec)}
                spec.loader.exec_module(plugin["module"])
                if hasattr(plugin["module"], "plugin_info") and hasattr(plugin["module"], "driver"):
                    plugins.append(plugin)
    return plugins


def main():
    try:
        record = json.load(open("record.json"))
    except FileNotFoundError:
        record = {}
    for type, menus_ in record.items():
        for menu in menus_:
            print(type, "Removing", menu)
            menus.removeMenu(menu, type)

    record.clear()
    with open("record.json", "w") as f:
        json.dump(record, f)

    plugins = load_plugins_with_folder("plugins")
    types = ["DIRECTORY", "DIRECTORY_BACKGROUND", "DRIVE", "FILES"]
    for plugin in plugins:
        print("\nLoading", plugin["name"], "from", plugin["folder"])
        for type in plugin["module"].plugin_info["type"]:
            if type not in types:
                continue
            print(type, "Adding", plugin["module"].plugin_info["title"], "in", plugin["module"].plugin_info["manu_name"])
            menu = menus.ContextMenu(plugin["module"].plugin_info["manu_name"], type)
            menu.add_items([menus.ContextCommand(plugin["module"].plugin_info["title"], icon_path=plugin["module"].plugin_info.get("icon"), python=plugin["module"].driver)])
            menu.compile()
            if type not in record:
                record[type] = [plugin["module"].plugin_info["manu_name"]]
            elif plugin["module"].plugin_info["manu_name"] not in record[type]:
                record[type].append(plugin["module"].plugin_info["manu_name"])

    with open("record.json", "w") as f:
        json.dump(record, f)


if __name__ == "__main__":
    main()
