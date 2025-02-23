import os
import time
from typing import Callable
import shutil
import time

import flet as f

from PluginManager import *
from DropZone import LoadDLL
from AI import AI

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
        def __init__(self, text: str | None = None, content: f.Control | None = None, on_click: Callable = None, icon: f.Icon = None, data: Any | None = None):
            super().__init__(
                style=f.ButtonStyle(
                    bgcolor={
                        f.ControlState.HOVERED: pm.themes.current.palette.bg_high_hover,
                        f.ControlState.DEFAULT: pm.themes.current.palette.bg_high_selection,
                    },
                    padding=f.Padding(10, 5, 10, 5),
                    shape=f.RoundedRectangleBorder(radius=5),
                    elevation=0,
                    color=pm.themes.current.palette.text,
                ),
                text=text,
                icon=icon,
                content=content,
                on_click=on_click,
                icon_color=pm.themes.current.palette.text,
                data=data,
            )

    class VerticalButton(f.Button):
        def __init__(self, text: str | None = None, content: f.Control | None = None, on_click: Callable = None, icon: f.Icon = None, data: Any | None = None):
            if not content:
                content = f.Column(
                    [
                        f.Container(
                            f.Icon(icon, color=pm.themes.current.palette.text, size=50),
                            alignment=f.alignment.center,
                        ),
                        f.Container(
                            cf.Text(text, size=cf.Text.Size.MEDIUM),
                            alignment=f.alignment.center,
                        ),
                    ],
                    spacing=5,
                    alignment=f.alignment.center,
                )
            super().__init__(
                style=f.ButtonStyle(
                    bgcolor={
                        f.ControlState.HOVERED: pm.themes.current.palette.bg_high_hover,
                        f.ControlState.DEFAULT: pm.themes.current.palette.bg_high_selection,
                    },
                    padding=20,
                    shape=f.RoundedRectangleBorder(radius=5),
                    elevation=0,
                    color=pm.themes.current.palette.text,
                ),
                content=content,
                width=200,
                on_click=on_click,
                data=data,
            )

    class IconButton(f.IconButton):
        def __init__(self, icon: f.Icon, on_click: Callable, tooltip: str | None = None):
            super().__init__(
                icon=icon,
                icon_color=pm.themes.current.palette.text,
                on_click=on_click,
                tooltip=tooltip,
            )

    class Divider(f.Divider):
        def __init__(self, alt=False, thickness=1):
            super().__init__(color=pm.themes.current.palette.divider_alt if alt else pm.themes.current.palette.divider, thickness=thickness)

    class Switch(f.Switch):
        def __init__(self, value: bool | None = None, on_change: Callable | None = None, data: Any | None = None):
            super().__init__(
                value=value,
                inactive_track_color=pm.themes.current.palette.bg,
                track_outline_color={
                    f.ControlState.SELECTED: f.Colors.TRANSPARENT,
                    f.ControlState.DEFAULT: pm.themes.current.palette.bg_high_hover,
                },
                thumb_color={
                    f.ControlState.SELECTED: pm.themes.current.palette.primary,
                    f.ControlState.DEFAULT: pm.themes.current.palette.bg_high_hover,
                },
                active_color=pm.themes.current.palette.primary,
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
                border_color=pm.themes.current.palette.divider,
                on_change=on_change,
                cursor_color=pm.themes.current.palette.primary,
                focused_border_color=pm.themes.current.palette.primary,
                label_style=f.TextStyle(color=pm.themes.current.palette.text),
                input_filter=input_filter,
            )

    class Checkbox(f.Checkbox):
        def __init__(self, label: str | None = None, value: bool = False):
            super().__init__(
                label=label,
                value=value,
                active_color=pm.themes.current.palette.primary,
                check_color=f.Colors.BLACK,
            )

    class Radio(f.Radio):
        def __init__(self, label: str | None = None, value: str | None = None):
            super().__init__(
                label=label,
                value=value,
                active_color=pm.themes.current.palette.primary,
            )

    class Text(f.Text):
        class Size:
            LARGE = 20
            MEDIUM = 16
            SMALL = 14
            TINY = 12

        def __init__(self, text: str | None = None, overflow: f.TextOverflow = None, dimmed=False, size: Size = Size.MEDIUM, text_align: f.TextAlign = f.TextAlign.LEFT):
            super().__init__(
                value=text,
                size=size,
                color=pm.themes.current.palette.text_muted if dimmed else pm.themes.current.palette.text,
                overflow=overflow,
                text_align=text_align,
            )

    class ShowSnackBar(f.SnackBar):
        def __init__(self, text: str, page: f.Page, color: str | None = None):
            super().__init__(
                content=cf.Text(text, size=cf.Text.Size.MEDIUM),
                duration=2000,
                bgcolor=color if color else pm.themes.current.palette.info,
            )
            page.open(self)

    class Dialog(f.AlertDialog):
        def __init__(self, title: str | None = None, subtitle: str | None = None, content: f.Control | None = None, actions: dict[str, Callable] = {}, on_dismiss: Callable | None = None, get_callback: Callable | None = None, alignment: f.Alignment | None = None):
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
                bgcolor=pm.themes.current.palette.bg,
                shape=f.RoundedRectangleBorder(radius=5),
                on_dismiss=on_dismiss,
                alignment=alignment,
            )
            self.get_callback = get_callback
            for text, on_click in actions.items():
                self.actions.append(
                    cf.Button(
                        text,
                        data=on_click,
                        on_click=self.closing_wrapper,
                    ),
                )

        def show(self, page: f.Page):
            page.open(self)

        def closing_wrapper(self, e: f.ControlEvent):
            if e.page.dialog if hasattr(e.page, "dialog") else False:
                del e.page.dialog
            e.page.close(e.control.parent)
            self.get_callback(e.control.text) if self.get_callback else None
            if isinstance(e.control.data, Callable):
                e.control.data(e)

    @staticmethod
    def show_loading(page: f.Page):
        pm.active_loading_control = f.Container(
            f.Column(
                [
                    f.Container(
                        f.Row(
                            [
                                f.ProgressRing(),
                            ],
                            expand=True,
                            alignment=f.MainAxisAlignment.CENTER,
                        ),
                        alignment=f.alignment.center,
                        expand=True,
                    ),
                ],
                expand=True,
                alignment=f.MainAxisAlignment.CENTER,
            ),
            expand=True,
            alignment=f.alignment.center,
            opacity=0.5,
            bgcolor=f.Colors.BLACK,
        )
        page.overlay.append(pm.active_loading_control)

        page.update()

    @staticmethod
    def hide_loading():
        pm.active_loading_control.page.overlay.remove(pm.active_loading_control)
        pm.active_loading_control.page.update()

    @staticmethod
    def load_for(seconds: float, page: f.Page):
        cf.show_loading(page)
        time.sleep(seconds)
        cf.hide_loading()


def main(page: f.Page, pm: PluginManager):
    def change_theme(e: f.ControlEvent):
        def handle_change_theme(theme: str):
            pm.themes.set_theme(theme)
            pm.save_session()
            make_page()
            page.update()
            cf.ShowSnackBar("The theme has been changed successfully", page)

        cf.Dialog(
            "Change Theme",
            "Select the theme to change to",
            f.Column(
                [
                    cf.Text("Select the theme to change to", size=cf.Text.Size.MEDIUM),
                    theme := f.RadioGroup(
                        f.Column(
                            [cf.Radio(value=name, label=name) for name in pm.themes.get_themes()],
                        ),
                        value=pm.themes.current.name,
                    ),
                ],
                spacing=20,
                height=200,
            ),
            actions={
                "Change": lambda e: handle_change_theme(theme.value),
                "Cancel": None,
            },
        ).show(page)

    def force_remove_plugin(e: f.ControlEvent):
        def handle_force_remove_plugin(name: str, types: list[str]):
            for type in types:
                print(name, type)
                pm.remove_menu_by_name(name, type)
            cf.ShowSnackBar("The plugin has been removed successfully", page)

        cf.Dialog(
            "Remove Plugin",
            "You are about to remove any entry that matches the name and types of the plugin. This action cannot be undone.",
            f.Column(
                [
                    f.Column(
                        [
                            cf.Text("Enter the name of the plugin to remove", size=cf.Text.Size.MEDIUM),
                            name := cf.TextField(label="Name", multiline=False, max_lines=1),
                        ],
                        spacing=15,
                    ),
                    f.Column(
                        [
                            cf.Text("Select the types of the plugin to remove", size=cf.Text.Size.MEDIUM),
                            checkboxes := f.Column(
                                [cf.Checkbox(label=type, value=False) for type in PLUGIN_TYPES],
                            ),
                        ],
                        spacing=15,
                    ),
                ],
                spacing=20,
                height=300,
            ),
            actions={
                "Remove": lambda e: handle_force_remove_plugin(name.value, [control.label for control in checkboxes.controls if control.value]),
                "Cancel": None,
            },
        ).show(page)

    def uninstall_plugin(e: f.ControlEvent):
        def handle_uninstall_plugin(e: f.ControlEvent):
            cf.show_loading(page)
            pm.uninstall_plugin()
            refresh_page()
            cf.hide_loading()
            cf.ShowSnackBar("The plugin has been uninstalled successfully", page)

        cf.Dialog(
            "Uninstall Plugin",
            "Are you sure you want to uninstall the plugin?",
            actions={
                "Yes": handle_uninstall_plugin,
                "No": None,
            },
        ).show(page)

    def load_plugins(files: list[Path] | None):
        any_loaded = False
        if not files:
            return any_loaded
        for file in files:
            if not isinstance(file, str):
                file = file.path

            file = Path(file).resolve()
            if file.name.endswith(".zip"):
                shutil.unpack_archive(file, TEMP_DIR)
                if not PluginManager.check_path(TEMP_DIR):
                    fs.empty_dir(TEMP_DIR)
                    continue
                try:
                    fs.move_contents(TEMP_DIR, PLUGINS_DIR)
                    fs.empty_dir(TEMP_DIR)
                except Exception as e:
                    print(e)
                    fs.empty_dir(TEMP_DIR)
                    continue
                any_loaded = True

            elif file.is_dir():
                if not PluginManager.check_path(file):
                    continue
                try:
                    shutil.copytree(file, PLUGINS_DIR / file.name)
                except Exception as e:
                    print(e)
                    continue
                any_loaded = True
        return any_loaded

    def handle_imports(files: list[Path] | None):
        if page.dialog if hasattr(page, "dialog") else False:
            close_dialog()

        if load_plugins(files):
            refresh_page()
            cf.ShowSnackBar("The plugins have been installed successfully", page)
        else:
            cf.ShowSnackBar("No valid plugins were found", page, pm.themes.current.palette.error)

    def open_dnd_dialog(e: f.ControlEvent):
        if page.dialog if hasattr(page, "dialog") else False:
            return
        page.dnd_dialog = cf.Dialog(
            "Drag and Drop",
            "Drag and drop the plugin files here to install them",
            content=f.Image(ASSETS_DIR / "drag_and_drop.svg", width=400, height=400),
            alignment=f.alignment.center,
        )
        page.dnd_dialog.show(page)
        page.update()

    def close_dialog(e: f.ControlEvent | None = None):
        if page.dialog if hasattr(page, "dialog") else False:
            return
        try:
            page.close(page.dnd_dialog)
        except:
            pass
        page.update()

    def generate_plugin_btn(e: f.ControlEvent, key: str = "", prompt: str = ""):
        if key:
            pm.ai_client.set_api_key(key)
            pm.save_session()

        cf.show_loading(page)
        check_validation = pm.ai_client.is_key_valid()
        cf.hide_loading()

        if not check_validation and key:
            cf.ShowSnackBar("The key is invalid. Please enter a valid Gemeni API key.", page, pm.themes.current.palette.error)

        if not check_validation:
            cf.Dialog(
                "Enter the key" if not key else "Invalid Key",
                "Enter the Gemeni API key to generate the plugin" if not key else "The key is invalid. Please enter a valid Gemeni API key.",
                text_feild := cf.TextField(label="Key", multiline=False, max_lines=1, value=pm.ai_client.get_api_key()),
                actions={
                    "Get a Gemini API Key": lambda e: os.system("start https://ai.google.dev/gemini-api/docs"),
                    "Next": lambda e: generate_plugin_btn(e, text_feild.value),
                    "Cancel": None,
                },
            ).show(page)
            return

        def handle_plugin_generation(e, prompt):
            if not prompt:
                generate_plugin_btn(e)
            cf.show_loading(page)
            result = pm.generate_plugin(prompt)
            cf.hide_loading()
            if result:
                refresh_page()
                cf.ShowSnackBar("The plugin has been generated successfully", page)
            else:
                cf.ShowSnackBar("An error occurred while generating the plugin", page, pm.themes.current.palette.error)
                cf.Dialog(
                    "Plugin Generation Failed",
                    "An error occurred while generating the plugin",
                    actions={
                        "Try Again": lambda e: generate_plugin_btn(e, prompt=prompt),
                        "Cancel": None,
                    },
                ).show(page)

        cf.Dialog(
            "Generate Plugin",
            "Enter the prompt to generate the plugin",
            text_feild := cf.TextField(label="Prompt", multiline=True, max_lines=10, value=prompt if prompt else "Plugin to manage my files"),
            actions={
                "Generate": lambda e: handle_plugin_generation(e, text_feild.value),
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

    def make_plugin(e: f.ControlEvent):
        def handle_make_plugin(e: f.ControlEvent, name: str):
            name = name.strip()
            if not name or name == PLUGIN_TEMPLATE.name:
                cf.ShowSnackBar("The name cannot be empty or the same as the template plugin", page, pm.themes.current.palette.error)
                return
            shutil.copytree(PLUGIN_TEMPLATE, TEMP_DIR / name)
            fs.move_contents(TEMP_DIR, PLUGINS_DIR)
            refresh_page()
            cf.ShowSnackBar("The plugin has been made successfully", page)
            cf.Dialog(
                "Plugin Made",
                "The plugin has been made successfully",
                actions={
                    "Ok": None,
                    "Open in VSCode": lambda e: (os.system(f'code "{PLUGINS_DIR / name}"'), cf.load_for(0.5, page)),
                },
            ).show(page)

        cf.Dialog(
            "Make Plugin",
            "Enter the name of the plugin to make",
            text_feild := cf.TextField(label="Name", multiline=False, max_lines=1),
            actions={
                "Make": lambda e: handle_make_plugin(e, text_feild.value),
                "Cancel": None,
            },
        ).show(page)

    def add_plugin_dialog(e: f.ControlEvent):
        dialog = cf.Dialog(
            "Add Plugin",
            "Select the plugin file to install",
            f.Container(
                f.Column(
                    [
                        f.Image(str(ASSETS_DIR / "drag_and_drop.svg"), width=400, height=400),
                        f.Row(
                            [
                                cf.VerticalButton("Select File", on_click=add_plugin, icon=f.Icons.ADD),
                                cf.VerticalButton("Generate Plugin", on_click=generate_plugin_btn, icon=f.Icons.BOLT),
                                cf.VerticalButton("Create New Plugin", on_click=make_plugin, icon=f.Icons.BUILD),
                            ],
                            alignment=f.MainAxisAlignment.SPACE_BETWEEN,
                            spacing=20,
                        ),
                    ],
                    alignment=f.MainAxisAlignment.SPACE_AROUND,
                    spacing=20,
                ),
                height=550,
            ),
            actions={
                "Cancel": None,
            },
        )
        page.dialog = dialog
        page.dialog.show(page)

    def make_page():
        if page.controls:
            page.controls.pop()
            page.controls.pop()

        page.add(
            # f.Column([
            f.Container(
                f.Row(
                    [
                        cf.Text("Context Menu Plugin Manager", size=cf.Text.Size.LARGE),
                        f.Container(expand=True),
                        cf.Button("Generate Plugin", icon=f.Icons.BOLT, on_click=generate_plugin_btn),
                        cf.Button("Add Plugin", icon=f.Icons.ADD, on_click=add_plugin_dialog),
                        f.PopupMenuButton(
                            items=[
                                # icon=f.Icons.FOLDER
                                # icon=f.Icons.DELETE
                                # icon=f.Icons.PALETTE
                                f.PopupMenuItem(text="Open Plugins Folder", on_click=lambda e: (cf.show_loading(page), os.system(f'explorer "{PLUGINS_DIR}"'), cf.hide_loading())),
                                f.PopupMenuItem(text="Force Remove Plugin", on_click=force_remove_plugin),
                                f.PopupMenuItem(text="Change Theme", on_click=change_theme),
                            ],
                            bgcolor=pm.themes.current.palette.bg_high_selection,
                            menu_position=f.PopupMenuPosition.UNDER,
                            icon_color=pm.themes.current.palette.text,
                        ),
                    ],
                    spacing=10,
                ),
                bgcolor=pm.themes.current.palette.bg_low,
                padding=f.Padding(20, 5, 20, 5),
            ),
            f.Row(
                controls=[
                    get_expansion_tiles(),
                    get_plugin_page(),
                ],
                expand=True,
                spacing=0,
            ),
        )

    def refresh_page(e: f.ControlEvent | None = None, snackbar=False, load_plugins=False):
        # cf.show_loading(page)
        pm.reload_plugins()
        make_page()
        page.bgcolor = pm.themes.current.palette.bg_low
        page.update()
        # cf.hide_loading()
        if snackbar:
            cf.ShowSnackBar("The plugins have been refreshed successfully", page)

    def get_expansion_tiles():
        if not pm.items:
            return f.Container(
                cf.Text(
                    "No plugins found. Add a plugin to get started",
                    dimmed=True,
                    size=cf.Text.Size.SMALL,
                ),
                bgcolor=pm.themes.current.palette.bg_low,
                padding=f.Padding(20, 0, 20, 20),
                width=450,
                alignment=f.alignment.center,
            )

        container = f.Container(
            f.Column(
                [
                    f.Row(
                        [
                            cf.Text("Plugins", size=cf.Text.Size.MEDIUM),
                            f.Row(
                                [
                                    cf.IconButton(f.Icons.REFRESH, tooltip="Refresh", on_click=lambda e: refresh_page(e, True)),
                                    enable_disable_btn := cf.Button(text="Disable All" if pm.is_all_plugin_enabled() else "Enable All", on_click=toggle_all_plugins),
                                ],
                            ),
                        ],
                        height=80,
                        alignment=f.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    f.Column(
                        [
                            f.Column(
                                controls=[
                                    f.Container(
                                        content=__get_expansion_tiles(plugin),
                                        padding=15,
                                        bgcolor=pm.themes.current.palette.bg,
                                        border_radius=5,
                                    )
                                    for plugin in pm.items
                                ],
                                scroll=True,
                                spacing=10,
                            ),
                        ],
                        scroll=f.ScrollMode.ADAPTIVE,
                        expand=True,
                    ),
                ],
            ),
            bgcolor=pm.themes.current.palette.bg_low,
            padding=f.Padding(20, 0, 20, 20),
            width=450,
            alignment=f.alignment.top_left,
        )
        pm.controls.enable_disable_btn = enable_disable_btn
        return container

    def __get_expansion_tiles(item: Menu | Plugin):
        if not (isinstance(item, Menu) or isinstance(item, Plugin)):
            return
        if isinstance(item, Plugin):
            item.controls.tile = f.Button(
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
                        f.ControlState.HOVERED: pm.themes.current.palette.bg_selection,
                        f.ControlState.FOCUSED: pm.themes.current.palette.bg_selection,
                        f.ControlState.DEFAULT: pm.themes.current.palette.bg_selection if pm.selected_plugin.id == item.id else pm.themes.current.palette.bg,
                    },
                    shape=f.RoundedRectangleBorder(radius=5),
                    elevation=0,
                ),
                expand=True,
                on_click=change_plugin_page,
                data=item,
            )
            return item.controls.tile

        item.controls.tile = f.ExpansionTile(
            title=cf.Text(item.name, size=cf.Text.Size.SMALL),
            subtitle=cf.Text(item.description, dimmed=True, size=cf.Text.Size.TINY),
            leading=f.Image(item.icon_path, width=40, height=40, border_radius=10),
            controls=[
                f.Container(
                    f.Column(
                        [__get_expansion_tiles(sub_item) for sub_item in item.sub_items],
                        spacing=5,
                    ),
                    border=f.Border(left=f.BorderSide(color=pm.themes.current.palette.divider, width=2)),
                    padding=f.padding.Padding(15, 5, 0, 5),
                ),
            ],
            tile_padding=f.padding.Padding(10, 5, 10, 5),
            shape=f.RoundedRectangleBorder(radius=5),
            maintain_state=True,
            initially_expanded=True,
            icon_color=pm.themes.current.palette.text,
        )
        return item.controls.tile

    def get_plugin_page():
        if not pm.selected_plugin:
            return f.Container(
                cf.Text("Click on the plugin to view its details", dimmed=True, size=cf.Text.Size.SMALL),
                bgcolor=pm.themes.current.palette.bg,
                padding=20,
                border_radius=f.border_radius.BorderRadius(10, 0, 0, 0),
                width=450,
                alignment=f.alignment.center,
                expand=True,
            )

        container = f.Container(
            f.Column(
                [
                    f.Row(
                        [
                            plugin_icon := f.Image(pm.selected_plugin.icon_path, width=130, height=130),
                            f.Column(
                                [
                                    plugin_name := cf.Text(pm.selected_plugin.name, size=cf.Text.Size.MEDIUM),
                                    plugin_description := cf.Text(pm.selected_plugin.description, dimmed=True, size=cf.Text.Size.SMALL),
                                    f.Row(
                                        [
                                            # Component.Button("Uninstall"),
                                            cf.Button(text="View in Explorer", on_click=lambda e: (cf.show_loading(page), os.system(f'explorer "{pm.selected_plugin.path}"'), cf.hide_loading())),
                                            cf.Button(text="Open in VSCode", on_click=lambda e: (cf.show_loading(page), os.system(f'code "{pm.selected_plugin.path}"'), cf.hide_loading())),
                                            cf.Button(text="Uninstall Plugin", on_click=uninstall_plugin),
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
                                                cf.Button(text="Reset Configurations", on_click=reset_plugin_configs, icon=f.Icons.REFRESH),
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
                        divider_color=pm.themes.current.palette.divider,
                        label_color=pm.themes.current.palette.text,
                        indicator_color=pm.themes.current.palette.secondary,
                    ),
                ],
            ),
            bgcolor=pm.themes.current.palette.bg,
            padding=20,
            border_radius=f.border_radius.BorderRadius(10, 0, 0, 0),
            width=450,
            alignment=f.alignment.top_left,
            expand=True,
        )
        pm.controls.icon = plugin_icon
        pm.controls.name = plugin_name
        pm.controls.description = plugin_description
        pm.controls.markdown = plugin_markdown
        pm.controls.configs = plugin_configs
        return container

    def change_plugin_page(e: f.ControlEvent):
        pm.select_plugin(e.control.data.id)
        if not pm.previous_plugin:
            page.controls[0].controls[1] = get_plugin_page()
        else:
            pm.controls.icon.src = pm.selected_plugin.icon_path
            pm.controls.name.value = pm.selected_plugin.name
            pm.controls.description.value = pm.selected_plugin.description
            pm.controls.markdown.value = open(pm.selected_plugin.markdown, "r", encoding="utf-8").read()
            pm.controls.configs.content = get_plugin_config()
            pm.previous_plugin.controls.tile.style.bgcolor[f.ControlState.DEFAULT] = pm.themes.current.palette.bg
            pm.selected_plugin.controls.tile.style.bgcolor[f.ControlState.DEFAULT] = pm.themes.current.palette.bg_selection
        page.update()

    def toggle_plugin(e: f.ControlEvent):
        pm.set_attr(e.control.data, "enabled", e.control.value)
        if pm.is_all_plugin_disabled():
            pm.remove_menu()
            pm.controls.enable_disable_btn.text = "Enable All"
        elif pm.is_all_plugin_enabled():
            pm.create_menu()
            pm.controls.enable_disable_btn.text = "Disable All"
        else:
            pm.refresh_menu()
            pm.controls.enable_disable_btn.text = "Enable All"
        pm.save_session()
        page.update()
        cf.ShowSnackBar(f"{pm.selected_plugin.name} has been enabled" if e.control.value else f"{pm.selected_plugin.name} has been disabled", page)

    def toggle_all_plugins(e: f.ControlEvent):
        value: bool = e.control.text == "Enable All"
        for plugin in pm.walk_items(Plugin):
            plugin.enabled = value
            plugin.controls.tile.content.controls[2].value = value
        if value:
            pm.create_menu()
            pm.controls.enable_disable_btn.text = "Disable All"
        else:
            pm.remove_menu()
            pm.controls.enable_disable_btn.text = "Enable All"
        pm.save_session()
        page.update()
        cf.ShowSnackBar("All plugins have been enabled" if value else "All plugins have been disabled", page)

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

    def reset_plugin_configs(e: f.ControlEvent):
        pm.selected_plugin.selected_types = pm.selected_plugin.supported_types
        for control in pm.selected_plugin.types_control.controls:
            control.value = control.label in pm.selected_plugin.selected_types
        if pm.selected_plugin.configs:
            for config in pm.selected_plugin.configs:
                if config["type"] == "str" or config["type"] == "int" or config["type"] == "float" or config["type"] == "bool":
                    config["control"].value = config["default"]
                elif config["type"] == "checkbox":
                    for control in config["control"].controls:
                        control.value = control.label in config["default"]
                elif config["type"] == "radio":
                    config["control"].value = config["default"]

                if "value" in config:
                    del config["value"]
            refresh_config_page()
        cf.ShowSnackBar("Configurations reset successfully", page)

    def save_plugin_configs(e: f.ControlEvent):
        pm.selected_plugin.selected_types = [control.label for control in pm.selected_plugin.types_control.controls if control.value]
        if pm.selected_plugin.configs:
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
        cf.ShowSnackBar("Configurations saved successfully", page)

    page.title = "Context Menu Plugin Manager"
    # page.icon = "assets/icon.ico"
    page.fonts = {"Inter": "Inter[slnt,wght].ttf"}
    page.theme = f.Theme(font_family="Inter")
    page.padding = 0
    page.bgcolor = pm.themes.current.palette.bg_low
    page.window_min_height = 610
    page.window_min_width = 713
    page.spacing = 0

    make_page()

    page.update()

    time.sleep(0.2)
    loaded_DLL = LoadDLL(
        page=page,
        on_dropped=handle_imports,
        on_entered=open_dnd_dialog,
        on_leaved=close_dialog,
        drop_zone_dll_path=DROPZONE_DLL_PATH,
    )


pm = PluginManager()
f.app(lambda page: main(page, pm), assets_dir=ASSETS_DIR)
