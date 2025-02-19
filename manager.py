import os
import json
import uuid
from pathlib import Path
from types import FunctionType
from typing import Literal, Any
from importlib.util import spec_from_file_location, module_from_spec

from context_menu import menus


ROOT = Path(__file__).parent
PLUGINS_DIR = ROOT / "plugins"
ASSETS_DIR = ROOT / "assets"
SESSION_FILE = ROOT / "record.json"
DOT_ENV = ROOT / ".env"
plugin_types = ["DIRECTORY", "DIRECTORY_BACKGROUND", "DRIVE", "FILES", "DESKTOP"]


def driver_decorator(func: FunctionType) -> FunctionType:
    def wrapper(*args, **kwargs):
        if "params" in kwargs:
            if isinstance(kwargs["params"], str):
                kwargs["params"] = json.loads(kwargs["params"])
        else:
            if len(args) > 1 and isinstance(args[1], str):
                args = list(args)
                args[1] = json.loads(args[1])
                args = tuple(args)
        return func(*args, **kwargs)

    return wrapper


class Plugin(menus.ContextCommand):
    def __init__(
        self,
        name: str,
        python: FunctionType | None = None,
        path: Path | str | None = None,
        icon_path: Path | str | None = None,
        markdown: Path | str | None = None,
        description: str | None = None,
        supported_types: list[Literal["FILES", "DIRECTORY", "DIRECTORY_BACKGROUND", "DRIVE", "DESKTOP"]] | None = None,
        enabled: bool = False,
        configs: dict[str, Any] | None = None,
    ):
        super().__init__(
            name=name,
            python=python,
            icon_path=str(icon_path),
        )
        self.id = uuid.uuid4()
        self.name = name
        self.python = python
        self.icon_path = str(icon_path)
        self.markdown = markdown
        self.description = description
        self.supported_types = supported_types
        self.selected_types = supported_types
        self.path = path
        self.enabled = enabled
        self.configs = configs
        self.params = ""

        self.set_params_from_config()

    @staticmethod
    def is_plugin_folder(path: Path) -> bool:
        return "function.py" in os.listdir(path) and "plugin.json" in os.listdir(path)

    def get_from_path(path: Path) -> "Plugin":
        plugin_json = json.loads(open(path / "plugin.json").read())

        spec = spec_from_file_location("function", path / "function.py")
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        # module.driver = driver_decorator(module.driver)

        return Plugin(
            name=path.name,
            icon_path=path / "icon.ico" if "icon.ico" in os.listdir(path) else ASSETS_DIR / "favicon.ico",
            markdown=path / "README.md" if "README.md" in os.listdir(path) else ASSETS_DIR / "README.md",
            description=plugin_json["description"],
            supported_types=plugin_json["supported_types"],
            configs=plugin_json["configs"] if "configs" in plugin_json else None,
            python=module.driver,
            enabled=True,
            path=path,
        )

    def __repr__(self):
        return "ContextCommand(name='{}', icon_path='{}', params='{}') {}".format(
            self.name,
            self.icon_path,
            json.dumps(self.configs).replace(r'"', r"\"") if self.configs else "",
            self.selected_types,
        )

    def set_params_from_config(self):
        if not self.configs:
            self.params = ""
            return
        params = {}
        for config in self.configs:
            params[config["name"]] = config["value"] if "value" in config else config["default"]
        self.params = json.dumps(params).replace(r'"', r"\"")

    def update_config_values(self, params: dict):
        if not self.configs:
            return None
        for config in self.configs:
            config["value"] = params[config["name"]] if config["name"] in params else None

class Menu(menus.ContextMenu):
    def __init__(
        self,
        name: str,
        description: str | None = None,
        path: Path | str | None = None,
        icon_path: Path | str | None = None,
    ):
        self.id = uuid.uuid4()
        self.name = name
        self.description = description
        self.icon_path = str(icon_path)
        self.sub_items: list[menus.ItemType] = []
        self.path = path
        self.type = None
        self.enabled = False
        super().__init__(
            name=name,
            type=None,
            icon_path=str(icon_path),
        )

    @staticmethod
    def is_menu_folder(path: Path) -> bool:
        return "plugin.json" in os.listdir(path) and "function.py" not in os.listdir(path)

    @staticmethod
    def get_from_path(path: Path) -> "Menu":
        plugin_json = json.loads(open(path / "plugin.json").read())
        return Menu(
            name=path.name,
            description=plugin_json["description"],
            icon_path=path / "icon.ico" if "icon.ico" in os.listdir(path) else ASSETS_DIR / "favicon.ico",
            path=path,
        )

    def get_sub_items(self):
        return self.sub_items

    def __repr__(self):
        return "ContextMenu(name='{}', icon_path='{}', type='{}')".format(self.name, self.icon_path, self.type)


class PluginManager:
    def __init__(self, path: Path | str = PLUGINS_DIR, no_setup=False):
        self.items: list[Plugin | Menu] = []
        if no_setup:
            return
        self.get_from_path(path)
        self.selected_plugin: Plugin | None = self.get_first_plugin()
        self.load_session()

    class ItemType:
        MENU = Menu
        PLUGIN = Plugin

    def get_from_path(self, path: Path | str):
        path = Path(path).resolve()
        if not os.path.exists(path) or not os.path.isdir(path):
            print(f"The directory '{path}' does not exist.")
            return

        items = os.listdir(path)
        menus = [Menu.get_from_path(path / item) for item in items if Menu.is_menu_folder(path / item)]
        # plugins = [Plugin.get_from_path(path / item) for item in items if Plugin.is_plugin_folder(path / item)]

        if menus:
            for menu in menus:
                PluginManager.add_path_items(menu, path / menu.name)
                self.items.append(menu)

        # if plugins:
        #     for plugin in plugins:
        #         print(f"menus.removeMenu('Command for {plugin.name}', '{plugin.supported_types}')")
        #         plugin = f"Command for {plugin}"
        #         menus.FastCommand(plugin, type="FILES", python=plugin.python).compile()

    def set_attr(self, id: uuid.UUID, attr: str, value):
        for plugin in self.walk_items(walk_only=PluginManager.ItemType.PLUGIN):
            if plugin.id == id:
                setattr(plugin, attr, value)

    @staticmethod
    def add_path_items(menu: Menu | Plugin, path: Path):
        for root, dirs, files in os.walk(path):
            for dir_name in dirs:
                root = Path(root)
                if Menu.is_menu_folder(root / dir_name):
                    sub_menu: Menu = Menu.get_from_path(root / dir_name)
                    PluginManager.add_path_items(sub_menu, root / dir_name)
                    menu.add_items([sub_menu])
                elif Plugin.is_plugin_folder(root / dir_name):
                    plugin: Plugin = Plugin.get_from_path(root / dir_name)
                    PluginManager.add_path_items(plugin, root / dir_name)
                    menu.add_items([plugin])
            break

    def print(self):
        for item in self.items:
            PluginManager.recursive_print(item)

    @staticmethod
    def recursive_print(menu: Menu | Plugin, level: int = 0):
        print("  " * level, menu)
        if isinstance(menu, Plugin):
            return
        for item in menu.sub_items:
            PluginManager.recursive_print(item, level + 1)

    def get_expand_types(self, filter=None):
        expanded_plugins = []
        for plugin in self.items:
            if isinstance(plugin, Menu):
                for type in plugin_types:
                    new_menu = Menu(name=plugin.name, description=plugin.description, icon_path=plugin.icon_path, path=plugin.path)
                    new_menu.type = type
                    PluginManager.__expand_menu_types(new_menu, plugin, type, filter)
                    if new_menu.sub_items:
                        expanded_plugins.append(new_menu)
        return expanded_plugins

    @staticmethod
    def __expand_menu_types(new_menu: Menu, original_menu: Menu, type: str, filter=None):
        for item in original_menu.sub_items:
            if isinstance(item, Menu):
                sub_menu = Menu(name=item.name, description=item.description, icon_path=item.icon_path, path=item.path)
                sub_menu.type = type
                PluginManager.__expand_menu_types(sub_menu, item, type)
                if sub_menu.sub_items:
                    new_menu.add_items([sub_menu])
            elif isinstance(item, Plugin) and (not filter or filter(item)):
                if item.selected_types and type in item.selected_types:
                    new_menu.add_items([item])

    def create_menu(self):
        expanded_items = self.get_expand_types(filter=lambda x: x.enabled == True)
        for item in expanded_items:
            if isinstance(item, Menu):
                item.compile()

    def remove_menu(self):
        expanded_items = self.get_expand_types(filter=lambda x: x.enabled == False)
        for item in expanded_items:
            if isinstance(item, Menu):
                try:
                    menus.removeMenu(item.name, item.type)
                except:
                    pass

    def disable_all(self):
        for plugin in self.walk_items():
            plugin.enabled = False

    def enable_all(self):
        for plugin in self.walk_items():
            plugin.enabled = True

    def get_first_plugin(self) -> Plugin:
        for plugin in self.walk_items(walk_only=PluginManager.ItemType.PLUGIN):
            return plugin

    def select_plugin(self, id: uuid.UUID):
        for plugin in self.walk_items(walk_only=PluginManager.ItemType.PLUGIN):
            if plugin.id == id:
                self.selected_plugin = plugin
                return plugin

    def refresh_menu(self):
        expanded_items = self.get_expand_types()
        for item in expanded_items:
            if isinstance(item, Menu):
                try:
                    menus.removeMenu(item.name, item.type)
                except:
                    pass
        expanded_items = self.get_expand_types(filter=lambda x: x.enabled == True)
        for item in expanded_items:
            if isinstance(item, Menu):
                item.compile()

    def is_all_plugin_enabled(self):
        for plugin in self.walk_items(walk_only=PluginManager.ItemType.PLUGIN):
            if not plugin.enabled:
                return False
        return True

    def is_all_plugin_disabled(self):
        for plugin in self.walk_items(walk_only=PluginManager.ItemType.PLUGIN):
            if plugin.enabled:
                return False
        return True

    def walk_items(self, walk_only: Any | None = None):
        if not self.items:
            return
        for item in self.items:
            if walk_only is None or isinstance(item, walk_only):
                yield item
            if isinstance(item, Menu):
                yield from PluginManager.__walk_items(item, walk_only)

    def __walk_items(menu: Menu, walk_only: Any | None = None):
        for item in menu.sub_items:
            if walk_only is None or isinstance(item, walk_only):
                yield item
            if isinstance(item, Menu):
                yield from PluginManager.__walk_items(item, walk_only)

    def save_session(self):
        def serialize_item(item):
            if isinstance(item, Plugin):
                return {
                    "class": "Plugin",
                    "name": item.name,
                    "params": json.loads(item.params.replace(r"\"", r'"')) if item.params else {},
                    "enabled": item.enabled,
                    "selected_types": item.selected_types,
                }
            elif isinstance(item, Menu):
                return {
                    "class": "Menu",
                    "name": item.name,
                    "enabled": item.enabled,
                    "sub_items": [serialize_item(child) for child in item.sub_items],
                }

        with open(SESSION_FILE, "w") as f:
            session = [serialize_item(item) for item in self.items]

            json.dump(session, f, indent=4)

    def load_session(self):
        def deserialize_item(data):
            if data["class"] == "Plugin":
                plugin = Plugin(name=data["name"])
                plugin.enabled = data["enabled"]
                plugin.params = data["params"]
                plugin.selected_types = data["selected_types"]
                return plugin
            elif data["class"] == "Menu":
                menu = Menu(name=data["name"])
                menu.enabled = data["enabled"]
                menu.sub_items = [deserialize_item(child) for child in data["sub_items"]]
                return menu

        if not SESSION_FILE.exists():
            return

        prev_session = PluginManager(no_setup=True)
        with open(SESSION_FILE, "r") as f:
            session_data = json.load(f)
            prev_session.items = [deserialize_item(item) for item in session_data]
        self.copy_plugin_configuration(prev_session)

    def copy_plugin_configuration(self, other: "PluginManager"):
        for item in self.walk_items():
            for other_item in other.walk_items():
                if isinstance(item, Plugin) and item.name == other_item.name:
                    item.enabled = other_item.enabled
                    item.params = json.dumps(other_item.params).replace(r'"', r"\"")
                    item.selected_types = other_item.selected_types
                    item.update_config_values(other_item.params)
                elif isinstance(item, Menu) and item.name == other_item.name:
                    item.enabled = other_item.enabled

        other.disable_all()
        other.remove_menu()
        self.refresh_menu()
        del other

    @staticmethod
    def remove_menu_by_name(name: str, type: str):
        try:
            menus.removeMenu(name, type)
        except:
            pass
