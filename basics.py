from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFocusEvent, QFont, QFontMetrics
from PyQt6.QtWidgets import (
    QAbstractButton,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)
from typing import Iterable
from shared import *

ALIGNMENT = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop


class Font(QFont):
    def __init__(self, size: int = 10) -> None:
        super().__init__()
        self.setFamily("Times New Roman")
        self.setStyleHint(QFont.StyleHint.Times)
        self.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setPointSize(size)
        self.setBold(True)
        self.setHintingPreference(QFont.HintingPreference.PreferFullHinting)


FONT = Font()
FONT_RULER = QFontMetrics(FONT)


def make_hbox(parent: QWidget = None, margin: int = 3) -> QHBoxLayout:
    return make_box(QHBoxLayout, parent, margin)


def make_vbox(parent: QWidget = None, margin: int = 3) -> QVBoxLayout:
    return make_box(QVBoxLayout, parent, margin)


class CustomLabel(QLabel):
    def __init__(self, text: str, name: str, width: int, height: int) -> None:
        super().__init__()
        self.setFont(FONT)
        self.setText(text)
        self.setFixedSize(width, height)
        self.setObjectName(name)


class CenterLabel(CustomLabel):
    def __init__(self, text: str, name: str, width: int, height: int) -> None:
        super().__init__(text, name, width, height)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class Score(CenterLabel):
    def __init__(self, text: str, name: str) -> None:
        super().__init__(text, name, 30, 16)


class BlackButton(CenterLabel):
    def __init__(self) -> None:
        super().__init__("Disabled", "Disabled", 72, 20)
        self.setStyleSheet(BLACK)


class CheckBox(QCheckBox):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.setFont(FONT)
        self.setText(text)


class Box(QGroupBox):
    def __init__(self) -> None:
        super().__init__()
        self.setAlignment(ALIGNMENT)
        self.setContentsMargins(0, 0, 0, 0)


class Button(QPushButton):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.setFont(FONT)
        self.setFixedSize(72, 20)
        self.setText(text)


class DummyCheckBox(CheckBox):
    def __init__(self, name: str, checked: bool) -> None:
        super().__init__(name)
        self.setDisabled(True)
        self.setChecked(checked)
        self.setObjectName(name)


class RadioButton(QRadioButton):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.setText(text)
        self.setFont(FONT)
        self.setFixedWidth(FONT_RULER.size(0, text).width() + 30)


class ComboBox(QComboBox):
    def __init__(self, texts: Iterable[str]) -> None:
        super().__init__()
        self.setFont(FONT)
        self.addItems(texts)
        self.setContentsMargins(3, 3, 3, 3)
        self.setFixedWidth(100)


def make_box(
    box_type: type[QHBoxLayout] | type[QVBoxLayout] | type[QGridLayout],
    parent: QWidget,
    margin: int,
) -> QHBoxLayout | QVBoxLayout | QGridLayout:
    box = box_type(parent) if parent else box_type()
    box.setAlignment(ALIGNMENT)
    box.setContentsMargins(*[margin] * 4)
    return box


class MessageBox(QMessageBox):
    instances = []

    def __init__(self, title: str, text: str) -> None:
        super().__init__()
        MessageBox.instances.append(self)
        self.setFont(FONT)
        self.setWindowTitle(title)
        self.setWindowIcon(GLOBALS["ICON"])
        self.setIcon(QMessageBox.Icon.Information)
        self.setText(text)
        self.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.set_style()

    def set_style(self) -> None:
        self.setStyleSheet(STYLIZER.get_style())


class Label(QLabel):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.setFont(FONT)
        self.set_text(text)

    def autoResize(self) -> None:
        self.Height = FONT_RULER.size(0, self.text()).height()
        self.Width = FONT_RULER.size(0, self.text()).width()
        self.setFixedSize(self.Width + 3, self.Height + 3)

    def set_text(self, text: str) -> None:
        self.setText(text)
        self.autoResize()


class ColorEdit(QLineEdit):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.setFixedSize(72, 20)
        self.setFont(FONT)
        self.setInputMask("\#HHHHHH")
        self.setText(text)
        self.color = text

    def focusOutEvent(self, e: QFocusEvent) -> None:
        super().focusOutEvent(e)
        if len(self.text()) != 7:
            self.setText(self.color)
        else:
            self.returnPressed.emit()


class ColorPicker(QColorDialog):
    instances = []

    def __init__(self) -> None:
        super().__init__()
        self.setWindowIcon(GLOBALS["ICON"])
        self.setWindowTitle("Color Picker")
        grid = self.findChild(QGridLayout)
        for i in range(grid.count()):
            grid.itemAt(i).widget().setFont(FONT)

        for e in self.findChildren(QAbstractButton):
            e.setFont(FONT)
            e.setMinimumWidth(72)
            e.setFixedHeight(20)

        for child in self.children():
            if isinstance(child, QWidget):
                child.setFont(FONT)

        self.set_style()
        ColorPicker.instances.append(self)

    def set_style(self) -> None:
        self.setStyleSheet(STYLIZER.get_style())


class BasicColorGetter(Box):
    def __init__(self, color: str) -> None:
        super().__init__()
        self.widgets = {}
        self.vbox = make_vbox(self)
        self.set_color(color)

    def init_GUI(self) -> None:
        self.widgets["editor"] = ColorEdit(self.color_text)
        self.widgets["picker"] = ColorPicker()

    def init_connections(self) -> None:
        self.widgets["button"].clicked.connect(self._show_color)
        self.widgets["picker"].accepted.connect(self.pick_color)
        self.widgets["editor"].returnPressed.connect(self.edit_color)

    def set_color(self, text: str) -> None:
        self.color = [int(text[a:b], 16) for a, b in ((1, 3), (3, 5), (5, 7))]

    @property
    def color_text(self) -> str:
        r, g, b = self.color
        return f"#{r:02x}{g:02x}{b:02x}"

    def _show_color(self) -> None:
        self.widgets["picker"].setCurrentColor(QColor(*self.color))
        self.widgets["picker"].show()

    def pick_color(self) -> None:
        self.color = self.widgets["picker"].currentColor().getRgb()[:3]
        self.widgets["editor"].setText(self.color_text)
        self.widgets["editor"].color = self.color_text

    def edit_color(self) -> None:
        text = self.widgets["editor"].text()
        self.widgets["editor"].color = text
        self.set_color(text)
        self.widgets["editor"].clearFocus()
