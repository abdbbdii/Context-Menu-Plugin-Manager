import flet as ft
from PluginManager import *
from tkinter import filedialog, messagebox
from os import getenv, mkdir, system
from pathlib import Path
from openai import OpenAI, OpenAIError
import json
from send2trash import send2trash

class Component:
    def Button(text, on_click):
        return ft.FilledButton(text, on_click=on_click, style=ft.ButtonStyle(bgcolor="#3502c9", color="white", padding=ft.padding.Padding(10, 5, 10, 5), shape=ft.RoundedRectangleBorder(radius=5)), height=30)

    def dlg_ask_input_btn(title, content, options: dict, is_ask=True, max_lines=1):
        return ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(content) if is_ask else ft.TextField(label=content, multiline=True, max_lines=max_lines, expand=True, border_color="#9ecaff", border_width=2, autofocus=True, width=500),
            actions=[
                *[ft.TextButton(text, on_click=on_click, style=ft.ButtonStyle(color="white")) for text, on_click in options.items()],
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor="#1d1c44",
            open=True,
            shape=ft.RoundedRectangleBorder(radius=10),
        )


all_installed = False
while not all_installed:
    try:
        pm = PluginManager()
        selected_plugin: Plugin = pm.plugins[0] if pm.plugins else None
    except ModuleNotFoundError as e:
        system("pip install " + str(e).split("'")[1])
    else:
        all_installed = True



def main(page: ft.Page):

    def enable_disable_all_btn_click(e):
        if enable_disable_all_btn.text == "Disable All":
            pm.disable_all_plugins()
            enable_disable_all_btn.text = "Enable All"
        else:
            pm.enable_all_plugins()
            enable_disable_all_btn.text = "Disable All"
        enable_disable_all_btn.update()
        make_plugin_list()
        pm.saveSession()

    def add_plugin_btn_click(e):
        path = filedialog.askdirectory()
        if not path:
            return
        if loaded := pm.loadPlugin(Path(path)):
            pm.plugins.append(loaded)
            loaded.enable_plugin()
            make_plugin_list()
        else:
            messagebox.showerror("Error", "Not a valid plugin directory. Because either no or multiple .py file(s) found with plugin_info dictionary and driver function")

    def uninstall_plugin_btn_click(e):
        def on_no(e):
            dlg_modal.open = False
            e.control.page.update()

        def on_yes(e):
            dlg_modal.open = False
            e.control.page.update()
            if selected_plugin.enable:
                selected_plugin.disable_plugin()
                pm.refresh_context_menu_plugins()
            pm.plugins.remove(selected_plugin)
            send2trash(selected_plugin.parent)
            make_plugin_list()

        dlg_modal = Component.dlg_ask_input_btn("Are you sure?", "Do you want to uninstall this plugin?", {"No": on_no, "Yes": on_yes})
        e.control.page.dialog = dlg_modal
        e.control.page.update()

    def configure__btn_click():
        raise NotImplementedError

    def enter_api_key(e, user_input=None):

        def on_cancel(e):
            dlg_modal.open = False
            e.control.page.update()

        def on_ok(e):
            dlg_modal.open = False
            e.control.page.update()
            dotenv.set_key(DOT_ENV, "OPENAI_API_KEY", dlg_modal.content.value)
            dotenv.load_dotenv(DOT_ENV)
            generate_btn_click(e, user_input)

        dlg_modal = Component.dlg_ask_input_btn("Enter OpenAI API Key", "Type here", {"Cancel": on_cancel, "Ok": on_ok}, is_ask=False, max_lines=1)
        e.control.page.dialog = dlg_modal
        e.control.page.update()

    def generate_btn_click(e, user_input=None):

        if not getenv("OPENAI_API_KEY"):
            enter_api_key(e)
            return

        def on_ok(e):
            dlg_modal.open = False
            e.control.page.update()

            comp = OpenAI()
            comp.api_key = getenv("OPENAI_API_KEY")
            print(getenv("OPENAI_API_KEY"))
            try:
                res: dict = json.loads(
                    comp.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": f'You are a context menu plugin generator. The plugins that are already created are: - unpack files: {open(PLUGINS_DIR / "unpack_files" / "unpack_files.py").read()}\n - remove extra exe: {open(PLUGINS_DIR / "remove_extra_exe" / "remove_extra_exe.py").read()}\n - git clone: {open(PLUGINS_DIR / "git_clone" / "git_clone.py").read()} etc. Now you have to generate a new plugin in json format such as {{"plugin_content": ,"plugin_file_name": ,"detailed_plugin_description_in_markdown_format": ,"markdown_file_name": }}. But do not include icon in plugin_info variable. The plugin should contain a driver function and plugin_info dictionary just like the examples. The plugin should be able to do the following: - '},
                            {"role": "user", "content": user_input if user_input else (latest_user_input := dlg_modal.content.value)},
                        ],
                        response_format={"type": "json_object"},
                    )
                    .choices[0]
                    .message.content
                )

            except OpenAIError as exeption:
                exeption = exeption.__dict__

                def on_open_page(e):
                    dlg.open = False
                    e.control.page.update()
                    system("start https://platform.openai.com/account/api-keys")

                def on_cancel(e):
                    dlg.open = False
                    e.control.page.update()

                def on_enter_api_key(e):
                    dlg.open = False
                    e.control.page.update()
                    enter_api_key(e)

                dlg = Component.dlg_ask_input_btn(exeption["code"], exeption["body"]["message"], {"Cancel": on_cancel, "Open Page": on_open_page, "Enter API Key Again": on_enter_api_key})
                e.control.page.dialog = dlg
                e.control.page.update()
                return

            try:
                parent = PLUGINS_DIR / str(res["plugin_file_name"].rstrip(".py"))
                mkdir(parent)
                open(parent / res["plugin_file_name"], "w", encoding="utf-8").write(res["plugin_content"])
                open(parent / "README.md", "w").write(res["detailed_plugin_description_in_markdown_format"])

            except KeyError:
                generate_btn_click(e, user_input=f"The previous response was {str(res)} I want you to generate again using {{'plugin_content': ,'plugin_file_name': ,'detailed_plugin_description_in_markdown_format': ,'markdown_file_name': }}\nHere is the promt again:\n{latest_user_input}")
                return

            try:
                if loaded := pm.loadPlugin(parent):
                    pm.plugins.append(loaded)
                    loaded.enable_plugin()
                    make_plugin_list()
            except SyntaxError:
                generate_btn_click(e, user_input=f"SyntaxError: The previous response was {str(res)} I want you to generate again using with corrent syntax.\nHere is the promt again:\n{latest_user_input}")
                return

            else:
                generate_btn_click(e, user_input=f"The previous response was {str(res)} I want you to generate again but it should only conatain what system specified.\nHere is the promt again:\n{latest_user_input}")
                return

        def on_cancel(e):
            dlg_modal.open = False
            e.control.page.update()

        dlg_modal = Component.dlg_ask_input_btn("Generate Plugin", "What do you want to generate?", {"Cancel": on_cancel, "Ok": on_ok}, is_ask=False, max_lines=10)
        e.control.page.dialog = dlg_modal
        e.control.page.update()

    def settings_btn_click(e):
        raise NotImplementedError

    def set_main_plugin_info():
        plugin_title.value = selected_plugin.title
        plugin_description.value = selected_plugin.description
        plugin_icon.src = selected_plugin.icon
        plugin_markdown.value = open(selected_plugin.markdown, "r").read()
        plugin_title.update()
        plugin_description.update()
        plugin_icon.update()
        plugin_markdown.update()

    def on_button_click(plugin):
        global selected_plugin
        selected_plugin = plugin
        set_main_plugin_info()

    def on_switch_change(plugin, value):
        if value:
            plugin.enable_plugin()
        else:
            plugin.disable_plugin()
            pm.refresh_context_menu_plugins()

        pm.saveSession()
        enable_disable_all_btn.text = "Disable All" if pm.isAllPluginEnabled() else "Enable All"
        enable_disable_all_btn.update()

    def make_plugin_list():
        plugins = []
        for plugin in pm.plugins:

            def on_button_click_closure(plugin=plugin):
                return lambda e: on_button_click(plugin)

            def on_switch_change_closure(plugin, plugin_switch):
                return lambda e: on_switch_change(plugin, plugin_switch.value)

            plugins.append(
                ft.Container(
                    ft.Row(
                        [
                            ft.Image(plugin.icon, width=40, height=40, border_radius=10),
                            ft.CupertinoButton(plugin.title, color="white", expand=True, alignment=ft.alignment.center_left, on_click=on_button_click_closure(plugin)),
                            plugin_switch := ft.Switch(value=plugin.enable, thumb_color="white", inactive_thumb_color="#8d9199", active_track_color="#3502c9", inactive_track_color="#222048"),
                        ],
                        height=60,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    bgcolor="#242458",
                    border_radius=5,
                    padding=ft.padding.Padding(10, 0, 10, 0),
                )
            )
            plugin_switch.on_change = on_switch_change_closure(plugin, plugin_switch)
            plugin_list.controls = plugins
            plugin_list.scroll = True
            plugin_list.update()

    page.title = "Flet counter example"
    page.fonts = {"Inter": "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bslnt,wght%5D.ttf"}

    page.theme = ft.Theme(font_family="Inter")
    page.padding = 0
    page.bgcolor = "#151635"
    page.window_height = 713
    page.window_width = 1020
    page.window_min_height = 713
    page.window_min_width = 1020
    page.on_close = lambda e: pm.saveSession()

    page.add(
        ft.Row(
            [
                ft.Container(
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text("Plugins", color="white", size=18, weight=ft.FontWeight.W_700),
                                    enable_disable_all_btn := Component.Button("Disable All" if pm.isAllPluginEnabled() else "Enable All", enable_disable_all_btn_click),
                                ],
                                height=80,
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            plugin_list := ft.Column(
                                [],
                                scroll=True,
                                spacing=10,
                            ),
                        ]
                    ),
                    bgcolor="#1d1c44",
                    padding=20,
                    width=300,
                    border_radius=ft.border_radius.BorderRadius(0, 20, 0, 20),
                    alignment=ft.alignment.top_left,
                ),
                ft.Container(
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.SearchBar(
                                        [ft.ListTile(title=ft.Text(plugin.title), data=plugin.title) for plugin in pm.plugins],
                                        view_elevation=1,
                                        bar_leading=ft.IconButton(ft.icons.SEARCH),
                                        bar_hint_text="Search Plugins",
                                        view_hint_text="Search Plugins",
                                        expand=True,
                                        divider_color="#1d1c44",
                                        bar_bgcolor="#222048",
                                        view_bgcolor="#222048",
                                        height=50,
                                    ),
                                    ft.IconButton(ft.icons.BOLT, on_click=generate_btn_click, bgcolor="#F80267", icon_color="white", height=50, width=50),
                                    ft.IconButton(ft.icons.ADD, on_click=add_plugin_btn_click, bgcolor="#3502C9", icon_color="white", height=50, width=50),
                                    ft.IconButton(ft.icons.SETTINGS, on_click=settings_btn_click, bgcolor="#3502C9", icon_color="white", height=50, width=50),
                                ],
                                spacing=20,
                            ),
                            ft.Column(
                                [
                                    ft.Row(
                                        [
                                            plugin_icon := ft.Image(selected_plugin.icon, width=130, height=130),
                                            ft.Column(
                                                [
                                                    plugin_title := ft.Text(selected_plugin.title, size=20),
                                                    plugin_description := ft.Text(selected_plugin.description, size=14, color="#9494ba"),
                                                    ft.Row(
                                                        [
                                                            Component.Button("Configure", lambda e: configure__btn_click()),
                                                            Component.Button("Uninstall", uninstall_plugin_btn_click),
                                                            Component.Button("View in Explorer", lambda e: system(f'explorer.exe "{selected_plugin.parent}"')),
                                                            Component.Button("Open in Code", lambda e: system(f'code "{selected_plugin.path}"')),
                                                        ],
                                                        scroll=True,
                                                    ),
                                                ],
                                                spacing=10,
                                            ),
                                        ]
                                    ),
                                    ft.Divider(thickness=2, color="#242458"),
                                    plugin_markdown := ft.Markdown(
                                        open(selected_plugin.markdown, "r", encoding="utf-8").read() if selected_plugin.markdown else "",
                                        expand=True,
                                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                                    ),
                                ]
                            ),
                        ]
                    ),
                    expand=True,
                    padding=20,
                ),
            ],
            expand=True,
            spacing=0,
        ),
    )

    make_plugin_list()


ft.app(main, assets_dir="assets")
