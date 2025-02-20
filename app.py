import os
from pathlib import Path
import json
from typing import Callable

import flet as ft

from manager import *


# all_installed = False
# while not all_installed:
#     try:
#         pm = PluginManager("plugins")
#     except ModuleNotFoundError as e:
#         system("pip install " + str(e).split("'")[1])
#     else:
#         all_installed = True


class Palette:
    def __init__(self, palette: dict):
        self.bg = palette["bg"]
        self.bg_selection = palette["bg-selection"]
        self.bg_low = palette["bg-low"]
        self.bg_low_selection = palette["bg-low-selection"]
        self.bg_low_hover = palette["bg-low-hover"]
        self.bg_high = palette["bg-high"]
        self.bg_high_selection = palette["bg-high-selection"]
        self.bg_high_hover = palette["bg-high-hover"]
        self.primary = palette["primary"]
        self.secondary = palette["secondary"]
        self.tertiary = palette["tertiary"]
        self.text = palette["text"]
        self.text_muted = palette["text-muted"]
        self.divider = palette["divider"]
        self.divider_alt = palette["divider-alt"]


class Theme:
    def __init__(self, theme: dict):
        self.name = theme["name"]
        self.palette = Palette(theme["palette"])


class Themes:
    def __init__(self, path: Path = THEME_DIR):
        self.themes: list[Theme] = []
        self.load_themes(path)
        self.theme = self.themes[0]

    def load_themes(self, path: Path):
        for theme in os.listdir(path):
            if not theme.endswith(".json"):
                continue
            with open(path / theme, "r") as f:
                self.themes.append(Theme(json.load(f)))

    def select_theme(self, theme_name: str):
        for theme in self.themes:
            if theme.name == theme_name:
                self.theme = theme
                break


class cft:
    class Button(ft.Button):
        def __init__(self, text: str | None = None, content: ft.Control | None = None, on_click: Callable = None, icon: ft.Icon = None):
            super().__init__(
                style=ft.ButtonStyle(
                    bgcolor={
                        ft.ControlState.HOVERED: te.theme.palette.bg_high_hover,
                        ft.ControlState.DEFAULT: te.theme.palette.bg_high_selection,
                    },
                    padding=ft.Padding(10, 5, 10, 5),
                    shape=ft.RoundedRectangleBorder(radius=5),
                    elevation=0,
                    color=te.theme.palette.text,
                ),
                text=text,
                icon=icon,
                content=content,
                on_click=on_click,
                icon_color=te.theme.palette.text,
            )

    class Divider(ft.Divider):
        def __init__(self, alt=False, thickness=1):
            super().__init__(color=te.theme.palette.divider_alt if alt else te.theme.palette.divider, thickness=thickness)

    class Switch(ft.Switch):
        def __init__(self, value: bool | None = None, on_change: Callable | None = None, data: Any | None = None):
            super().__init__(
                value=value,
                inactive_track_color=te.theme.palette.bg,
                track_outline_color={
                    ft.ControlState.SELECTED: ft.Colors.TRANSPARENT,
                    ft.ControlState.DEFAULT: te.theme.palette.bg_high_hover,
                },
                thumb_color={
                    ft.ControlState.SELECTED: te.theme.palette.primary,
                    ft.ControlState.DEFAULT: te.theme.palette.bg_high_hover,
                },
                active_color=te.theme.palette.primary,
                data=data,
                on_change=on_change,
            )

    class TextField(ft.TextField):
        def __init__(self, label: str | None = None, value: str | None = None, multiline: bool = False, max_lines: int = 1, on_change: Callable | None = None, input_filter: ft.InputFilter | None = None):
            super().__init__(
                label=label,
                value=value,
                multiline=multiline,
                max_lines=max_lines,
                border_color=te.theme.palette.divider,
                on_change=on_change,
                cursor_color=te.theme.palette.primary,
                focused_border_color=te.theme.palette.primary,
                label_style=ft.TextStyle(color=te.theme.palette.text),
                input_filter=input_filter,
            )

    class Checkbox(ft.Checkbox):
        def __init__(self, label: str | None = None, value: bool = False):
            super().__init__(
                label=label,
                value=value,
                active_color=te.theme.palette.primary,
                check_color=ft.Colors.BLACK,
            )

    class Radio(ft.Radio):
        def __init__(self, label: str | None = None, value: str | None = None):
            super().__init__(
                label=label,
                value=value,
                active_color=te.theme.palette.primary,
            )

    class Text(ft.Text):
        class Size:
            LARGE = 20
            MEDIUM = 16
            SMALL = 14
            TINY = 12

        def __init__(self, text: str | None = None, overflow: ft.TextOverflow = None, dimmed=False, size: Size = Size.MEDIUM):
            super().__init__(value=text, size=size, color=te.theme.palette.text_muted if dimmed else te.theme.palette.text, overflow=overflow)

    class Dialog(ft.AlertDialog):
        def __init__(
            self,
            title: str | None = None,
            subtitle: str | None = None,
            content: ft.Control | None = None,
            actions: dict[str, Callable] | None = None,
            on_dismiss: Callable | None = None,
            get_callback: Callable | None = None,
        ):
            super().__init__(
                modal=True,
                title=ft.Column(
                    [
                        cft.Text(title, size=cft.Text.Size.LARGE),
                        cft.Text(subtitle, dimmed=True, size=cft.Text.Size.SMALL),
                    ],
                    spacing=5,
                ),
                content=content,
                actions=[
                    *[cft.Button(text, on_click=on_click if on_click else self.close_dialog) for text, on_click in actions.items()],
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                bgcolor=te.theme.palette.bg,
                shape=ft.RoundedRectangleBorder(radius=5),
                on_dismiss=on_dismiss,
            )
            self.get_callback = get_callback

        def show(self, page: ft.Page):
            page.open(self)

        def close_dialog(self, e: ft.ControlEvent):
            e.page.close(e.control.parent)
            self.get_callback(e.control.text) if self.get_callback else None


def main(page: ft.Page, pm: PluginManager, th: Themes):
    def generate_plugin(e: ft.ControlEvent):
        # check if key is valid and if not then do this:
        cft.Dialog(
            "Enter the key",
            "Enter the key to generate the plugin",
            cft.TextField(label="Key", multiline=False, max_lines=1),
            {
                "Generate": lambda e: print("Generate"),
                "Cancel": None,
            },
        ).show(page)

    def get_expansion_tiles_container():
        return ft.Column(
            controls=[
                ft.Container(
                    content=get_expansion_tiles(plugin),
                    padding=15,
                    bgcolor=th.theme.palette.bg,
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
            plugin_tile = ft.Button(
                content=ft.Row(
                    controls=[
                        ft.Image(item.icon_path, width=40, height=40, border_radius=10),
                        ft.Column(
                            [
                                cft.Text(item.name, overflow=ft.TextOverflow.ELLIPSIS, size=cft.Text.Size.SMALL),
                                cft.Text(item.description, overflow=ft.TextOverflow.ELLIPSIS, dimmed=True, size=cft.Text.Size.TINY),
                            ],
                            spacing=2,
                            alignment=ft.alignment.center_left,
                            expand=True,
                            scroll=ft.ScrollMode.ADAPTIVE,
                        ),
                        cft.Switch(value=item.enabled, on_change=toggle_plugin, data=item.id),
                    ],
                    height=60,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                style=ft.ButtonStyle(
                    bgcolor={
                        ft.ControlState.HOVERED: th.theme.palette.bg_selection,
                        ft.ControlState.FOCUSED: th.theme.palette.bg_selection,
                        ft.ControlState.DEFAULT: th.theme.palette.bg_selection if pm.selected_plugin.id == item.id else th.theme.palette.bg,
                    },
                    shape=ft.RoundedRectangleBorder(radius=5),
                    elevation=0,
                ),
                expand=True,
                on_click=change_plugin_page,
                data=item,
            )
            item.control = plugin_tile
            return plugin_tile

        menu_tile = ft.ExpansionTile(
            title=cft.Text(item.name, size=cft.Text.Size.SMALL),
            subtitle=cft.Text(item.description, dimmed=True, size=cft.Text.Size.TINY),
            leading=ft.Image(item.icon_path, width=40, height=40, border_radius=10),
            controls=[
                ft.Container(
                    ft.Column(
                        [get_expansion_tiles(sub_item) for sub_item in item.sub_items],
                        spacing=5,
                    ),
                    border=ft.Border(left=ft.BorderSide(color=th.theme.palette.divider, width=2)),
                    padding=ft.padding.Padding(15, 5, 0, 5),
                ),
            ],
            tile_padding=ft.padding.Padding(10, 5, 10, 5),
            shape=ft.RoundedRectangleBorder(radius=5),
            maintain_state=True,
            initially_expanded=True,
            icon_color=th.theme.palette.text,
        )
        item.control = menu_tile
        return menu_tile

    def change_plugin_page(e: ft.ControlEvent):
        pm.select_plugin(e.control.data.id)
        plugin_icon.src = pm.selected_plugin.icon_path
        plugin_title.value = pm.selected_plugin.name
        plugin_description.value = pm.selected_plugin.description
        plugin_markdown.value = open(pm.selected_plugin.markdown, "r", encoding="utf-8").read()
        plugin_configs.content = get_plugin_config()
        pm.previous_plugin.control.style.bgcolor[ft.ControlState.DEFAULT] = th.theme.palette.bg
        e.control.style.bgcolor[ft.ControlState.DEFAULT] = th.theme.palette.bg_selection
        page.update()

    def toggle_plugin(e: ft.ControlEvent):
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

    def toggle_all_plugins(e: ft.ControlEvent):
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
        config_column = ft.Column(
            controls=[
                cft.Text("Plugin Configurations", size=cft.Text.Size.LARGE),
                cft.Divider(),
                ft.Column(
                    controls=[
                        cft.Text("Change Plugin Type", size=cft.Text.Size.MEDIUM),
                        cft.Text("Only change the plugin type if you know what you are doing", dimmed=True, size=cft.Text.Size.SMALL),
                        control := ft.Column(
                            [cft.Checkbox(label=option, value=option in pm.selected_plugin.selected_types) for option in PLUGIN_TYPES],
                        ),
                    ],
                    spacing=15,
                ),
            ],
            spacing=15,
            scroll=ft.ScrollMode.ADAPTIVE,
        )

        pm.selected_plugin.types_control = control

        if not pm.selected_plugin.configs:
            return config_column
        for config in pm.selected_plugin.configs:
            config_column.controls.append(cft.Divider())
            container = ft.Column(spacing=15)
            container.controls.append(cft.Text(config["label"], size=cft.Text.Size.MEDIUM))
            container.controls.append(cft.Text(config["description"], dimmed=True, size=cft.Text.Size.SMALL))
            if config["type"] == "str":
                control = cft.TextField(label=config["label"], value=config["value"] if "value" in config else config["default"])
            elif config["type"] == "bool":
                control = cft.Switch(value=config["value"] if "value" in config else config["default"])

            elif config["type"] == "int":
                control = cft.TextField(label=config["label"], value=config["value"] if "value" in config else config["default"], input_filter=ft.NumbersOnlyInputFilter())

            elif config["type"] == "float":
                control = cft.TextField(label=config["label"], value=config["value"] if "value" in config else config["default"], input_filter=ft.InputFilter("^[0-9]*[.]?[0-9]*$"))

            elif config["type"] == "checkbox":
                control = ft.Column([cft.Checkbox(label=option, value=option in (config["value"] if "value" in config else config["default"])) for option in config["options"]])

            elif config["type"] == "radio":
                control = ft.RadioGroup(
                    content=ft.Column(
                        [cft.Radio(value=option, label=option) for option in config["options"]],
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

    def reset_config(e: ft.ControlEvent):
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

    def save_plugin_configs(e: ft.ControlEvent):
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
    page.theme = ft.Theme(font_family="Inter")
    page.padding = 0
    page.bgcolor = th.theme.palette.bg_low
    page.window_min_height = 610
    page.window_min_width = 713

    page.appbar = ft.AppBar(
        title=ft.Row(
            [
                cft.Text("Context Menu Plugin Manager", size=cft.Text.Size.LARGE),
                ft.Container(expand=True),
                cft.Button("Generate Plugin", icon=ft.Icons.BOLT, on_click=generate_plugin),
                cft.Button("Add Plugin", icon=ft.Icons.ADD),
                cft.Button("Open Plugins Folder", icon=ft.Icons.FOLDER, on_click=lambda e: os.system(f'explorer "{PLUGINS_DIR}"')),
                # ft.IconButton(ft.Icons.SETTINGS, tooltip="Settings", on_click=lambda e: print("Settings")),
            ],
            spacing=20,
        ),
        leading_width=70,
        automatically_imply_leading=True,
        bgcolor=th.theme.palette.bg_low,
        surface_tint_color=th.theme.palette.bg_low,
    )

    page.add(
        ft.Row(
            controls=[
                ft.Container(
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    cft.Text("Plugins", size=cft.Text.Size.MEDIUM),
                                    enable_disable_btn := cft.Button(text="Disable All" if pm.is_all_plugin_enabled() else "Enable All", on_click=toggle_all_plugins),
                                ],
                                height=80,
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Column(
                                [
                                    get_expansion_tiles_container(),
                                ],
                                scroll=ft.ScrollMode.ADAPTIVE,
                                expand=True,
                            ),
                        ],
                    ),
                    bgcolor=th.theme.palette.bg_low,
                    padding=ft.Padding(20, 0, 20, 20),
                    width=450,
                    alignment=ft.alignment.top_left,
                ),
                ft.Container(
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    plugin_icon := ft.Image(pm.selected_plugin.icon_path, width=130, height=130),
                                    ft.Column(
                                        [
                                            plugin_title := cft.Text(pm.selected_plugin.name, size=cft.Text.Size.MEDIUM),
                                            plugin_description := cft.Text(pm.selected_plugin.description, dimmed=True, size=cft.Text.Size.SMALL),
                                            ft.Row(
                                                [
                                                    # Component.Button("Uninstall"),
                                                    cft.Button(text="View in Explorer", on_click=lambda e: os.system(f'explorer "{pm.selected_plugin.path}"')),
                                                    cft.Button(text="Edit in VSCode", on_click=lambda e: os.system(f'code "{pm.selected_plugin.path}"')),
                                                ],
                                            ),
                                        ],
                                        spacing=10,
                                    ),
                                ],
                            ),
                            ft.Tabs(
                                selected_index=0,
                                animation_duration=300,
                                tabs=[
                                    ft.Tab(
                                        text="Description",
                                        content=ft.Container(
                                            ft.Column(
                                                [
                                                    plugin_markdown := ft.Markdown(
                                                        open(pm.selected_plugin.markdown, "r", encoding="utf-8").read(),
                                                        code_theme=ft.MarkdownCodeTheme.DRAGULA,
                                                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                                                    ),
                                                ],
                                                expand=True,
                                                scroll=ft.ScrollMode.ADAPTIVE,
                                            ),
                                            padding=20,
                                        ),
                                    ),
                                    ft.Tab(
                                        "Configure Plugin",
                                        content=ft.Column(
                                            [
                                                plugin_configs := ft.Container(
                                                    get_plugin_config(),
                                                    padding=ft.Padding(20, 20, 20, 0),
                                                    expand=True,
                                                ),
                                                cft.Divider(alt=True, thickness=2),
                                                ft.Row(
                                                    [
                                                        cft.Button(text="Reset Configurations", on_click=reset_config, icon=ft.Icons.REFRESH),
                                                        cft.Button(text="Save Configurations", on_click=save_plugin_configs, icon=ft.Icons.SAVE),
                                                    ],
                                                    spacing=20,
                                                    alignment=ft.MainAxisAlignment.END,
                                                ),
                                            ]
                                        ),
                                    ),
                                ],
                                expand=True,
                                scrollable=True,
                                width=1000,
                                divider_color=th.theme.palette.divider,
                                label_color=th.theme.palette.text,
                                indicator_color=th.theme.palette.secondary,
                            ),
                        ],
                    ),
                    bgcolor=th.theme.palette.bg,
                    padding=20,
                    border_radius=ft.border_radius.BorderRadius(10, 0, 0, 0),
                    width=450,
                    alignment=ft.alignment.top_left,
                    expand=True,
                ),
            ],
            expand=True,
            spacing=0,
        ),
    )


te = Themes()
pm = PluginManager()
ft.app(lambda page: main(page, pm, te), assets_dir=ASSETS_DIR)
