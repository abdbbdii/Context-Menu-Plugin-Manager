import os
import json
from pathlib import Path

from manager import THEMES_DIR


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
    def __init__(self, path: Path = THEMES_DIR):
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
