import json, dotenv
from os import listdir
from shutil import move
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
from context_menu import menus

ROOT = Path(__file__).parent
PLUGINS_DIR = ROOT / "plugins"
ASSETS_DIR = ROOT / "assets"
DOT_ENV = ROOT / ".env"
plugin_types = ["DIRECTORY", "DIRECTORY_BACKGROUND", "DRIVE", "FILES"]
dotenv.load_dotenv(DOT_ENV)


class Plugin:

    def __init__(self, file_name=None, parent=None, path=None, driver=None, title=None, icon=None, markdown=None, description=None, menu_name=None, supported_type=None, enable=None):
        self.file_name = file_name
        self.parent = parent
        self.path = path
        self.driver = driver
        self.title = title
        self.icon = icon
        self.markdown = markdown
        self.description = description
        self.menu_name = menu_name
        self.supported_type = supported_type
        self.enable = enable

    def construct_from_module(file_name, parent, module):
        return Plugin(
            file_name=file_name,
            parent=parent,
            path=PLUGINS_DIR / parent / Path(file_name),
            driver=module.driver,
            title=module.plugin_info["title"],
            icon=parent / "icon.ico" if "icon.ico" in listdir(PLUGINS_DIR / str(parent)) else ASSETS_DIR / "favicon.ico",
            markdown=parent / "README.md" if "README.md" in listdir(PLUGINS_DIR / str(parent)) else ASSETS_DIR / "README.md",
            description=module.plugin_info["description"],
            menu_name=module.plugin_info["menu_name"],
            supported_type={key: key in module.plugin_info["type"] for key in plugin_types},
            enable=False,
        )

    def construct_from_dictionary(recorded_plugin):
        return Plugin(
            file_name=recorded_plugin["file_name"],
            parent=recorded_plugin["parent"],
            path=recorded_plugin["path"],
            driver=None,
            title=None,
            icon=None,
            markdown=None,
            description=None,
            menu_name=recorded_plugin["menu_name"],
            supported_type=recorded_plugin["supported_type"],
            enable=recorded_plugin["enable"],
        )

    def enable_plugin(self):
        for type in self.supported_type:
            if self.supported_type[type]:
                print("[ADDING]", type, self.title, "in", self.menu_name)
                menu = menus.ContextMenu(self.menu_name, type)
                menu.add_items([menus.ContextCommand(self.title, icon_path=str(self.icon), python=self.driver)])
                menu.compile()
        self.enable = True

    def disable_plugin(self):
        for type, supported in self.supported_type.items():
            if supported:
                print("[REMOVING]", type, self.title, "from", self.menu_name)
                try:
                    menus.removeMenu(self.menu_name, type)
                except FileNotFoundError:
                    pass
        self.enable = False


class PluginManager:

    def __init__(self):
        self.plugins: list[Plugin] = []
        self.loadSession()

    def loadPluginsFromPluginFolder(self):
        for dir_path in listdir(PLUGINS_DIR):
            if temp := self.loadPlugin(PLUGINS_DIR / dir_path):
                self.plugins.append(temp)

    def loadPlugin(self, dir_path: Path):
        if not Path(dir_path).is_dir():
            return False
        temp = []
        for file in listdir(dir_path):
            if not Path(file).is_dir() and file.endswith(".py"):
                spec = spec_from_file_location(file.rstrip(".py"), dir_path / file)
                module = module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, "plugin_info") and hasattr(module, "driver"):
                    temp.append(Plugin.construct_from_module(file, dir_path, module))
        if len(temp) == 1:
            if dir_path.parent != PLUGINS_DIR:
                move(dir_path, PLUGINS_DIR)
                self.loadPlugin(PLUGINS_DIR / dir_path)
            else:
                return temp[0]
        return False

    def getPugin(self, path):
        for plugin in self.plugins:
            if plugin.path == path:
                return plugin

    def getPugins(self, name):
        return [plugin for plugin in self.plugins if plugin.title == name]

    def disable_all_plugins(self):
        for plugin in self.plugins:
            plugin.disable_plugin()
        print("Disabled all plugins")

    def enable_all_plugins(self):
        for plugin in self.plugins:
            plugin.enable_plugin()
        print("Enabled all plugins")

    def refresh_context_menu_plugins(self):
        for plugin in self.plugins:
            if not plugin.enable:
                plugin.disable_plugin()

        for plugin in self.plugins:
            if plugin.enable:
                plugin.enable_plugin()
        print("Re-enabled plugins")

    def saveSession(self):
        with open("record.json", "w") as f:
            json.dump(
                [
                    {
                        "file_name": str(plugin.file_name),
                        "parent": str(plugin.parent),
                        "path": str(plugin.path),
                        "menu_name": plugin.menu_name,
                        "supported_type": plugin.supported_type,
                        "enable": plugin.enable,
                    }
                    for plugin in self.plugins
                ],
                f,
                indent=4,
            )
        print("Saved session")

    def loadSession(self):
        self.loadPluginsFromPluginFolder()
        with open("record.json", "r") as f:
            for plugin in json.load(f):
                if temp := self.getPugin(Path(plugin["path"])):
                    temp.enable = plugin["enable"]
                else:
                    Plugin.construct_from_dictionary(recorded_plugin=plugin).disable_plugin()

        self.refresh_context_menu_plugins()
        print("Loaded session")

    def isAllPluginEnabled(self):
        return all([plugin.enable for plugin in self.plugins])
