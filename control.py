import random
from basics import *
from shared import *
from PyQt6.QtCore import pyqtSignal


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
                    random.choice(BORDER_STYLES)
                    if k == "borderstyle"
                    else f"#{random.randrange(16777216):06x}"
                )


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
