import numpy as np
from basic_data import *
from itertools import chain
from PIL import Image
from PyQt6.QtGui import QIcon, QImage, QPixmap
from typing import Callable, Tuple


WINDOWS = (
    "QMainWindow",
    "QMessageBox",
    "QWidget#Window",
    "QWidget#Picker",
)

WINDOWS = (
    ", ".join(w for window in WINDOWS for w in (window, f"{window}::title"))
    + " { background: "
)


class Style_Compiler:
    @staticmethod
    def validate(entries: dict, widget: str) -> None:
        if entries.keys() - NORMAL_KEYS:
            raise ValueError(
                f"dictionary contains keys that cannot be parsed by this class, widget: {widget}, dictionary: {entries!r}"
            )

    def __init__(
        self,
        widget: str,
        entries: dict,
        round: bool = True,
        keys: list = None,
        vertical: bool = False,
    ) -> None:
        self.validate(entries, widget)
        self.entries = entries
        self.data = {}
        self.keys = keys
        self.round = round
        self.vertical = vertical
        self.widget = widget

    def parse_background(self) -> None:
        if background := self.entries.get("background"):
            if self.entries.keys() & {"lowlight", "highlight"}:
                raise ValueError("background cannot be both plain and gradient")

            self.data["background"] = background

    def parse_gradient(self) -> None:
        highlight = self.entries.get("highlight")
        lowlight = self.entries.get("lowlight")
        if highlight or lowlight:
            if bool(highlight) - bool(lowlight):
                raise ValueError("gradient must have two end points")

            if "background" in self.entries:
                raise ValueError("background cannot be both plain and gradient")

            self.data["background"] = GRADIENT[self.vertical].format(
                lowlight=lowlight, highlight=highlight
            )

    def parse_border(self) -> None:
        bordercolor = self.entries.get("bordercolor")
        borderstyle = self.entries.get("borderstyle")
        if bordercolor or borderstyle:
            if bordercolor and borderstyle:
                self.data["border"] = f"3px {borderstyle} {bordercolor}"

            elif bordercolor:
                self.data["border-color"] = bordercolor

            else:
                self.data["border-style"] = borderstyle

            if self.round:
                self.data["border-radius"] = "6px"

    def parse_color(self) -> None:
        if textcolor := self.entries.get("textcolor"):
            self.data["color"] = textcolor

    def parse(self) -> None:
        self.parse_background()
        self.parse_gradient()
        self.parse_border()
        self.parse_color()
        self.extras = EXTRA_ATTRIBUTES.get(self.widget, {})

    def format_items(self) -> str:
        items = chain.from_iterable(
            [
                ((k, self.data[k]) for k in self.keys)
                if self.keys
                else self.data.items(),
                self.extras.items(),
            ]
        )

        return "\n".join(f"    {k}: {v};" for k, v in items)

    def compile_style(self) -> str:
        self.parse()
        return self.widget + " {\n" + self.format_items() + "\n}\n"


class Style_Combiner:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.compilers = []
        self._get_normal_compilers()
        self._get_special_compilers()

    def _get_normal_compilers(self) -> None:
        self.compilers.extend(
            [
                Style_Compiler(widget, self.config[style])
                for widget, style in WIDGETS["normal"].items()
            ]
        )

    def _get_special_compilers(self) -> None:
        self.compilers.extend(
            [
                Style_Compiler(widget, self.config[style], *args)
                for widget, (style, *args) in WIDGETS["special"].items()
            ]
        )

    def board_style(self) -> str:
        return BOARD_BASE.format_map(self.config["board_base"])

    def hover_label_style(self) -> str:
        return HOVER_LABEL_BASE.format_map(self.config["combobox_menu"])

    def background_style(self) -> str:
        return WINDOWS + self.config["window"]["background"] + "; }\n"

    def combobox_style(self) -> str:
        base = self.config["combobox"]
        menu = self.config["combobox_menu"]
        entries = {}
        for k in BOX:
            entries[f"{k}_1"] = base[k]
            entries[f"{k}_2"] = menu[k]

        return COMBOBOX_BASE.format(
            textcolor=base["textcolor"],
            hoverbase=menu["hoverbase"],
            hovercolor=menu["hovercolor"],
            **entries,
        )

    def mock_dropdown_style(self) -> str:
        return MOCK_MENU_BASE.format_map(self.config["combobox_menu"])

    def special_styles(self) -> str:
        return (
            self.background_style()
            + self.board_style()
            + self.combobox_style()
            + self.hover_label_style()
            + self.mock_dropdown_style()
        )

    def get_style(self) -> str:
        return (
            IMMUTABLE
            + self.special_styles()
            + "".join(compiler.compile_style() for compiler in self.compilers)
        )


class Icon:
    def __init__(self, path: str) -> None:
        self.img = np.array(Image.open(path))
        self.height, self.width = self.img.shape[:2]
        self.base = (self.img / 255)[..., 0:3]
        self.color = np.zeros_like(self.base)
        self.set_icon()

    def set_color(self, color: Tuple[int]) -> None:
        self.color[...] = [i / 255 for i in color]

    def set_blend(self, blend: Callable) -> None:
        self.blend = blend
        self.img[..., 0:3] = (
            (blend(self.base, self.color) * 255).round().astype(np.uint8)
        )

    def set_icon(self) -> None:
        self.qimage = QImage(
            bytearray(self.img), self.width, self.height, QImage.Format.Format_RGBA8888
        )
        self.qsize = self.qimage.size()
        self.qpixmap = QPixmap(self.qimage)
        self.qicon = QIcon(self.qpixmap)


class Piece:
    def __init__(self, color: Tuple[int], blend: str, choice: str, player: str) -> None:
        GLOBALS[player] = self
        self.choices = {shape: Icon(f"{FOLDER}/icons/{shape}.png") for shape in SHAPES}
        self.color = color
        self.blend = BLEND_MODES[blend]
        self.set_active(choice)
        self.set_icon()

    def __set_blend(self) -> None:
        self.active.set_blend(self.blend)

    def set_active(self, choice: str) -> None:
        self.active = self.choices[choice]
        self.set_color()
        self.__set_blend()
        self.set_icon()

    def set_color(self) -> None:
        self.active.set_color(self.color)
        self.__set_blend()
        self.set_icon()

    def set_blend(self, blend: str) -> None:
        self.blend = BLEND_MODES[blend]
        self.__set_blend()
        self.set_icon()

    def set_icon(self) -> None:
        self.active.set_icon()


if __name__ == "__main__":
    combiner = Style_Combiner(CONFIG)
    print(combiner.get_style())
