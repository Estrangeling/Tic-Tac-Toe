import random
from typing import List
from basics import *
from color import RGB_from_HSV_pixel
from functools import cache
from shared import *
from PyQt6.QtCore import pyqtSignal


@cache
def agm(a: int | float, b: int | float, n: int = 16) -> int | float:
    if a > b:
        a, b = b, a
    for _ in range(n):
        c = (a * b) ** 0.5
        d = (a + b) / 2
        a, b = c, d
    return (c + d) / 2


@cache
def gauss(x: int | float, weight: int | float) -> int | float:
    return np.exp(-(x - 0.5) * (x - 0.5) / (2 * weight**2))


def randBias(
    base: int | float, top: int | float, bias: int | float, weight: float = 0.5
) -> int | float:
    assert 0 < weight <= 1
    influence = random.random()
    x = random.random() * (top - base) + base
    if x > bias:
        return x + gauss(influence, weight) * (bias - x)
    return x - gauss(influence, weight) * (x - bias)


LUMA = {
    "textcolor": (0.9, 1, agm(0.9, 1)),
    "background": (0.2, 0.5, agm(0.2, 0.5)),
    "lowlight": (1 / 3, 2 / 3, agm(1 / 3, 2 / 3)),
    "highlight": (0.75, 1, agm(0.75, 1)),
    "bordercolor": (0.5, 1, agm(0.5, 1)),
    "hoverbase": (2 / 3, 0.8, agm(2 / 3, 0.8)),
    "hovercolor": (0.9, 1, agm(0.9, 1)),
}

BORDERS = (
    "groove",
    "outset",
    "ridge",
    "solid",
    "double",
    "inset",
)

BACKGROUNDS = {"background", "lowlight", "highlight", "hoverbase"}


def get_hue(key: str) -> float:
    return (
        randBias(0.5, 11 / 12, agm(0.5, 11 / 12), 0.25)
        if key in BACKGROUNDS
        else random.random()
    )


def make_weights(power: float, n: int) -> List[float]:
    weights = [1.0]
    remaining = 1.0
    for _ in range(n - 1):
        weights.append(term := remaining * power)
        remaining -= term

    return weights


WEIGHTS = make_weights(agm(0.5, (5**0.5 - 1) / 2), 6)


class PauseButton(Button):
    def __init__(self) -> None:
        super().__init__("Pause")
        GLOBALS["PauseButton"] = self
        self.clicked.connect(self.switch)

    def switch(self) -> None:
        GLOBALS["pause"] ^= 1
        self.setText(next(PAUSE))


class RunButton(Button):
    def __init__(self) -> None:
        super().__init__("Start")
        GLOBALS["RunButton"] = self
        self.clicked.connect(self.switch)

    def switch(self) -> None:
        self.setText(next(RUN))
        GLOBALS["pause"] = GLOBALS["run"]
        if GLOBALS["PauseButton"].text() == "Resume":
            GLOBALS["PauseButton"].setText("Pause")
            next(PAUSE)

        GLOBALS["run"] ^= 1
        if GLOBALS["run"]:
            GLOBALS["Preview"].qthread.start()


class PlayerRadioButton(RadioButton):
    def __init__(self, text: str, state: bool, player: str) -> None:
        super().__init__(text)
        self.setChecked(state)
        self.player = player
        self.toggled.connect(self.switch_order)

    def switch_order(self) -> None:
        if self.isChecked():
            entry = PLAYERINFO[self.player]
            other = entry[0]
            GLOBALS["new_order"] = [self.player, other]
            if GLOBALS["run"]:
                GLOBALS["orderchanged"] = True
            else:
                GLOBALS["Animation"].switch_order(self.player, other, entry)


class RevertButton(Button):
    revert = pyqtSignal()

    def __init__(self) -> None:
        super().__init__("Revert")
        GLOBALS["RevertButton"] = self
        self.clicked.connect(self.revert_style)

    def revert_style(self) -> None:
        if GLOBALS["revertible"]:
            for group, change in GLOBALS["groups"].items():
                if change[1]:
                    self.revert_group(group)

            self.revert.emit()
            GLOBALS["Preview"].update_style()
            GLOBALS["Preview"].qthread.change.emit()
            GLOBALS["revertible"] = False

    @staticmethod
    def revert_group(group: str) -> None:
        for _, key in WIDGET_GROUPS[group]:
            entry = CONFIG[key]
            for k, v in CONFIG_COPY[key].items():
                entry[k] = v


class RandomizeButton(Button):
    change = pyqtSignal()

    def __init__(self) -> None:
        super().__init__("Randomize")
        GLOBALS["RandomizeButton"] = self
        self.clicked.connect(self.random_style)

    def random_style(self) -> None:
        for group, change in GLOBALS["groups"].items():
            if change[0]:
                self.change_group(group)
                GLOBALS["revertcheckboxes"][group].setDisabled(False)

        self.change.emit()
        GLOBALS["Preview"].update_style()
        GLOBALS["Animation"].change.emit()
        GLOBALS["revertible"] = True

    @staticmethod
    def change_group(group: str) -> None:
        for _, key in WIDGET_GROUPS[group]:
            entry = CONFIG[key]
            for k in entry:
                entry[k] = (
                    random.choices(BORDERS, weights=WEIGHTS)[0]
                    if k == "borderstyle"
                    else RandomizeButton.weighted_color(k)
                )

    @staticmethod
    def weighted_color(key: str) -> str:
        r, g, b = [
            round(i * 255)
            for i in RGB_from_HSV_pixel(
                get_hue(key),
                randBias(0.5, 1, agm(0.5, 1), 0.25),
                randBias(*LUMA[key]),
            )
        ]
        return f"#{r:02x}{g:02x}{b:02x}"


class AnimateCheckBox(CheckBox):
    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.key = text
        self.setChecked(True)
        self.stateChanged.connect(self.update_config)

    def update_config(self) -> None:
        GLOBALS["animate"][self.key][0] = self.isChecked()


class RandomizerCheckBox(CheckBox):
    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.key = text
        self.setChecked(True)
        self.stateChanged.connect(self.update_config)

    def update_config(self) -> None:
        GLOBALS["groups"][self.key][0] = self.isChecked()


class RevertCheckBox(CheckBox):
    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.key = text
        GLOBALS["revertcheckboxes"][text] = self
        self.setChecked(True)
        self.setDisabled(True)
        self.init_connections()

    def init_connections(self) -> None:
        GLOBALS["RevertButton"].revert.connect(self.disable)
        self.stateChanged.connect(self.update_config)

    def disable(self) -> None:
        self.setDisabled(True)

    def update_config(self) -> None:
        GLOBALS["groups"][self.key][1] = self.isChecked()


class AnimationBar(Box):
    def __init__(self) -> None:
        super().__init__()
        self.hbox = make_hbox(self)
        self.hbox.addWidget(RunButton())
        self.hbox.addStretch()
        for key in GLOBALS["animate"]:
            self.hbox.addWidget(AnimateCheckBox(key))
            self.hbox.addStretch()

        self.hbox.addWidget(PauseButton())


class Randomizer(Box):
    def __init__(self) -> None:
        super().__init__()
        self.init_layout()
        self.init_GUI()

    def init_layout(self) -> None:
        self.hbox = make_hbox(self)

    def init_GUI(self) -> None:
        self.hbox.addWidget(RandomizeButton())
        for key in GLOBALS["groups"]:
            self.hbox.addStretch()
            self.hbox.addWidget(RandomizerCheckBox(key))


class Reverter(Box):
    def __init__(self) -> None:
        super().__init__()
        self.init_layout()
        self.init_GUI()

    def init_layout(self) -> None:
        self.hbox = make_hbox(self)

    def init_GUI(self) -> None:
        self.hbox.addWidget(RevertButton())
        for key in GLOBALS["groups"]:
            self.hbox.addStretch()
            self.hbox.addWidget(RevertCheckBox(key))


class ControlBox(Box):
    def __init__(self) -> None:
        super().__init__()
        self.init_layout()
        self.init_GUI()

    def init_layout(self) -> None:
        self.hbox = make_hbox(self)

    def init_GUI(self) -> None:
        self.buttons = {}
        for text, func in CONTROL:
            button = Button(text)
            button.clicked.connect(getattr(self, func))
            self.hbox.addWidget(button)
            self.buttons[text] = button

    def restore_default(self) -> None:
        global CONFIG_COPY
        CONFIG_COPY = deepcopy(DEFAULT_CONFIG)
        for widget, values in CONFIG.items():
            for key in values:
                values[key] = DEFAULT_CONFIG[widget][key]

        CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=4))
        self.revert()

    def apply_style(self) -> None:
        global CONFIG_COPY
        CONFIG_COPY = deepcopy(CONFIG)
        CONFIG_PATH.write_text(json.dumps(CONFIG, indent=4))
        self.apply_change()

    def revert_style(self) -> None:
        for widget, values in CONFIG.items():
            for key in values:
                values[key] = CONFIG_COPY[widget][key]

        self.revert()
        self.apply_change()

    @staticmethod
    def apply_change() -> None:
        for i in ColorPicker.instances + MessageBox.instances:
            i.set_style()

        if window := GLOBALS.get("Window"):
            board = GLOBALS["GUIBoard"]
            window.setStyleSheet(STYLIZER.get_style())
            for cell in board.cells:
                cell._change()

            board.set_interactive(board.interactive)

            if GLOBALS["run"]:
                GLOBALS["RunButton"].click()

            GLOBALS["Preview"].hide()

    @staticmethod
    def revert() -> None:
        GLOBALS["RevertButton"].revert.emit()
        GLOBALS["Preview"].update_style()
        GLOBALS["Preview"].qthread.change.emit()
