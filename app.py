import os
from typing import Callable
import shutil
import time

import flet as f

from manager import *
from Themes import Themes
from DropZone import LoadDLL


# all_installed = False
# while not all_installed:
#     try:
#         pm = PluginManager("plugins")
#     except ModuleNotFoundError as e:
#         system("pip install " + str(e).split("'")[1])
#     else:
#         all_installed = True


class cf:
    class Button(f.Button):
        def __init__(self, text: str | None = None, content: f.Control | None = None, on_click: Callable = None, icon: f.Icon = None):
            super().__init__(
                style=f.ButtonStyle(
                    bgcolor={
                        f.ControlState.HOVERED: t.theme.palette.bg_high_hover,
                        f.ControlState.DEFAULT: t.theme.palette.bg_high_selection,
                    },
                    padding=f.Padding(10, 5, 10, 5),
                    shape=f.RoundedRectangleBorder(radius=5),
                    elevation=0,
                    color=t.theme.palette.text,
                ),
                text=text,
                icon=icon,
                content=content,
                on_click=on_click,
                icon_color=t.theme.palette.text,
            )

    class Divider(f.Divider):
        def __init__(self, alt=False, thickness=1):
            super().__init__(color=t.theme.palette.divider_alt if alt else t.theme.palette.divider, thickness=thickness)

    class Switch(f.Switch):
        def __init__(self, value: bool | None = None, on_change: Callable | None = None, data: Any | None = None):
            super().__init__(
                value=value,
                inactive_track_color=t.theme.palette.bg,
                track_outline_color={
                    f.ControlState.SELECTED: f.Colors.TRANSPARENT,
                    f.ControlState.DEFAULT: t.theme.palette.bg_high_hover,
                },
                thumb_color={
                    f.ControlState.SELECTED: t.theme.palette.primary,
                    f.ControlState.DEFAULT: t.theme.palette.bg_high_hover,
                },
                active_color=t.theme.palette.primary,
                data=data,
                on_change=on_change,
            )

    class TextField(f.TextField):
        def __init__(self, label: str | None = None, value: str | None = None, multiline: bool = False, max_lines: int = 1, on_change: Callable | None = None, input_filter: f.InputFilter | None = None):
            super().__init__(
                label=label,
                value=value,
                multiline=multiline,
                max_lines=max_lines,
                border_color=t.theme.palette.divider,
                on_change=on_change,
                cursor_color=t.theme.palette.primary,
                focused_border_color=t.theme.palette.primary,
                label_style=f.TextStyle(color=t.theme.palette.text),
                input_filter=input_filter,
            )

    class Checkbox(f.Checkbox):
        def __init__(self, label: str | None = None, value: bool = False):
            super().__init__(
                label=label,
                value=value,
                active_color=t.theme.palette.primary,
                check_color=f.Colors.BLACK,
            )

    class Radio(f.Radio):
        def __init__(self, label: str | None = None, value: str | None = None):
            super().__init__(
                label=label,
                value=value,
                active_color=t.theme.palette.primary,
            )

    class Text(f.Text):
        class Size:
            LARGE = 20
            MEDIUM = 16
            SMALL = 14
            TINY = 12

        def __init__(self, text: str | None = None, overflow: f.TextOverflow = None, dimmed=False, size: Size = Size.MEDIUM):
            super().__init__(value=text, size=size, color=t.theme.palette.text_muted if dimmed else t.theme.palette.text, overflow=overflow)

    class Dialog(f.AlertDialog):
        def __init__(
            self,
            title: str | None = None,
            subtitle: str | None = None,
            content: f.Control | None = None,
            actions: dict[str, Callable] = {},
            on_dismiss: Callable | None = None,
            get_callback: Callable | None = None,
            alignment: f.Alignment | None = None,
        ):
            super().__init__(
                modal=True,
                title=f.Column(
                    [
                        cf.Text(title, size=cf.Text.Size.LARGE),
                        cf.Text(subtitle, dimmed=True, size=cf.Text.Size.SMALL),
                    ],
                    spacing=5,
                    width=500,
                ),
                content=content,
                actions_alignment=f.MainAxisAlignment.END,
                bgcolor=t.theme.palette.bg,
                shape=f.RoundedRectangleBorder(radius=5),
                on_dismiss=on_dismiss,
                alignment=alignment,
            )
            for text, on_click in actions.items():
                self.actions.append(cf.Button(text, on_click=on_click if on_click else self.close_dialog))
            self.get_callback = get_callback

        def show(self, page: f.Page):
            page.open(self)

        def close_dialog(self, e: f.ControlEvent):
            e.page.close(e.control.parent)
            self.get_callback(e.control.text) if self.get_callback else None


def load_plugins(files: list[Path] | None):
    any_loaded = False
    if files is None:
        return any_loaded
    for file in files:
        if not isinstance(file, str):
            file = file.path
        file = Path(file).resolve()
        if file.name.endswith(".zip"):
            shutil.unpack_archive(file, TEMP_DIR)
            if not PluginManager.check_path(TEMP_DIR):
                empty_dir(TEMP_DIR)
                continue
            try:
                move_contents(TEMP_DIR, PLUGINS_DIR)
                empty_dir(TEMP_DIR)
            except Exception as e:
                print(e)
                empty_dir(TEMP_DIR)
                continue
            any_loaded = True
    return any_loaded


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


def main(page: f.Page, pm: PluginManager, t: Themes):
    def handle_imports(files: list[Path] | None):
        if dnd_dialog in page.controls:
            close_dnd_dialog()
        if load_plugins(files):
            pm.reload_plugins()
            expansion_tiles.controls = [get_expansion_tiles_container()]
            expansion_tiles.update()
            cf.Dialog(
                "Successfully Installed Plugins",
                "Plugins have been successfully installed",
                actions={"Ok": None},
            ).show(page)
        else:
            cf.Dialog(
                "Failed to Install Plugins",
                "No valid plugins found in the selected files",
                actions={"Ok": None},
            ).show(page)
        page.update()

    def open_dnd_dialog(e: f.ControlEvent):
        dnd_dialog.show(page)
        page.update()

    def close_dnd_dialog(e: f.ControlEvent | None = None):
        page.close(dnd_dialog)
        page.update()

    def generate_plugin(e: f.ControlEvent):
        # check if key is valid and if not then do this:
        cf.Dialog(
            "Enter the key",
            "Enter the key to generate the plugin",
            cf.TextField(label="Key", multiline=False, max_lines=1),
            {
                "Generate": lambda e: print("Generate"),
                "Cancel": None,
            },
        ).show(page)

    def add_plugin(e: f.ControlEvent):
        page.add(filepicker := f.FilePicker(on_result=lambda e: handle_imports(e.files)))
        filepicker.pick_files(
            "Select file...",
            file_type=f.FilePickerFileType.CUSTOM,
            initial_directory=Path.home() / "Downloads",
            allow_multiple=True,
            allowed_extensions=["zip"],
        )
        page.update()

    def get_expansion_tiles_container():
        return f.Column(
            controls=[
                f.Container(
                    content=get_expansion_tiles(plugin),
                    padding=15,
                    bgcolor=t.theme.palette.bg,
                    border_radius=5,
                )
                for plugin in pm.items
            ],
            scroll=True,
            spacing=10,
        )

    def get_expansion_tiles(item: Menu | Plugin):
        if not (isinstance(item, Menu) or isinstance(item, Plugin)):
            return
        if isinstance(item, Plugin):
            item.control = f.Button(
                content=f.Row(
                    controls=[
                        f.Image(item.icon_path, width=40, height=40, border_radius=10),
                        f.Column(
                            [
                                cf.Text(item.name, overflow=f.TextOverflow.ELLIPSIS, size=cf.Text.Size.SMALL),
                                cf.Text(item.description, overflow=f.TextOverflow.ELLIPSIS, dimmed=True, size=cf.Text.Size.TINY),
                            ],
                            spacing=2,
                            alignment=f.alignment.center_left,
                            expand=True,
                            scroll=f.ScrollMode.ADAPTIVE,
                        ),
                        cf.Switch(value=item.enabled, on_change=toggle_plugin, data=item.id),
                    ],
                    height=60,
                    alignment=f.MainAxisAlignment.SPACE_BETWEEN,
                ),
                style=f.ButtonStyle(
                    bgcolor={
                        f.ControlState.HOVERED: t.theme.palette.bg_selection,
                        f.ControlState.FOCUSED: t.theme.palette.bg_selection,
                        f.ControlState.DEFAULT: t.theme.palette.bg_selection if pm.selected_plugin.id == item.id else t.theme.palette.bg,
                    },
                    shape=f.RoundedRectangleBorder(radius=5),
                    elevation=0,
                ),
                expand=True,
                on_click=change_plugin_page,
                data=item,
            )
            return item.control

        item.control = f.ExpansionTile(
            title=cf.Text(item.name, size=cf.Text.Size.SMALL),
            subtitle=cf.Text(item.description, dimmed=True, size=cf.Text.Size.TINY),
            leading=f.Image(item.icon_path, width=40, height=40, border_radius=10),
            controls=[
                f.Container(
                    f.Column(
                        [get_expansion_tiles(sub_item) for sub_item in item.sub_items],
                        spacing=5,
                    ),
                    border=f.Border(left=f.BorderSide(color=t.theme.palette.divider, width=2)),
                    padding=f.padding.Padding(15, 5, 0, 5),
                ),
            ],
            tile_padding=f.padding.Padding(10, 5, 10, 5),
            shape=f.RoundedRectangleBorder(radius=5),
            maintain_state=True,
            initially_expanded=True,
            icon_color=t.theme.palette.text,
        )
        return item.control

    def change_plugin_page(e: f.ControlEvent):
        pm.select_plugin(e.control.data.id)
        plugin_icon.src = pm.selected_plugin.icon_path
        plugin_title.value = pm.selected_plugin.name
        plugin_description.value = pm.selected_plugin.description
        plugin_markdown.value = open(pm.selected_plugin.markdown, "r", encoding="utf-8").read()
        plugin_configs.content = get_plugin_config()
        pm.previous_plugin.control.style.bgcolor[f.ControlState.DEFAULT] = t.theme.palette.bg
        e.control.style.bgcolor[f.ControlState.DEFAULT] = t.theme.palette.bg_selection
        page.update()

    def toggle_plugin(e: f.ControlEvent):
        pm.set_attr(e.control.data, "enabled", e.control.value)
        if pm.is_all_plugin_disabled():
            pm.remove_menu()
            enable_disable_btn.text = "Enable All"
        elif pm.is_all_plugin_enabled():
            pm.create_menu()
            enable_disable_btn.text = "Disable All"
        else:
            pm.refresh_menu()
            enable_disable_btn.text = "Enable All"
        pm.save_session()
        page.update()

    def toggle_all_plugins(e: f.ControlEvent):
        value: bool = e.control.text == "Enable All"
        for plugin in pm.walk_items(Plugin):
            plugin.enabled = value
            plugin.control.content.controls[2].value = value
        if value:
            pm.create_menu()
            enable_disable_btn.text = "Disable All"
        else:
            pm.remove_menu()
            enable_disable_btn.text = "Enable All"
        pm.save_session()
        page.update()

    def get_plugin_config():
        config_column = f.Column(
            controls=[
                cf.Text("Plugin Configurations", size=cf.Text.Size.LARGE),
                cf.Divider(),
                f.Column(
                    controls=[
                        cf.Text("Change Plugin Type", size=cf.Text.Size.MEDIUM),
                        cf.Text("Only change the plugin type if you know what you are doing", dimmed=True, size=cf.Text.Size.SMALL),
                        control := f.Column(
                            [cf.Checkbox(label=option, value=option in pm.selected_plugin.selected_types) for option in PLUGIN_TYPES],
                        ),
                    ],
                    spacing=15,
                ),
            ],
            spacing=15,
            scroll=f.ScrollMode.ADAPTIVE,
        )

        pm.selected_plugin.types_control = control

        if not pm.selected_plugin.configs:
            return config_column
        for config in pm.selected_plugin.configs:
            config_column.controls.append(cf.Divider())
            container = f.Column(spacing=15)
            container.controls.append(cf.Text(config["label"], size=cf.Text.Size.MEDIUM))
            container.controls.append(cf.Text(config["description"], dimmed=True, size=cf.Text.Size.SMALL))
            if config["type"] == "str":
                control = cf.TextField(label=config["label"], value=config["value"] if "value" in config else config["default"])
            elif config["type"] == "bool":
                control = cf.Switch(value=config["value"] if "value" in config else config["default"])

            elif config["type"] == "int":
                control = cf.TextField(label=config["label"], value=config["value"] if "value" in config else config["default"], input_filter=f.NumbersOnlyInputFilter())

            elif config["type"] == "float":
                control = cf.TextField(label=config["label"], value=config["value"] if "value" in config else config["default"], input_filter=f.InputFilter("^[0-9]*[.]?[0-9]*$"))

            elif config["type"] == "checkbox":
                control = f.Column([cf.Checkbox(label=option, value=option in (config["value"] if "value" in config else config["default"])) for option in config["options"]])

            elif config["type"] == "radio":
                control = f.RadioGroup(
                    content=f.Column(
                        [cf.Radio(value=option, label=option) for option in config["options"]],
                    ),
                    value=config["value"] if "value" in config else config["default"],
                )
            config["control"] = control
            container.controls.append(control)
            config_column.controls.append(container)

        return config_column

    def refresh_config_page():
        pm.selected_plugin.set_params_from_config()
        pm.refresh_menu()
        pm.save_session()
        page.update()

    def reset_config(e: f.ControlEvent):
        for config in pm.selected_plugin.configs:
            if "value" in config:
                if config["type"] == "str" or config["type"] == "int" or config["type"] == "float" or config["type"] == "bool":
                    config["control"].value = config["default"]
                elif config["type"] == "checkbox":
                    for control in config["control"].controls:
                        control.value = control.label in config["default"]
                elif config["type"] == "radio":
                    config["control"].value = config["default"]

                del config["value"]

        refresh_config_page()

    def save_plugin_configs(e: f.ControlEvent):
        pm.selected_plugin.selected_types = [control.label for control in pm.selected_plugin.types_control.controls if control.value]
        if not pm.selected_plugin.configs:
            return
        for config in pm.selected_plugin.configs:
            if config["type"] == "str":
                config["value"] = config["control"].value
            elif config["type"] == "bool":
                config["value"] = config["control"].value
            elif config["type"] == "int":
                config["value"] = int(config["control"].value)
            elif config["type"] == "float":
                config["value"] = float(config["control"].value)
            elif config["type"] == "checkbox":
                config["value"] = [control.label for control in config["control"].controls if control.value]
            elif config["type"] == "radio":
                config["value"] = config["control"].value

        refresh_config_page()

    page.title = "Context Menu Plugin Manager"
    page.icon = "assets/icon.ico"
    page.fonts = {"Inter": "Inter[slnt,wght].ttf"}
    page.theme = f.Theme(font_family="Inter")
    page.padding = 0
    page.bgcolor = t.theme.palette.bg_low
    page.window_min_height = 610
    page.window_min_width = 713

    page.appbar = f.AppBar(
        title=f.Row(
            [
                cf.Text("Context Menu Plugin Manager", size=cf.Text.Size.LARGE),
                f.Container(expand=True),
                cf.Button("Generate Plugin", icon=f.Icons.BOLT, on_click=generate_plugin),
                cf.Button("Add Plugin", icon=f.Icons.ADD, on_click=add_plugin),
                cf.Button("Open Plugins Folder", icon=f.Icons.FOLDER, on_click=lambda e: os.system(f'explorer "{PLUGINS_DIR}"')),
                # ft.IconButton(ft.Icons.SETTINGS, tooltip="Settings", on_click=lambda e: print("Settings")),
            ],
            spacing=20,
        ),
        leading_width=70,
        automatically_imply_leading=True,
        bgcolor=t.theme.palette.bg_low,
        surface_tint_color=t.theme.palette.bg_low,
    )

    page.add(
        f.Row(
            controls=[
                f.Container(
                    f.Column(
                        [
                            f.Row(
                                [
                                    cf.Text("Plugins", size=cf.Text.Size.MEDIUM),
                                    enable_disable_btn := cf.Button(text="Disable All" if pm.is_all_plugin_enabled() else "Enable All", on_click=toggle_all_plugins),
                                ],
                                height=80,
                                alignment=f.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            expansion_tiles := f.Column(
                                [
                                    get_expansion_tiles_container(),
                                ],
                                scroll=f.ScrollMode.ADAPTIVE,
                                expand=True,
                            ),
                        ],
                    ),
                    bgcolor=t.theme.palette.bg_low,
                    padding=f.Padding(20, 0, 20, 20),
                    width=450,
                    alignment=f.alignment.top_left,
                ),
                f.Container(
                    f.Column(
                        [
                            f.Row(
                                [
                                    plugin_icon := f.Image(pm.selected_plugin.icon_path, width=130, height=130),
                                    f.Column(
                                        [
                                            plugin_title := cf.Text(pm.selected_plugin.name, size=cf.Text.Size.MEDIUM),
                                            plugin_description := cf.Text(pm.selected_plugin.description, dimmed=True, size=cf.Text.Size.SMALL),
                                            f.Row(
                                                [
                                                    # Component.Button("Uninstall"),
                                                    cf.Button(text="View in Explorer", on_click=lambda e: os.system(f'explorer "{pm.selected_plugin.path}"')),
                                                    cf.Button(text="Edit in VSCode", on_click=lambda e: os.system(f'code "{pm.selected_plugin.path}"')),
                                                ],
                                            ),
                                        ],
                                        spacing=10,
                                    ),
                                ],
                            ),
                            f.Tabs(
                                selected_index=0,
                                animation_duration=300,
                                tabs=[
                                    f.Tab(
                                        text="Description",
                                        content=f.Container(
                                            f.Column(
                                                [
                                                    plugin_markdown := f.Markdown(
                                                        open(pm.selected_plugin.markdown, "r", encoding="utf-8").read(),
                                                        code_theme=f.MarkdownCodeTheme.DRAGULA,
                                                        extension_set=f.MarkdownExtensionSet.GITHUB_WEB,
                                                    ),
                                                ],
                                                expand=True,
                                                scroll=f.ScrollMode.ADAPTIVE,
                                            ),
                                            padding=20,
                                        ),
                                    ),
                                    f.Tab(
                                        "Configure Plugin",
                                        content=f.Column(
                                            [
                                                plugin_configs := f.Container(
                                                    get_plugin_config(),
                                                    padding=f.Padding(20, 20, 20, 0),
                                                    expand=True,
                                                ),
                                                cf.Divider(alt=True, thickness=2),
                                                f.Row(
                                                    [
                                                        cf.Button(text="Reset Configurations", on_click=reset_config, icon=f.Icons.REFRESH),
                                                        cf.Button(text="Save Configurations", on_click=save_plugin_configs, icon=f.Icons.SAVE),
                                                    ],
                                                    spacing=20,
                                                    alignment=f.MainAxisAlignment.END,
                                                ),
                                            ]
                                        ),
                                    ),
                                ],
                                expand=True,
                                scrollable=True,
                                width=1000,
                                divider_color=t.theme.palette.divider,
                                label_color=t.theme.palette.text,
                                indicator_color=t.theme.palette.secondary,
                            ),
                        ],
                    ),
                    bgcolor=t.theme.palette.bg,
                    padding=20,
                    border_radius=f.border_radius.BorderRadius(10, 0, 0, 0),
                    width=450,
                    alignment=f.alignment.top_left,
                    expand=True,
                ),
            ],
            expand=True,
            spacing=0,
        ),
    )

    dnd_dialog = cf.Dialog(
        "Drag and Drop",
        "Drag and drop the plugin files here to install them",
        content=f.Image("assets/drag_and_drop.svg", width=400, height=400),
        alignment=f.alignment.center,
    )

    time.sleep(0.2)
    loaded_DLL = LoadDLL(
        page=page,
        on_dropped=handle_imports,
        on_entered=open_dnd_dialog,
        on_leaved=close_dnd_dialog,
    )


t = Themes()
pm = PluginManager()
f.app(lambda page: main(page, pm, t), assets_dir=ASSETS_DIR)
