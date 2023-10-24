import random
from advanced import *
from basics import *
from logic import check_state, optimal_move, stochastic_move
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QLabel, QSpinBox, QWidget
from shared import *
from typing import Callable, Iterable


class Box100(Box):
    def __init__(self, layout: Callable) -> None:
        super().__init__()
        self.box = layout(self, 0)
        self.setFixedWidth(100)


class ListBox(Box100):
    def __init__(self) -> None:
        super().__init__(make_vbox)
        self.items = []
        for i, (word, name) in enumerate(zip(NONSENSE, SEXDECIM)):
            label = DynamicLabel(word, name, 100, 20, i)
            self.items.append(label)
            self.box.addWidget(label)

        self.setObjectName("Menu")


class TopLabel(CustomLabel):
    def __init__(self, text: str, name: str, width: int, height: int) -> None:
        super().__init__(text, name, width, height)
        GLOBALS["Animation"].change.connect(self.change)
        GLOBALS["Animation"].restore.connect(self._change)

    def change(self) -> None:
        if GLOBALS["animate"]["ComboBox"][0]:
            self._change()

    def _change(self) -> None:
        self.setText(NONSENSE[SEXDECIM.index("High")])


class DummyEdit(CustomLabel):
    def __init__(self, index: int) -> None:
        super().__init__("", "Edit", 72, 20)
        self.index = index
        self.change()
        GLOBALS["Animation"].change.connect(self.change)
        GLOBALS["Animation"].restore.connect(self._change)

    def change(self) -> None:
        if GLOBALS["animate"]["LineEdit"][0]:
            self._change()

    def _change(self) -> None:
        self.setText(f"#{16777216 - GLOBALS[15][self.index]:06x}")


class Arrow(QLabel):
    def __init__(self) -> None:
        super().__init__()
        self.setFixedSize(10, 10)
        self.setPixmap(self.get_arrow())
        self.setObjectName("Arrow")
        self.setStyleSheet("QLabel#Arrow {margin-right: 2px;}")

    @staticmethod
    def get_arrow() -> QPixmap:
        return QPixmap(
            QImage(
                bytearray(
                    np.array(Image.open(f"{FOLDER}/icons/combobox-downarrow.png"))
                ),
                10,
                10,
                QImage.Format.Format_RGBA8888,
            )
        )


class UniBox(Box100):
    def __init__(self) -> None:
        super().__init__(make_hbox)
        self.setFixedHeight(23)
        self.left = TopLabel(NONSENSE[0], "Mock", 70, 16)
        self.box.addWidget(self.left)
        self.box.addStretch()
        self.right = Arrow()
        self.box.addWidget(self.right)
        self.setObjectName("Top")


class SpinBox(QSpinBox):
    def __init__(self, value: int, index: int) -> None:
        super().__init__()
        self.index = index
        self.setFixedSize(50, 23)
        self.setFont(FONT)
        self.setAlignment(ALIGNMENT)
        self.setMaximum(9999)
        self.setValue(value)
        GLOBALS["Animation"].change.connect(self.change)
        GLOBALS["Animation"].restore.connect(self._change)
        self.setObjectName("Dummy")
        self.setDisabled(True)

    def change(self) -> None:
        if GLOBALS["animate"]["SpinBox"][0]:
            self._change()

    def _change(self) -> None:
        self.setValue(GLOBALS[24][self.index])


class DummyButton(CenterLabel):
    styles = {
        "Base": Style_Compiler("DummyButton#Base", CONFIG["button"]),
        "Hover": Style_Compiler("DummyButton#Hover", CONFIG["button_hover"]),
        "Pressed": Style_Compiler("DummyButton#Pressed", CONFIG["button_pressed"]),
    }

    def __init__(self, text: str, index: int) -> None:
        super().__init__(text, text, 72, 20)
        self.index = index
        GLOBALS["Animation"].change.connect(self.change)
        GLOBALS["Animation"].restore.connect(self._change)

    def change(self) -> None:
        if GLOBALS["animate"]["Button"][0]:
            self._change()

    def _change(self) -> None:
        name = BUTTONS[self.index]
        self.setText(name)
        self.setObjectName(name)
        self.setStyleSheet(self.styles[name].compile_style())


class AutoBoard(BaseBoard):
    def __init__(self) -> None:
        super().__init__("AutoBoard", "AnimationBoard", Square)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)


class AnimationCheckBox(DummyCheckBox):
    styles = {
        "Base": Style_Compiler("QCheckBox", CONFIG["checkbox"]),
        "Hover": Style_Compiler("QCheckBox#Hover", CONFIG["checkbox_hover"]),
        "Pressed": Style_Compiler("QCheckBox#Pressed", CONFIG["checkbox_pressed"]),
    }

    def __init__(self, name: str, checked: bool, index: int) -> None:
        super().__init__(name, checked)
        self.index = index
        GLOBALS["Animation"].change.connect(self.change)
        GLOBALS["Animation"].restore.connect(self._change)

    def change(self) -> None:
        if GLOBALS["animate"]["CheckBox"][0]:
            self._change()

    def _change(self) -> None:
        name, checked = CHECKBOXES[self.index]
        self.setText(name)
        self.setObjectName(name)
        self.setChecked(checked)
        self.setStyleSheet(self.styles[name].compile_style())


class DynamicLabel(CustomLabel):
    compiler = Style_Compiler("QLabel#Mock", CONFIG["combobox"], False, ["color"])

    def __init__(
        self, text: str, name: str, width: int, height: int, index: int
    ) -> None:
        super().__init__(text, name, width, height)
        self.index = index
        GLOBALS["Animation"].change.connect(self.change)
        GLOBALS["Animation"].restore.connect(self._change)

    def change(self) -> None:
        if GLOBALS["animate"]["ComboBox"][0]:
            self._change()

    def _change(self) -> None:
        self.setText(NONSENSE[self.index])
        name = (
            ("Focus" if self.index else name)
            if (name := SEXDECIM[self.index]) == "High"
            else name
        )
        self.setObjectName(name)
        self.setStyleSheet(
            self.compiler.compile_style()
            if name == "Mock"
            else HOVER_LABEL_BASE.format_map(CONFIG["combobox_menu"])
        )


class DummyRadioButton(RadioButton):
    styles = {
        "Base": Style_Compiler("QRadioButton#Base", CONFIG["radiobutton"]),
        "Hover": Style_Compiler("QRadioButton#Hover", CONFIG["radiobutton_hover"]),
        "Pressed": Style_Compiler(
            "QRadioButton#Pressed", CONFIG["radiobutton_pressed"]
        ),
    }

    def __init__(self, name: str, state: bool, index: int) -> None:
        super().__init__(name)
        self.setDisabled(True)
        self.setChecked(state)
        self.setObjectName(name)
        self.setAutoExclusive(False)
        self.index = index
        GLOBALS["Animation"].change.connect(self.change)
        GLOBALS["Animation"].restore.connect(self._change)

    def change(self) -> None:
        if GLOBALS["animate"]["RadioButton"][0]:
            self._change()

    def _change(self) -> None:
        name, checked = RADIOBUTTONS[self.index]
        self.setText(name)
        self.setObjectName(name)
        self.setChecked(checked)
        self.setStyleSheet(self.styles[name].compile_style())


class Animation(QThread):
    change = pyqtSignal()
    clear = pyqtSignal()
    gameover = pyqtSignal()
    playermove = pyqtSignal()
    restore = pyqtSignal()
    orderchange = pyqtSignal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        GLOBALS["Animation"] = self
        self.advance = True
        a, b = GLOBALS["order"]
        self.turns = cycle([getattr(self, a), getattr(self, b)])
        GLOBALS["autostate"] = [[None, None] for _ in range(9)]
        self.state = 0

    def run(self) -> None:
        while GLOBALS["run"]:
            self.animate()
            QTest.qWait(125)

        self.reset()
        self.quit()

    def animate(self) -> None:
        while GLOBALS["run"] and GLOBALS["pause"]:
            QTest.qWait(40)

        count = 0
        for state, func in GLOBALS["animate"].values():
            if state:
                count += 1
                getattr(self, func)()

        if count:
            self.change.emit()
        else:
            GLOBALS["RunButton"].click()

    def animate_buttons(self) -> None:
        random.shuffle(BUTTONS)

    def animate_radiobuttons(self) -> None:
        random.shuffle(RADIOBUTTONS)

    def animate_combobox(self) -> None:
        random.shuffle(NONSENSE)
        random.shuffle(SEXDECIM)

    def animate_checkbox(self) -> None:
        random.shuffle(CHECKBOXES)

    def animate_spinbox(self) -> None:
        self.roll(SECRET, 24)

    def animate_lineedit(self) -> None:
        self.roll(SECRET_TOO, 15)

    def roll(self, matrix: Iterable[Iterable[int]], length: int) -> None:
        GLOBALS[length] = matrix[next(GLOBALS[str(length)])].copy()

    def make_move(self, move: int, player: str) -> None:
        GLOBALS["AnimationBoard"].submit(move, player)
        self.move = (move, player)
        if GLOBALS[f"P{player}"]["id"] == "P1":
            GLOBALS["autostate"][move][1] = "Hover"
            self.advance = False
        else:
            self.update_board()

    def nought(self) -> None:
        GLOBALS["active"] = GLOBALS["PO"]["name"]
        self.playermove.emit()
        move = optimal_move(
            GLOBALS["AnimationBoard"].state_string, GLOBALS["PO"]["states"], 0
        )
        self.make_move(move, "O")

    def cross(self) -> None:
        GLOBALS["active"] = GLOBALS["PX"]["name"]
        self.playermove.emit()
        move = stochastic_move(
            GLOBALS["AnimationBoard"].alternate_state, GLOBALS["PX"]["states"], 0
        )
        self.make_move(move, "X")

    def update_board(self) -> None:
        move, player = self.move
        GLOBALS["autostate"][move] = [GLOBALS[player], GLOBALS[f"P{player}"]["id"]]
        self.advance = True
        GLOBALS["turn_count"] += 1

    def animate_game(self) -> None:
        if self.advance:
            if self.state == 0:
                next(self.turns)()
            elif self.state == 1:
                self.show_winner()
            else:
                self.reset_game()
        else:
            self.update_board()

        if not self.state:
            self.judge()

    def judge(self) -> None:
        state, winner, line = check_state(GLOBALS["AnimationBoard"].state_string)
        if winner:
            self.process_win(winner, line)
        elif state:
            self.state = 2
            GLOBALS["game_count"] += 1
            GLOBALS["PX"]["stats"]["Tie"] += 1
            GLOBALS["PO"]["stats"]["Tie"] += 1
            self.gameover.emit()

    def process_win(self, winner: str, line: range) -> None:
        player = GLOBALS[f"P{winner}"]
        GLOBALS["winner"] = player["name"]
        player["stats"]["Win"] += 1
        GLOBALS[player["opponent"]]["stats"]["Loss"] += 1
        GLOBALS["game_count"] += 1
        self.winner = f"{player['id']}Win", line
        self.state = 1

    def show_winner(self) -> None:
        name, line = self.winner
        for i in line:
            GLOBALS["autostate"][i][1] = name

        self.state = 2
        self.advance = True
        self.gameover.emit()

    def reset(self) -> None:
        self.reset_buttons()
        self.reset_checkbox()
        self.reset_combobox()
        self.reset_spinbox()
        self.reset_lineedit()
        self.reset_game()
        self.reset_radiobuttons()
        self.restore.emit()
        if GLOBALS["orderchanged"]:
            player, other = GLOBALS["new_order"]
            self.switch_order(player, other, PLAYERINFO[player])

    def reset_buttons(self) -> None:
        global BUTTONS
        BUTTONS = BUTTONS_COPY.copy()

    def reset_radiobuttons(self) -> None:
        global RADIOBUTTONS
        RADIOBUTTONS = RADIOBUTTONS_COPY.copy()

    def reset_checkbox(self) -> None:
        global CHECKBOXES
        CHECKBOXES = CHECKBOXES_COPY.copy()

    def reset_combobox(self) -> None:
        global NONSENSE, SEXDECIM
        NONSENSE = NONSENSE_COPY.copy()
        SEXDECIM = ["High"] + ["Mock"] * 15

    def reset_game(self) -> None:
        GLOBALS["autostate"] = [[None, None] for _ in range(9)]
        GLOBALS["AnimationBoard"].reset()
        self.advance = True
        a, b = GLOBALS["order"]
        self.turns = cycle([getattr(self, a), getattr(self, b)])
        self.state = 0
        GLOBALS["turn_count"] = 0
        GLOBALS["active"] = GLOBALS[GLOBALS["player_order"][0]]["name"]
        GLOBALS["winner"] = "null"
        self.clear.emit()

    def reset_lineedit(self) -> None:
        GLOBALS[15] = SECRET_TOO[0].copy()
        GLOBALS["15"] = cycle(range(15))

    def reset_spinbox(self) -> None:
        GLOBALS[24] = SECRET[0].copy()
        GLOBALS["24"] = cycle(range(24))

    def switch_order(self, player: str, other: str, entry: list) -> None:
        GLOBALS["player_order"] = (player, other)
        other_entry = PLAYERINFO[other]
        a = entry[1]
        b = other_entry[1]
        GLOBALS["order"] = (a, b)
        self.turns = cycle([getattr(self, a), getattr(self, b)])
        self.set_player_info(player, entry, 2, "P1")
        self.set_player_info(other, other_entry, 3, "P2")
        GLOBALS["orderchanged"] = False
        self.orderchange.emit()
        self.gameover.emit()

    def set_player_info(self, player: str, entry: str, i: int, name: str) -> None:
        info = GLOBALS[player]
        info["states"] = entry[i]
        info["id"] = name
