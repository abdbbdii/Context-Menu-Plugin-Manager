import os
import json
import uuid
import shutil
from pathlib import Path
from types import FunctionType
from typing import Literal, Any
from importlib.util import spec_from_file_location, module_from_spec

from context_menu import menus
from flet import (
    Image,
    Text,
    Button,
    Markdown,
    Container,
)

from AI import AI
from Themes import Themes


ROOT = Path(__file__).parent.parent.resolve()
PLUGINS_DIR = ROOT / "plugins"
os.makedirs(PLUGINS_DIR, exist_ok=True)
TEMP_DIR = ROOT / "temp"
os.makedirs(TEMP_DIR, exist_ok=True)
ASSETS_DIR = ROOT / "assets"
os.makedirs(ASSETS_DIR, exist_ok=True)
THEMES_DIR = ROOT / "assets" / "themes"
os.makedirs(THEMES_DIR, exist_ok=True)
PLUGIN_TEMPLATE = ROOT / "assets" / "Plugin Template"
DROPZONE_DLL_PATH = ROOT / "src" / "DropZone.dll"
SESSION_FILE = ROOT / "session.json"
SCHEMA_FILE = ASSETS_DIR / "schema.json"
SYSTEM_INSTRUCTIONS_FILE = ASSETS_DIR / "system_instructions.md"
PLUGIN_TYPES = ["DIRECTORY", "DIRECTORY_BACKGROUND", "DRIVE", "FILES", "DESKTOP"]


# DOT_ENV = ROOT / ".env"
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


class Controls:
    icon: Image = None
    name: Text = None
    description: Text = None
    configs: Container = None
    markdown: Markdown = None
    tile: Button = None
    enable_disable_btn: Button = None


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
        params: str = "",
        type: str = "",
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
        self.type = type
        self.params = params
        self.controls: Controls = Controls()

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
            enabled=False,
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

    def compile(self):
        if self.enabled:
            menus.FastCommand(self.name, type=self.type, python=self.python, params=self.params, icon_path=self.icon_path).compile()


class Menu(menus.ContextMenu):
    def __init__(
        self,
        name: str,
        description: str | None = None,
        path: Path | str | None = None,
        icon_path: Path | str | None = None,
    ):
        self.id = uuid.uuid4()
        self.name: str = name
        self.description: str | None = description
        self.icon_path = str(icon_path)
        self.sub_items: list[menus.ItemType] = []
        self.path: Path | None = path
        self.type: Literal["DIRECTORY", "DIRECTORY_BACKGROUND", "DRIVE", "FILES", "DESKTOP"] | None = None
        self.enabled: bool = False
        self.controls: Controls = Controls()
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
        self.selected_plugin: Plugin | None = next(self.walk_items(walk_only=PluginManager.ItemType.PLUGIN), None)
        self.previous_plugin: Plugin | None = None
        self.controls: Controls = Controls()
        self.themes = Themes(THEMES_DIR)
        self.ai_client = AI(
            schema=json.load(open(SCHEMA_FILE)),
            system_instructions=open(SYSTEM_INSTRUCTIONS_FILE).read(),
        )
        self.load_session()

    def generate_plugin(self, prompt: str):
        try:
            response: dict = self.ai_client.generate_object(prompt)
            plugin_dir = TEMP_DIR / response["name"]
            os.makedirs(plugin_dir)
            with open(plugin_dir / "function.py", "w") as file:
                file.write(response["function"])
            with open(plugin_dir / "plugin.json", "w") as file:
                file.write(json.dumps(response["plugin"]))
            with open(plugin_dir / "README.md", "w") as file:
                file.write(response["readme"])
            with open(plugin_dir / "requirements.txt", "w") as file:
                file.write("\n".join(response["requirements"]))
            # with open(plugin_dir / "icon.ico", "wb") as file:
            #     file.write(response["image"])
        except Exception as e:
            print(e)
            return False

        if PluginManager.check_path(TEMP_DIR):
            fs.move_contents(TEMP_DIR, PLUGINS_DIR)
        return True
    
    def uninstall_plugin(self, plugin: None | Plugin = None):
        if plugin:
            fs.empty_dir(plugin.path)
            try:
                os.rmdir(plugin.path)
            except Exception as e:
                print(e)
        else:
            self.uninstall_plugin(self.selected_plugin)

    def get_settings(self):
        return {
            "ai_api_key": self.ai_client.get_api_key(),
            "theme": self.themes.current.name,
        }

    def set_settings(self, settings):
        if "ai_api_key" in settings:
            self.ai_client.set_api_key(settings["ai_api_key"]) 
        if "theme" in settings:
            self.themes.set_theme(settings["theme"])

    @staticmethod
    def check_path(path: Path | str):
        try:
            temp_pm = PluginManager(TEMP_DIR, no_setup=True)
            temp_pm.get_from_path(path)
            if not len(temp_pm.items):
                return False
            temp_pm.get_expand_types()
        except Exception as e:
            print(e)
            return False
        return True

    class ItemType:
        MENU = Menu
        PLUGIN = Plugin

    def get_from_path(self, path: Path | str):
        path = Path(path).resolve()
        if not path.is_dir():
            return
        
        if Plugin.is_plugin_folder(path):
            self.items.append(Plugin.get_from_path(path))
            return

        menus, plugins = [], []

        for item in Path(path).iterdir():
            if item.is_dir():
                if Menu.is_menu_folder(item):
                    menus.append(Menu.get_from_path(item))
                elif Plugin.is_plugin_folder(item):
                    plugins.append(Plugin.get_from_path(item))

        for menu in menus:
            PluginManager.add_path_items(menu, menu.path)
            self.items.append(menu)

        self.items.extend(plugins)

    def set_attr(self, id: uuid.UUID, attr: str, value):
        for plugin in self.walk_items(walk_only=PluginManager.ItemType.PLUGIN):
            if plugin.id == id:
                setattr(plugin, attr, value)

    def reload_plugins(self):
        self.items = []
        self.get_from_path(PLUGINS_DIR)
        self.selected_plugin = next(self.walk_items(walk_only=PluginManager.ItemType.PLUGIN), None)
        self.previous_plugin = None
        self.load_session()

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
                for type in PLUGIN_TYPES:
                    new_menu = Menu(
                        name=plugin.name,
                        description=plugin.description,
                        icon_path=plugin.icon_path,
                        path=plugin.path,
                    )
                    new_menu.type = type
                    PluginManager.__expand_menu_types(new_menu, plugin, type, filter)
                    if new_menu.sub_items:
                        expanded_plugins.append(new_menu)
            if isinstance(plugin, Plugin):
                for type in plugin.selected_types:
                    new_plugin = Plugin(
                        name=plugin.name,
                        python=plugin.python,
                        path=plugin.path,
                        icon_path=plugin.icon_path,
                        markdown=plugin.markdown,
                        description=plugin.description,
                        supported_types=plugin.supported_types,
                        enabled=plugin.enabled,
                        configs=plugin.configs,
                        params=plugin.params,
                        type=type,
                    )
                    expanded_plugins.append(new_plugin)
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
            item.compile()

    def remove_menu(self):
        expanded_items = self.get_expand_types(filter=lambda x: x.enabled == False)
        for item in expanded_items:
            try:
                menus.removeMenu(item.name, item.type)
            except:
                pass

    def refresh_menu(self):
        expanded_items = self.get_expand_types()
        for item in expanded_items:
            try:
                menus.removeMenu(item.name, item.type)
            except:
                pass
        expanded_items = self.get_expand_types(filter=lambda x: x.enabled == True)
        for item in expanded_items:
            item.compile()

    def disable_all(self):
        for plugin in self.walk_items():
            plugin.enabled = False

    def enable_all(self):
        for plugin in self.walk_items():
            plugin.enabled = True

    def select_plugin(self, id: uuid.UUID | None = None, name: str | None = None) -> Plugin:
        for plugin in self.walk_items(walk_only=PluginManager.ItemType.PLUGIN):
            if plugin.id == id:
                if (self.selected_plugin.id != plugin.id and id) or (self.selected_plugin.name != plugin.name and name):
                    self.previous_plugin = self.selected_plugin
                    self.selected_plugin = plugin
                return plugin

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

    @staticmethod
    def __walk_items(menu: Menu, walk_only: Any | None = None):
        for item in menu.sub_items:
            if walk_only is None or isinstance(item, walk_only):
                yield item
            if isinstance(item, Menu):
                yield from PluginManager.__walk_items(item, walk_only)

    def initialize_ai(self, api_key: str):
        if api_key:
            self.ai_client.set_api_key(api_key)

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

        items = [serialize_item(item) for item in self.items]
        session = {"items": items, "settings": self.get_settings()}
        json.dump(session, open(SESSION_FILE, "w"), indent=4)

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
        session_data = json.load(open(SESSION_FILE))
        self.set_settings(session_data["settings"])
        prev_session.items = [deserialize_item(item) for item in session_data["items"]]
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
        self.save_session()

    @staticmethod
    def remove_menu_by_name(name: str, type: str):
        try:
            menus.removeMenu(name, type)
        except:
            pass


class fs:
    @staticmethod
    def move_contents(source_folder: Path, destination_folder: Path, overwrite=False):
        if not source_folder.exists():
            print("Source folder does not exist.")
            return

        os.makedirs(destination_folder, exist_ok=True)
        for filename in os.listdir(source_folder):
            src_path = source_folder / filename
            dest_path = destination_folder / filename
            if dest_path.exists() and not overwrite:
                print(f"File '{filename}' already exists in '{destination_folder}'")
                continue

            shutil.move(src_path, dest_path)

    @staticmethod
    def empty_dir(path: str):
        for filename in os.listdir(path):
            file_path = path / filename
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
