import ctypes
import random
import sys
from advanced import *
from basics import *
from gamecontrol import STATSPATH
from preview import Preview
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QMainWindow
from shared import *
from theme import *

SWITCH = cycle(["Stop", "Run"])
STYLIZER = Style_Combiner(CONFIG)


class Window(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        GLOBALS["Window"] = self
        self.initialized = False
        self.init_GUI()
        self.setup_widgets()
        self.add_widgets()
        self.setup_connections()
        self.setStyleSheet(STYLIZER.get_style())
        self.show()
        self.setFixedSize(600, 420)
        self.initialized = True
        GLOBALS["Game"].auto_start()
        if GLOBALS["Game"].match:
            self.popup_box.setDisabled(False)

    def init_GUI(self) -> None:
        frame = self.frameGeometry()
        center = self.screen().availableGeometry().center()
        frame.moveCenter(center)
        self.move(frame.topLeft())
        self.setWindowIcon(GLOBALS["ICON"])
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.setWindowTitle("Tic Tac Toe")

    def setup_widgets(self) -> None:
        self.vbox = make_vbox(self.centralwidget)
        self.hbox = make_hbox()
        self.preview = Preview()
        GLOBALS["POPUP"] = self.popup_box = CheckBox("Popup messages")
        self.run = GLOBALS["rungamebutton"] = Button("Run")
        self.board = Board()
        self.player1 = Player("Player 1", "P1")
        self.player2 = Player("Player 2", "P2")
        self.statsbar = StatsBar()
        self.underbar = QHBoxLayout()
        self.customize_button = Button("Customize")

    def add_widgets(self) -> None:
        self.hbox.addWidget(self.board)
        self.hbox.addWidget(self.player1)
        self.hbox.addWidget(self.player2)
        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.statsbar)
        self.underbar.addWidget(self.popup_box)
        self.underbar.addStretch()
        self.underbar.addWidget(self.customize_button)
        self.underbar.addStretch()
        self.underbar.addWidget(self.run)
        self.vbox.addLayout(self.underbar)

    def setup_connections(self) -> None:
        self.popup_box.clicked.connect(self.set_popup)
        self.customize_button.clicked.connect(self.preview.show)
        self.run.clicked.connect(self.toggle)
        self.underbar.addWidget(self.run)

    def check_pairing(self) -> None:
        if (
            self.initialized
            and self.player1.item["Player"] == self.player2.item["Player"]
        ):
            if self.player1.changed:
                self.ensure_opponent(self.player1, self.player2)
            else:
                self.ensure_opponent(self.player2, self.player1)

    def ensure_opponent(self, new: Player, old: Player) -> None:
        new.changed = False
        box = old.player_choice_box
        box.currentTextChanged.disconnect(old.update_player)
        choice = random.choice(PLAYERS["opponents"][new.item["Player"]])
        old.player_choice_box.setCurrentText(choice)
        old.item["Player"] = choice
        old.set_player_info()
        box.currentTextChanged.connect(old.update_player)

    def toggle(self) -> None:
        self.run.setText(next(SWITCH))
        GLOBALS["rungame"] ^= 1
        if GLOBALS["rungame"]:
            GLOBALS["Game"].start()

    def set_popup(self) -> None:
        GLOBALS["popup"] = self.popup_box.isChecked()

    def closeEvent(self, e: QCloseEvent) -> None:
        GLOBALS["rungame"] = False
        GLOBALS["pause"] = True
        GLOBALS["run"] = False
        STATSPATH.write_text(json.dumps(GLOBALS["Game"].stats, indent=4))
        PLAYER_SETTINGS_PATH.write_text(json.dumps(PLAYER_SETTINGS, indent=4))
        Path(f"{FOLDER}/Data/menace-memory.pkl").write_bytes(
            pickle.dumps(MENACE_MEMORY, protocol=pickle.HIGHEST_PROTOCOL)
        )
        QTest.qWait(125)
        for window in QApplication.topLevelWidgets():
            window.close()

        e.accept()


if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("Fusion")
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Tic Tac Toe")
    GLOBALS["ICON"] = QIcon(f"{FOLDER}/Icons/logo.png")
    window = Window()
    sys.exit(app.exec())
