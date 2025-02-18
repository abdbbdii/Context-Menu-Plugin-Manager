import os
import json
import uuid
from pathlib import Path
from types import FunctionType
from typing import Literal, Any
from importlib.util import spec_from_file_location, module_from_spec

import dotenv

from context_menu import menus


ROOT = Path(__file__).parent
PLUGINS_DIR = ROOT / "plugins"
ASSETS_DIR = ROOT / "assets"
SESSION_FILE = ROOT / "record.json"
DOT_ENV = ROOT / ".env"
plugin_types = ["DIRECTORY", "DIRECTORY_BACKGROUND", "DRIVE", "FILES", "DESKTOP"]
dotenv.load_dotenv(DOT_ENV)


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
        python: FunctionType,
        path: Path,
        icon_path: Path | str | None = None,
        markdown: Path | str | None = None,
        description: str | None = None,
        supported_types: list[Literal["FILES", "DIRECTORY", "DIRECTORY_BACKGROUND", "DRIVE", "DESKTOP"]] | None = None,
        enabled: bool = True,
        configs: dict[str, Any] | None = None,
    ):
        super().__init__(
            name=name,
            python=python,
            icon_path=str(icon_path),
            params=Plugin.get_params_from_config(configs),
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
        return "ContextCommand(name='{}', icon_path='{}', params='{}')".format(
            self.name,
            self.icon_path,
            json.dumps(self.configs).replace(r'"', r"\"") if self.configs else "",
        )

    @staticmethod
    def get_params_from_config(configs: dict[str, Any] | None) -> str:
        if not configs:
            return ""
        params = {}
        for config in configs:
            params[config["name"]] = config["value"] if "value" in config else config["default"]
        return json.dumps(params).replace(r'"', r"\"")

    @staticmethod
    def edit_config_from_params(params: dict, configs: dict[str, Any] | None) -> dict[str, Any] | None:
        if not configs:
            return None
        for config in configs:
            config["value"] = params[config["name"]] if config["name"] in params else None
        return configs


class Menu(menus.ContextMenu):
    def __init__(
        self,
        name: str,
        description: str,
        path: Path,
        icon_path: Path | str | None = None,
    ):
        self.id = uuid.uuid4()
        self.name = name
        self.description = description
        self.icon_path = str(icon_path)
        self.sub_items: list[menus.ItemType] = []
        self.path = path
        self.type = None
        self.enabled = True
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
    def __init__(self, path: Path | str):
        self.items: list[Plugin | Menu] = []
        self.generate_context_menu(path)
        self.selected_plugin: Plugin | None = self.get_first_plugin()
        self.load_session()

    def generate_context_menu(self, path: Path | str):
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
        for plugin in self.walk_plugin():
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
                    self._expand_menu_types(new_menu, plugin, type, filter)
                    if new_menu.sub_items:
                        expanded_plugins.append(new_menu)
        return expanded_plugins

    def _expand_menu_types(self, new_menu: Menu, original_menu: Menu, type: str, filter=None):
        for item in original_menu.sub_items:
            if isinstance(item, Menu):
                sub_menu = Menu(name=item.name, description=item.description, icon_path=item.icon_path, path=item.path)
                sub_menu.type = type
                self._expand_menu_types(sub_menu, item, type)
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

    def get_first_plugin(self) -> Plugin:
        for plugin in self.walk_plugin():
            return plugin

    def select_plugin(self, id: uuid.UUID):
        for plugin in self.walk_plugin():
            if plugin.id == id:
                self.selected_plugin = plugin
                return plugin

    def refresh_menu(self):
        expanded_items = self.get_expand_types(filter=lambda x: x.enabled == True)
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
        for plugin in self.walk_plugin():
            if not plugin.enabled:
                return False
        return True

    def is_all_plugin_disabled(self):
        for plugin in self.walk_plugin():
            if plugin.enabled:
                return False
        return True

    def walk_plugin(self):
        if not self.items:
            return
        for item in self.items:
            if isinstance(item, Plugin):
                yield item
            if isinstance(item, Menu):
                for plugin in self.walk_plugin_(item):
                    yield plugin

    def walk_plugin_(self, menu: Menu):
        for item in menu.sub_items:
            if isinstance(item, Plugin):
                yield item
            elif isinstance(item, Menu):
                self.walk_plugin_(item)

    def save_session(self):
        with open(SESSION_FILE, "w") as f:
            session = []
            for plugin in self.walk_plugin():
                session.append(
                    {
                        "name": plugin.name,
                        "params": json.loads(plugin.params.replace(r"\"", r'"')) if plugin.params else {},
                        "enabled": plugin.enabled,
                        "selected_types": plugin.selected_types,
                    }
                )
            json.dump(session, f, indent=4)

    def load_session(self):
        if not SESSION_FILE.exists():
            return
        with open(SESSION_FILE, "r") as f:
            for plugin in json.load(f):
                found = False
                for p in self.walk_plugin():
                    if p.name == plugin["name"]:
                        found = True
                        p.enabled = plugin["enabled"]
                        p.params = json.dumps(plugin["params"]).replace(r'"', r"\"")
                        p.selected_types = plugin["selected_types"]
                        p.configs = Plugin.edit_config_from_params(plugin["params"], p.configs)
                        break
                if not found:
                    for type in plugin["selected_types"]:
                        menus.removeMenu(plugin["name"], type=type)
