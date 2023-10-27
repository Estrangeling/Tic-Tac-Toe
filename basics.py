from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtGui import (
    QColor,
    QFocusEvent,
    QFont,
    QFontMetrics,
    QMouseEvent,
    QShowEvent,
)
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


class LongScore(CenterLabel):
    def __init__(self, text: str, name: str) -> None:
        super().__init__(text, name, 42, 16)


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


class ColorPicker(QWidget):
    instances = []

    def __init__(self) -> None:
        super().__init__()
        self.init_window()
        self.add_dialog()
        self.set_style()
        self.dialog.accepted.connect(self.close)
        self.dialog.rejected.connect(self.close)
        ColorPicker.instances.append(self)

    def init_window(self) -> None:
        self.setWindowIcon(GLOBALS["ICON"])
        self.setWindowTitle("Color Picker")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.MSWindowsFixedSizeDialogHint
        )
        self.vbox = make_vbox(self, 0)
        self.vbox.addWidget(TitleBar("Color Picker", self.close, False))
        self.setFixedSize(518, 436)
        self.frame = self.frameGeometry()
        center = self.screen().availableGeometry().center()
        self.frame.moveCenter(center)
        self.setObjectName("Picker")

    def add_dialog(self) -> None:
        self.dialog = QColorDialog()
        self.dialog.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        grid = self.dialog.findChild(QGridLayout)
        for i in range(grid.count()):
            grid.itemAt(i).widget().setFont(FONT)

        for e in self.dialog.findChildren(QAbstractButton):
            e.setFont(FONT)
            e.setMinimumWidth(72)
            e.setFixedHeight(20)

        for child in self.dialog.children():
            if isinstance(child, QWidget):
                child.setFont(FONT)

        self.vbox.addWidget(self.dialog)

    def showEvent(self, e: QShowEvent) -> None:
        self.move(self.frame.topLeft())
        self.dialog.show()
        e.accept()

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
        self.widgets["picker"].dialog.accepted.connect(self.pick_color)
        self.widgets["editor"].returnPressed.connect(self.edit_color)

    def set_color(self, text: str) -> None:
        self.color = [int(text[a:b], 16) for a, b in ((1, 3), (3, 5), (5, 7))]

    @property
    def color_text(self) -> str:
        r, g, b = self.color
        return f"#{r:02x}{g:02x}{b:02x}"

    def _show_color(self) -> None:
        self.widgets["picker"].dialog.setCurrentColor(QColor(*self.color))
        self.widgets["picker"].show()

    def pick_color(self) -> None:
        self.color = self.widgets["picker"].dialog.currentColor().getRgb()[:3]
        self.widgets["editor"].setText(self.color_text)
        self.widgets["editor"].color = self.color_text

    def edit_color(self) -> None:
        text = self.widgets["editor"].text()
        self.widgets["editor"].color = text
        self.set_color(text)
        self.widgets["editor"].clearFocus()


class SquareButton(QPushButton):
    def __init__(self, icon: str) -> None:
        super().__init__()
        self.setIcon(GLOBALS[icon])
        self.setFixedSize(32, 32)


class TitleBar(QGroupBox):
    def __init__(self, name: str, exitfunc: Callable, minimize: bool = True) -> None:
        super().__init__()
        self.hbox = make_hbox(self, 0)
        self.name = name
        self.exitfunc = exitfunc
        self.start = None
        self.setObjectName("Title")
        self.add_icon()
        self.add_title()
        self.add_buttons(minimize)
        self.setFixedHeight(32)

    def add_icon(self) -> None:
        self.icon = QLabel()
        self.icon.setPixmap(GLOBALS["Logo"])
        self.icon.setFixedSize(32, 32)
        self.hbox.addWidget(self.icon)
        self.hbox.addStretch()

    def add_title(self) -> None:
        self.label = Label(self.name)
        self.hbox.addWidget(self.label)
        self.hbox.addStretch()

    def add_buttons(self, minimize: bool = True) -> None:
        if minimize:
            self.minimize_button = SquareButton("Minimize")
            self.minimize_button.clicked.connect(self.minimize)
            self.hbox.addWidget(self.minimize_button)

        self.close_button = SquareButton("Close")
        self.close_button.clicked.connect(self.exitfunc)
        self.hbox.addWidget(self.close_button)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MouseButton.LeftButton:
            self.start = e.position()

    def mouseMoveEvent(self, e: QMouseEvent) -> None:
        if self.start is not None:
            self.window().move((e.globalPosition() - self.start).toPoint())

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        self.start = None

    def minimize(self) -> None:
        self.window().showMinimized()


class MessageBox(QWidget):
    instances = []

    def __init__(self, title: str, text: str, icon: str, option: str) -> None:
        super().__init__()
        MessageBox.instances.append(self)
        self.setObjectName("Window")
        self.title = title
        self.init_window()
        self.setFixedSize(200, 136)
        self.frame = self.frameGeometry()
        center = self.screen().availableGeometry().center()
        self.frame.moveCenter(center)
        self.add_widgets(text, icon, option)
        self.set_style()

    def init_window(self) -> None:
        self.setWindowTitle(self.title)
        self.setWindowIcon(GLOBALS["ICON"])
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.MSWindowsFixedSizeDialogHint
        )
        self.vbox = make_vbox(self, 0)
        self.vbox.addWidget(TitleBar(self.title, self.close, False))
        self.hbox = QHBoxLayout()
        self.vbox.addLayout(self.hbox)
        self.hbox.addStretch()
        self.buttonbar = QHBoxLayout()
        self.buttonbar.addStretch()
        self.vbox.addLayout(self.buttonbar)

    def add_widgets(self, text: str, icon: str, option: str) -> None:
        self.icon = CenterLabel("", "", 72, 72)
        self.icon.setPixmap(GLOBALS[icon])
        self.hbox.addWidget(self.icon)
        self.label = Label(text)
        self.label.setObjectName(self.title)
        self.hbox.addWidget(self.label)
        self.hbox.addStretch()
        self.ok = Button(option)
        self.ok.clicked.connect(self.close)
        self.buttonbar.addWidget(self.ok)

    def set_style(self) -> None:
        self.setStyleSheet(STYLIZER.get_style())

    def showEvent(self, e: QShowEvent) -> None:
        self.move(self.frame.topLeft())
        e.accept()
