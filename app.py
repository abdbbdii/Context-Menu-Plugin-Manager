import os

import flet as ft

from manager import *


pm = PluginManager("plugins")
# all_installed = False
# while not all_installed:
#     try:
#         pm = PluginManager("plugins")
#     except ModuleNotFoundError as e:
#         system("pip install " + str(e).split("'")[1])
#     else:
#         all_installed = True


class Colors:
    PRIMARY_CLR = "#468189"
    SECONDARY_CLR = "#c9bfa5"
    LIGHTPRIMARY_CLR = "#468189"
    BACKGROUND0_CLR = "#031926"
    BACKGROUND1_CLR = "#042131"
    BACKGROUND2_CLR = "#052a3f"
    BACKGROUND3_CLR = "#052d44"
    BACKGROUND4_CLR = "#06334d"
    DISABLED_CLR = "#acacac"
    TEXT_CLR = "#ffffff"


class Component:
    def button(text, on_click):
        return ft.FilledButton(
            text=text,
            on_click=on_click,
            style=ft.ButtonStyle(bgcolor=Colors.PRIMARY_CLR, color=Colors.TEXT_CLR, padding=ft.padding.Padding(10, 5, 10, 5), shape=ft.RoundedRectangleBorder(radius=5)),
            height=30,
        )

    def dlg_ask_input_btn(title, content, options: dict, show_input_field=False, max_lines=1):
        return ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=(
                ft.TextField(
                    label=content,
                    multiline=True,
                    max_lines=max_lines,
                    border_color=Colors.LIGHTPRIMARY_CLR,
                    border_width=2,
                    autofocus=True,
                    width=500,
                )
                if show_input_field
                else ft.Text(content)
            ),
            actions=[
                *[ft.TextButton(text, on_click=on_click, style=ft.ButtonStyle(color=Colors.TEXT_CLR)) for text, on_click in options.items()],
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=Colors.BACKGROUND1_CLR,
            open=True,
            shape=ft.RoundedRectangleBorder(radius=10),
        )


def main(page: ft.Page):
    def get_expansion_tiles_container():
        return ft.Column(
            controls=[
                ft.Container(
                    content=get_expansion_tiles(plugin),
                    padding=15,
                    bgcolor=Colors.BACKGROUND2_CLR,
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
            plugin_tile = ft.CupertinoButton(
                content=ft.Row(
                    controls=[
                        ft.Image(item.icon_path, width=40, height=40, border_radius=10),
                        ft.Column(
                            [
                                ft.Text(item.name, size=16, color=Colors.TEXT_CLR, overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Text(item.description, size=14, color=Colors.DISABLED_CLR, overflow=ft.TextOverflow.ELLIPSIS),
                            ],
                            spacing=2,
                            alignment=ft.alignment.center_left,
                            expand=True,
                            scroll=ft.ScrollMode.ADAPTIVE,
                        ),
                        ft.Switch(value=item.enabled, inactive_track_color=Colors.BACKGROUND2_CLR, track_outline_color=Colors.PRIMARY_CLR, thumb_color=Colors.PRIMARY_CLR, active_color=Colors.PRIMARY_CLR, data=item.id, on_change=toggle_plugin),
                    ],
                    height=60,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                bgcolor=Colors.BACKGROUND4_CLR if pm.selected_plugin.id == item.id else None,
                border_radius=5,
                padding=ft.padding.Padding(10, 5, 10, 5),
                expand=True,
                alignment=ft.alignment.center_left,
                on_click=change_plugin_page,
                data=item,
            )
            item.control = plugin_tile
            return plugin_tile

        menu_tile = ft.ExpansionTile(
            title=ft.Text(item.name, size=20),
            subtitle=ft.Text(item.description, size=14, color=Colors.DISABLED_CLR),
            leading=ft.Image(item.icon_path, width=40, height=40, border_radius=10),
            controls=[
                ft.Container(
                    ft.Column(
                        [get_expansion_tiles(sub_item) for sub_item in item.sub_items],
                        spacing=5,
                    ),
                    border=ft.Border(left=ft.BorderSide(color=Colors.BACKGROUND4_CLR, width=2)),
                    padding=ft.padding.Padding(15, 5, 0, 5),
                ),
            ],
            tile_padding=ft.padding.Padding(10, 5, 10, 5),
            shape=ft.RoundedRectangleBorder(radius=5),
            maintain_state=True,
            initially_expanded=True,
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
        pm.previous_plugin.control.bgcolor = None
        pm.selected_plugin.control.bgcolor = Colors.BACKGROUND4_CLR
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
                ft.Text("Plugin Configurations", size=18, color=Colors.TEXT_CLR, weight=ft.FontWeight.W_600),
                ft.Divider(color=Colors.BACKGROUND2_CLR),
                ft.Column(
                    controls=[
                        ft.Text(
                            "Change Plugin Type",
                            size=16,
                            color=Colors.TEXT_CLR,
                        ),
                        ft.Text(
                            "Only change the plugin type if you know what you are doing",
                            size=14,
                            color=Colors.DISABLED_CLR,
                        ),
                        control := ft.Column(
                            [ft.Checkbox(label=option, value=option in pm.selected_plugin.selected_types, active_color=Colors.LIGHTPRIMARY_CLR) for option in plugin_types],
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
            config_column.controls.append(ft.Divider(color=Colors.BACKGROUND2_CLR))
            container = ft.Column(
                spacing=15,
            )
            container.controls.append(ft.Text(config["label"], size=16, color=Colors.TEXT_CLR))
            container.controls.append(ft.Text(config["description"], size=14, color=Colors.DISABLED_CLR))
            if config["type"] == "str":
                control = ft.TextField(
                    label=config["label"],
                    value=config["value"] if "value" in config else config["default"],
                    border_color=Colors.LIGHTPRIMARY_CLR,
                    multiline=False,
                    max_lines=1,
                    cursor_color=Colors.LIGHTPRIMARY_CLR,
                )

            elif config["type"] == "bool":
                control = ft.Switch(
                    value=config["value"] if "value" in config else config["default"],
                    inactive_track_color=Colors.BACKGROUND2_CLR,
                    track_outline_color=Colors.PRIMARY_CLR,
                    thumb_color=Colors.PRIMARY_CLR,
                    active_color=Colors.PRIMARY_CLR,
                )

            elif config["type"] == "int":
                control = ft.TextField(
                    label=config["label"],
                    value=config["value"] if "value" in config else config["default"],
                    border_color=Colors.LIGHTPRIMARY_CLR,
                    input_filter=ft.NumbersOnlyInputFilter(),
                    multiline=False,
                    max_lines=1,
                )

            elif config["type"] == "float":
                control = ft.TextField(
                    label=config["label"],
                    value=config["value"] if "value" in config else config["default"],
                    border_color=Colors.LIGHTPRIMARY_CLR,
                    input_filter=ft.InputFilter("^[0-9]*[.]?[0-9]*$"),
                    multiline=False,
                    max_lines=1,
                )

            elif config["type"] == "checkbox":
                control = ft.Column(
                    [ft.Checkbox(label=option, value=option in (config["value"] if "value" in config else config["default"]), active_color=Colors.LIGHTPRIMARY_CLR) for option in config["options"]],
                )

            elif config["type"] == "radio":
                control = ft.RadioGroup(
                    content=ft.Column(
                        [ft.Radio(value=option, label=option, fill_color=Colors.LIGHTPRIMARY_CLR) for option in config["options"]],
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
    page.bgcolor = Colors.BACKGROUND1_CLR
    page.window_min_height = 610
    page.window_min_width = 713

    page.appbar = ft.AppBar(
        title=ft.Row(
            [
                ft.Text("Context Menu Plugin Manager", size=20, weight=ft.FontWeight.W_600, color=Colors.TEXT_CLR),
                ft.Container(expand=True),
                ft.Button("Generate Plugin", icon=ft.Icons.BOLT),
                ft.Button("Add Plugin", icon=ft.Icons.ADD),
                ft.Button("Open Plugins Folder", icon=ft.Icons.FOLDER, on_click=lambda e: os.system(f'explorer "{PLUGINS_DIR}"')),
                # ft.IconButton(ft.Icons.SETTINGS, tooltip="Settings", on_click=lambda e: print("Settings")),
            ],
            spacing=20,
        ),
        leading_width=70,
        automatically_imply_leading=True,
        bgcolor=Colors.BACKGROUND1_CLR,
        surface_tint_color=Colors.BACKGROUND1_CLR,
    )

    page.add(
        ft.Row(
            controls=[
                ft.Container(
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text("Plugins", size=18, weight=ft.FontWeight.W_600),
                                    enable_disable_btn := Component.button("Disable All" if pm.is_all_plugin_enabled() else "Enable All", toggle_all_plugins),
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
                    bgcolor=Colors.BACKGROUND1_CLR,
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
                                            plugin_title := ft.Text(pm.selected_plugin.name, size=20),
                                            plugin_description := ft.Text(pm.selected_plugin.description, size=14, color=Colors.DISABLED_CLR),
                                            ft.Row(
                                                [
                                                    # Component.Button("Uninstall"),
                                                    Component.button("View in Explorer", lambda e: os.system(f'explorer "{pm.selected_plugin.path}"')),
                                                    Component.button("Edit in VSCode", lambda e: os.system(f'code "{pm.selected_plugin.path}"')),
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
                                                        code_theme=ft.MarkdownCodeTheme.SOLARIZED_DARK,
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
                                                ft.Divider(color=Colors.BACKGROUND2_CLR),
                                                ft.Row(
                                                    [
                                                        Component.button("Save Configurations", save_plugin_configs),
                                                        Component.button("Reset Configurations", reset_config),
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
                                divider_color=Colors.BACKGROUND2_CLR,
                                label_color=Colors.TEXT_CLR,
                                indicator_color=Colors.PRIMARY_CLR,
                            ),
                        ],
                    ),
                    bgcolor=Colors.BACKGROUND0_CLR,
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


ft.app(main, assets_dir="assets")
