import ctypes
import sys
from advanced import *
from animation import *
from basics import *
from control import *
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QCloseEvent
from shared import *
from theme import *


class DummyGroupBox(QGroupBox):
    def __init__(self, text: str, name: str) -> None:
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hbox = QHBoxLayout(self)
        self.hbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setObjectName(name)
        self.hbox.addWidget(Label(text))
        self.setFixedSize(120, 130)


class Customizer(Box):
    def __init__(self, mx: int, my: int, w: int, h: int = 420) -> None:
        super().__init__()
        self.hbox = make_hbox(self, mx)
        self.vbox = make_vbox(None, my)
        self.hbox.addLayout(self.vbox)
        self.setFixedSize(w, h)


class ComboBox_Customizer(Customizer):
    def __init__(self) -> None:
        super().__init__(3, 3, 280)
        self.init_GUI()

    def init_GUI(self) -> None:
        self.vbox.addWidget(UniBox())
        self.vbox.addWidget(ListBox())
        self.hbox.addWidget(RightPane("ComboBox"))


class Button_Customizer(Customizer):
    def __init__(self) -> None:
        super().__init__(3, 3, 250)
        self.init_GUI()

    def init_GUI(self) -> None:
        for i, button in enumerate(BUTTONS):
            self.vbox.addWidget(DummyButton(button, i))

        self.vbox.addWidget(BlackButton())
        self.hbox.addWidget(RightPane("Button"))


class LineEdit_Customizer(Customizer):
    def __init__(self) -> None:
        super().__init__(3, 3, 250)
        self.init_GUI()

    def init_GUI(self) -> None:
        for i in range(15):
            self.vbox.addWidget(DummyEdit(i))

        self.hbox.addWidget(RightPane("LineEdit"))


class SpinBox_Customizer(Customizer):
    def __init__(self) -> None:
        super().__init__(3, 0, 230)
        self.init_GUI()

    def init_GUI(self) -> None:
        for i, n in enumerate(GLOBALS[24]):
            self.vbox.addWidget(SpinBox(n, i))

        self.hbox.addWidget(RightPane("SpinBox"))


class CheckBox_Customizer(Customizer):
    def __init__(self) -> None:
        super().__init__(3, 0, 240)
        self.init_GUI()

    def init_GUI(self) -> None:
        for i, (name, state) in enumerate(CHECKBOXES):
            self.vbox.addWidget(AnimationCheckBox(name, state, i))

        self.vbox.addWidget(DummyCheckBox("Disabled", False))
        self.hbox.addWidget(RightPane("CheckBox"))


class Misc_Customizer(Customizer):
    def __init__(self) -> None:
        super().__init__(3, 3, 420)
        self.init_GUI()

    def init_GUI(self) -> None:
        self.grid = QGridLayout()
        self.grid.addWidget(PlayerBox(0), 0, 0)
        self.grid.addWidget(PlayerBox(1), 0, 1)
        self.grid.addWidget(StatsBox(), 1, 0, 1, 2)
        self.grid.addWidget(DummyGroupBox("GroupBox", ""), 2, 0)
        self.grid.addWidget(DummyGroupBox("Background", "Window"), 2, 1)
        self.vbox.addLayout(self.grid)
        self.hbox.addWidget(RightPane("Miscellaneous"))


class RadioButton_Customizer(Customizer):
    def __init__(self) -> None:
        super().__init__(3, 3, 260)
        self.init_GUI()

    def init_GUI(self) -> None:
        for i, (name, state) in enumerate(RADIOBUTTONS):
            self.vbox.addWidget(DummyRadioButton(name, state, i))
            self.vbox.addStretch()

        radio = RadioButton("Disabled")
        radio.setDisabled(True)
        self.vbox.addWidget(radio)
        self.hbox.addWidget(RightPane("RadioButton"))


class Board_Customizer(Customizer):
    def __init__(self) -> None:
        super().__init__(3, 3, 470)
        self.init_GUI()

    def init_GUI(self) -> None:
        self.vbox.addWidget(AutoBoard())
        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        for name in SEXTET:
            row1.addWidget(CenterLabel(name, "", 45, 20))
            row2.addWidget(CenterLabel("", name, 42, 42))

        self.vbox.addLayout(row1)
        self.vbox.addLayout(row2)
        row3 = QHBoxLayout()
        row3.addWidget(Label("Player 1:"))
        row3.addWidget(PlayerRadioButton("Cross", True, "PX"))
        row3.addWidget(PlayerRadioButton("Nought", False, "PO"))
        self.vbox.addLayout(row3)

        self.hbox.addWidget(RightPane("Board"))


FIRST_ROW = (
    Board_Customizer,
    Misc_Customizer,
    CheckBox_Customizer,
    lambda: RightPane("ScrollArea", 150, 420),
)
SECOND_ROW = (
    ComboBox_Customizer,
    RadioButton_Customizer,
    Button_Customizer,
    LineEdit_Customizer,
    SpinBox_Customizer,
)


CINQLIGNES = (
    (QHBoxLayout, "addLayout", True),
    (QHBoxLayout, "addLayout", True),
    (Randomizer, "addWidget", False),
    (Reverter, "addWidget", False),
    (QHBoxLayout, "addLayout", True),
)


class Preview(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowIcon(GLOBALS["ICON"])
        self.setWindowTitle("Preview")
        GLOBALS["Preview"] = self
        self.qthread = Animation(self)
        self.init_icons()
        self.add_rows()
        self.init_GUI()

    def add_rows(self) -> None:
        self.vbox = make_vbox(self)
        self.rows = []
        for cls, func, is_row in CINQLIGNES:
            row = cls()
            getattr(self.vbox, func)(row)
            if is_row:
                self.rows.append(row)

    def init_GUI(self) -> None:
        self.rows[2].addWidget(AnimationBar())
        self.rows[2].addWidget(ControlBox())
        for cls in FIRST_ROW:
            self.rows[0].addWidget(cls())

        for cls in SECOND_ROW:
            self.rows[1].addWidget(cls())

        self.setObjectName("Window")
        self.update_style()
        self.setFixedSize(1300, 960)

    def update_style(self) -> None:
        self.setStyleSheet(STYLIZER.get_style())

    def closeEvent(self, e: QCloseEvent) -> None:
        GLOBALS["run"] = False
        QTest.qWait(125)
        e.accept()

    @staticmethod
    def init_icons() -> None:
        GLOBALS.update(
            {
                "X": QPixmap(QImage(X, 100, 100, QImage.Format.Format_RGBA8888)),
                "O": QPixmap(QImage(O, 100, 100, QImage.Format.Format_RGBA8888)),
            }
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    GLOBALS["ICON"] = QIcon(f"{FOLDER}/Icons/logo.png")
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Tic Tac Toe")
    window = Preview()
    window.show()
    sys.exit(app.exec())
