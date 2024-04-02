from importlib.util import spec_from_file_location, module_from_spec
import os, json
from context_menu import menus


def load_plugins(plugin_dir):
    plugins = {}
    for file in os.listdir(plugin_dir):
        if file.endswith(".py"):
            plugin_name = file.rstrip(".py")
            spec = spec_from_file_location(plugin_name, os.path.join(plugin_dir, file))
            plugins[plugin_name] = module_from_spec(spec)
            spec.loader.exec_module(plugins[plugin_name])
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
    plugins = load_plugins("plugins")
    for type in ["DIRECTORY", "DIRECTORY_BACKGROUND", "DRIVE", "FILELOC", "FILES"]:
        if len([value for value in plugins.values() if type in value.plugin_info["type"]]) != 0:
            for _, value in plugins.items():
                print(type, "Adding", value.plugin_info["title"], "in", value.plugin_info["manu_name"])
                if type in value.plugin_info["type"]:
                    menu = menus.ContextMenu(value.plugin_info["manu_name"], type)
                    menu.add_items([menus.ContextCommand(value.plugin_info["title"], python=value.driver)])
                    menu.compile()
                    if type not in record:
                        record[type] = [value.plugin_info["manu_name"]]
                    elif value.plugin_info["manu_name"] not in record[type]:
                        record[type].append(value.plugin_info["manu_name"])
    json.dump(record, open("record.json", "w"))


if __name__ == "__main__":
    main()
