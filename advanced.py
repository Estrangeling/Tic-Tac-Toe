from basics import *
from gamecontrol import Game
from logic import *
from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtWidgets import QAbstractItemView, QScrollArea, QTableWidget
from shared import *

CELLSTYLES = {
    name: Style_Compiler(f"QLabel#{name}", CONFIG[config])
    for name, config in (
        ("Cell", "board_base"),
        ("Hover", "board_hover"),
        ("P1", "player1_base"),
        ("P2", "player2_base"),
        ("P1Win", "player1_win"),
        ("P2Win", "player2_win"),
    )
}
PLAYER_SETTINGS_PATH = Path(f"{FOLDER}/config/player_settings.json")
if PLAYER_SETTINGS_PATH.is_file():
    PLAYER_SETTINGS = json.loads(PLAYER_SETTINGS_PATH.read_text())
else:
    PLAYER_SETTINGS = {
        "P1": {
            "Blend": "HSL color",
            "Color": (255, 178, 255),
            "Player": "Human",
            "Shape": "Circle",
        },
        "P2": {
            "Blend": "HSV color",
            "Color": (20, 40, 80),
            "Player": "Master AI",
            "Shape": "Circle",
        },
    }


class ColorGetter(BasicColorGetter):
    def __init__(self, widget: str, key: str, name: str, group: str) -> None:
        self.config = CONFIG[widget] if widget else CONFIG
        self.key = key
        self.name = name
        self.group = group
        super().__init__(self.config[key])
        self.init_GUI()
        self.init_connections()

    def init_GUI(self) -> None:
        super().init_GUI()
        self.widgets["button"] = Button(self.color_text)
        self.vbox.addWidget(Label(self.name))
        self.vbox.addWidget(self.widgets["editor"])
        self.vbox.addWidget(self.widgets["button"])

    def init_connections(self) -> None:
        GLOBALS["RandomizeButton"].change.connect(self.sync_config)
        GLOBALS["RevertButton"].revert.connect(self.sync_config)
        super().init_connections()

    def pick_color(self) -> None:
        GLOBALS["revertcheckboxes"][self.group].setDisabled(False)
        GLOBALS["revertible"] = True
        super().pick_color()
        self._update()

    def edit_color(self) -> None:
        GLOBALS["revertcheckboxes"][self.group].setDisabled(False)
        GLOBALS["revertible"] = True
        super().edit_color()
        self._update()

    def _update(self) -> None:
        self.widgets["button"].setText(self.color_text)
        self.config[self.key] = self.color_text
        GLOBALS["Animation"].change.emit()
        GLOBALS["Preview"].update_style()

    def sync_config(self) -> None:
        color_html = self.config[self.key]
        self.color = [int(color_html[a:b], 16) for a, b in ((1, 3), (3, 5), (5, 7))]
        self.widgets["editor"].setText(color_html)
        self.widgets["editor"].color = color_html
        self.widgets["button"].setText(color_html)


class BorderStylizer(Box):
    def __init__(self, widget: str, key: str, name: str, group: str) -> None:
        super().__init__()
        self.config = CONFIG[widget] if widget else CONFIG
        self.key = key
        self.name = name
        self.borderstyle = self.config[key]
        self.init_GUI()
        self.group = group
        GLOBALS["RandomizeButton"].change.connect(self.sync_config)
        GLOBALS["RevertButton"].revert.connect(self.sync_config)

    def init_GUI(self) -> None:
        self.vbox = make_vbox(self)
        self.vbox.addWidget(Label(self.name))
        self.combobox = ComboBox(BORDER_STYLES)
        self.vbox.addWidget(self.combobox)
        self.combobox.setCurrentText(self.borderstyle)
        self.combobox.currentTextChanged.connect(self._update)

    def _update(self) -> None:
        GLOBALS["revertcheckboxes"][self.group].setDisabled(False)
        GLOBALS["revertible"] = True
        self.borderstyle = self.combobox.currentText()
        self.config[self.key] = self.borderstyle
        GLOBALS["Preview"].update_style()

    def sync_config(self) -> None:
        self.borderstyle = self.config[self.key]
        self.combobox.currentTextChanged.disconnect(self._update)
        self.combobox.setCurrentText(self.borderstyle)
        self.combobox.currentTextChanged.connect(self._update)


class RightPane(QScrollArea):
    def __init__(self, group: str, width: int = 150, height: int = 400) -> None:
        super().__init__()
        self.group = group
        self.box = Box()
        self.vbox = make_vbox(self.box)
        self.setWidget(self.box)
        self.setFixedSize(width, height)
        self.setWidgetResizable(True)
        self.setObjectName("Scroll")
        self.add_widgets()

    def add_widgets(self) -> None:
        for name, key in WIDGET_GROUPS[self.group]:
            self.vbox.addWidget(Label(name))
            for k in CONFIG[key]:
                cls = BorderStylizer if k == "borderstyle" else ColorGetter
                self.vbox.addWidget(cls(key, k, k, self.group))


class PieceButton(QPushButton):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name
        self.setObjectName(name)
        self.setFixedSize(100, 100)
        self.setIconSize(QSize(100, 100))


class PieceColorGetter(BasicColorGetter):
    changed = pyqtSignal()

    def __init__(self, color: str, name: str) -> None:
        super().__init__(color)
        self.init_GUI(name)
        self.init_connections()

    def init_GUI(self, name: str) -> None:
        super().init_GUI()
        self.widgets["button"] = PieceButton(name)
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.widgets["editor"])
        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.widgets["button"])

    def edit_color(self) -> None:
        super().edit_color()
        self.changed.emit()

    def pick_color(self) -> None:
        super().pick_color()
        self.changed.emit()


class BaseCell(CenterLabel):
    def __init__(
        self,
        index: int,
        driver: str,
        state: str,
    ) -> None:
        super().__init__("", "", 100, 100)
        self.index = index
        self.checked = False
        self.driver = driver
        self.state = state
        self.init_connections()

    def init_connections(self) -> None:
        GLOBALS[self.driver].clear.connect(self.reset)
        GLOBALS[self.driver].restore.connect(self.reset)

    def change(self) -> None:
        if GLOBALS["animate"]["Board"][0]:
            self._change()

    def reset(self) -> None:
        self.setObjectName("")
        self.clear()
        self.setStyleSheet("")
        self.checked = False


class Square(BaseCell):
    def __init__(self, index: int) -> None:
        super().__init__(index, "Animation", "autostate")
        GLOBALS["Animation"].change.connect(self.change)

    def _change(self) -> None:
        icon, name = GLOBALS[self.state][self.index]
        if icon:
            self.setPixmap(icon)

        if name:
            self.setObjectName(name)
            self.setStyleSheet(CELLSTYLES[name].compile_style())


class Cell(BaseCell):
    def __init__(self, index: int) -> None:
        super().__init__(index, "Game", "gamestate")
        GLOBALS["Game"].change.connect(self._change)

    def _change(self) -> None:
        piece, name = GLOBALS[self.state][self.index]
        if piece:
            self.setPixmap(piece.active.qpixmap)
            self.checked = True

        if name:
            self.setObjectName(name)
            self.setStyleSheet(CELLSTYLES[name].compile_style())
            self.checked = True


class BaseBoard(QTableWidget):
    def __init__(
        self,
        self_name: str,
        board_name: str,
        cls: type[Cell] | type[Square],
    ) -> None:
        super().__init__()
        GLOBALS[self_name] = self
        self.set_size()
        self.cells = [cls(i) for i in range(9)]
        for i, cell in enumerate(self.cells):
            self.setCellWidget(*divmod(i, 3), cell)

        GLOBALS[board_name] = Game_Board()
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

    def set_size(self) -> None:
        self.setColumnCount(3)
        self.setRowCount(3)
        for i in (0, 1, 2):
            self.setColumnWidth(i, 100)
            self.setRowHeight(i, 100)

        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setFixedSize(304, 304)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


class Board(BaseBoard):
    styler = Style_Compiler("QTableWidget#Game::item:hover", CONFIG["board_hover"])

    def __init__(self) -> None:
        GLOBALS["Game"] = Game()
        super().__init__("GUIBoard", "GameBoard", Cell)
        self.setObjectName("Game")
        GLOBALS["gamestate"] = [[None, None] for _ in range(9)]
        self.cellPressed.connect(self.onClick)
        self.interactive = True
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def set_interactive(self, interactive: bool) -> None:
        name = ""
        style = BOARD_BASE.format_map(CONFIG["board_base"])
        if interactive:
            name = "Game"
            style += self.styler.compile_style()

        self.setObjectName(name)
        self.setStyleSheet(style)
        self.interactive = interactive

    def onClick(self, row: int, col: int) -> None:
        if self.interactive and not (cell := self.cellWidget(row, col)).checked:
            GLOBALS["Game"].chosen = cell.index
            GLOBALS["Game"].human_move()

    def update_images(self) -> None:
        for cell in self.cells:
            if cell.checked:
                cell._change()

    def reset(self) -> None:
        self.clearSelection()
        for cell in self.cells:
            cell.reset()


class BasicPlayerBox(Box):
    def __init__(self, number: int, order: str) -> None:
        super().__init__()
        self.setObjectName(f"P{number + 1}")
        self.number = number
        self.order = order

    def init_GUI(self, cls: type[Score] | type[LongScore]) -> None:
        self.vbox = make_vbox(self)
        hbox = QHBoxLayout()
        hbox.addWidget(Label(f"Player {self.number + 1}"))
        self.vbox.addLayout(hbox)
        self.add_scores(cls)
        self.indicator = Label("")

    def add_scores(self, cls: type[Score] | type[LongScore]) -> None:
        self.scores = {}
        self.grid = QGridLayout()
        for i, label in enumerate(("Win", "Loss", "Tie")):
            self.grid.addWidget(CenterLabel(label, label, 30, 16), 0, i)
            self.grid.addWidget(score := cls("0", label), 1, i)
            self.scores[label] = score

    @property
    def player(self) -> str:
        return GLOBALS[self.order][self.number]


class PlayerBox(BasicPlayerBox):
    def __init__(self, number: int) -> None:
        super().__init__(number, "player_order")
        self.init_GUI()
        self.update_indicator()
        GLOBALS["Animation"].gameover.connect(self.update_scores)
        GLOBALS["Animation"].clear.connect(self.update_scores)
        GLOBALS["Animation"].orderchange.connect(self.update_indicator)

    def init_GUI(self) -> None:
        super().init_GUI(Score)
        self.vbox.addStretch()
        self.vbox.addWidget(self.indicator)
        self.vbox.addStretch()
        self.vbox.addLayout(self.grid)
        self.vbox.addStretch()
        self.setFixedSize(120, 130)

    def update_indicator(self) -> None:
        self.indicator.set_text(f"Current: {GLOBALS[self.player]['name']}")

    def update_scores(self) -> None:
        for k, v in GLOBALS[self.player]["stats"].items():
            self.scores[k].setText(str(v))


class GamePlayerBox(BasicPlayerBox):
    def __init__(self, number: int) -> None:
        super().__init__(number, "game_player_order")
        self.init_GUI()
        self.update_indicator()
        GLOBALS["Game"].gameover.connect(self.update_scores)
        GLOBALS["Game"].clear.connect(self.update_scores)
        GLOBALS["Game"].orderchange.connect(self.update_indicator)

    def init_GUI(self) -> None:
        super().init_GUI(LongScore)
        hbox = QHBoxLayout()
        hbox.addWidget(self.indicator)
        hbox1 = QHBoxLayout()
        hbox1.addLayout(self.grid)
        self.vbox.addLayout(hbox)
        self.vbox.addLayout(hbox1)

    def update_indicator(self) -> None:
        self.indicator.set_text(f"Current: {self.player}")

    def update_scores(self) -> None:
        for k, v in GLOBALS["stats"][self.player].items():
            self.scores[k].setText(str(v))


class BasicStats(Box):
    def __init__(self, control: str, prefix: str) -> None:
        super().__init__()
        self.control = control
        self.prefix = prefix

    def init_GUI(self) -> None:
        self.set_game_count()
        self.set_turn_count()
        self.set_active_player()
        self.set_winner()

    def init_connections(self) -> None:
        animation = GLOBALS[self.control]
        animation.gameover.connect(self.set_game_count)
        animation.gameover.connect(self.set_winner)
        animation.playermove.connect(self.set_active_player)
        animation.change.connect(self.set_turn_count)
        animation.clear.connect(self.set_turn_count)
        animation.clear.connect(self.set_active_player)
        animation.clear.connect(self.set_winner)

    def set_game_count(self) -> None:
        self.quad["game"].set_text(f'Game count: {GLOBALS[f"{self.prefix}game_count"]}')

    def set_turn_count(self) -> None:
        self.quad["turn"].set_text(f'Turn count: {GLOBALS[f"{self.prefix}turn_count"]}')

    def set_active_player(self) -> None:
        self.quad["active"].set_text(f'Active: {GLOBALS[f"{self.prefix}active"]}')

    def set_winner(self) -> None:
        self.quad["winner"].set_text(f'Winner: {GLOBALS[f"{self.prefix}winner"]}')


class StatsBox(BasicStats):
    def __init__(self) -> None:
        super().__init__("Animation", "")
        self._init_GUI()
        self.init_connections()

    def _init_GUI(self) -> None:
        self.setObjectName("Stats")
        self.grid = QGridLayout(self)
        self.quad = {}
        for i, key in enumerate(QUADDRUPLE):
            label = Label("")
            self.quad[key] = label
            self.grid.addWidget(label, *divmod(i, 2))

        self.setFixedHeight(130)
        super().init_GUI()


class StatsBar(BasicStats):
    def __init__(self) -> None:
        super().__init__("Game", "live_")
        self._init_GUI()
        self.init_connections()

    def _init_GUI(self) -> None:
        self.setObjectName("Stats")
        self.hbox = make_hbox(self)
        self.quad = {}
        for i, key in enumerate(QUADDRUPLE):
            label = Label("")
            self.quad[key] = label
            self.hbox.addWidget(label)
            if i != 3:
                self.hbox.addStretch()

        self.setFixedHeight(32)
        super().init_GUI()


class Player(Box):
    def __init__(self, label: str, name: str) -> None:
        super().__init__()
        item = PLAYER_SETTINGS[name]
        GLOBALS[name] = self.piece = Piece(
            item["Color"], item["Blend"], item["Shape"], name
        )
        self.item = item
        self.label = label
        self.changed = False
        self.number = int(name[1]) - 1
        self.name = name
        self.boxname = f"{name}Box"
        GLOBALS[self.boxname] = self
        self.setObjectName(name)
        self.setup_GUI()
        self.set_player_info()

    def set_player_info(self) -> None:
        game = GLOBALS["Game"]
        player = self.item["Player"]
        game.new_players[self.name] = (self.piece, player)
        if player == "Human":
            game.new_match["Human"] = (self.piece, self.name)
        else:
            game.new_match["AI"] = (self.name, player)

        game.new_players["changed"] = True
        game.switch_order()
        game.auto_start()

    def setup_GUI(self) -> None:
        self.vbox = make_vbox(self, 3)
        self.vbox.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._setup_playerbox()
        self._setup_player()
        self._setup_shape()
        self._setup_blend()
        self._setup_color()
        self.setFixedSize(150, 330)

    def _setup_playerbox(self) -> None:
        self.playerbox = GamePlayerBox(self.number)
        self.playerbox.setObjectName(self.name)
        self.playerbox.setStyleSheet("QGroupBox { border: 0px;}")
        self.vbox.addWidget(self.playerbox)

    def _setup_player(self) -> None:
        self.player_choice_box = ComboBox(PLAYERS["players"])
        self.player_choice_box.currentTextChanged.connect(self.update_player)
        self.player_choice_box.setCurrentText(self.item["Player"])
        hbox = QHBoxLayout()
        hbox.addWidget(self.player_choice_box)
        self.vbox.addLayout(hbox)

    def _setup_shape(self) -> None:
        self.shape_box = ComboBox(SHAPES)
        self.shape_box.setCurrentText(self.item["Shape"])
        self.shape_box.currentTextChanged.connect(self.pick_piece)
        hbox = QHBoxLayout()
        hbox.addWidget(self.shape_box)
        self.vbox.addLayout(hbox)

    def _setup_blend(self) -> None:
        self.blend_box = ComboBox(BLEND_MODES)
        self.blend_box.setCurrentText(self.item["Blend"])
        self.blend_box.currentTextChanged.connect(self.pick_blend)
        hbox = QHBoxLayout()
        hbox.addWidget(self.blend_box)
        self.vbox.addLayout(hbox)

    def _setup_color(self) -> None:
        r, g, b = self.item["Color"]
        self.colorgetter = PieceColorGetter(f"#{r:02x}{g:02x}{b:02x}", self.name)
        self.colorgetter.vbox.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.colorgetter.widgets["button"].setIcon(self.piece.active.qicon)
        self.colorgetter.setObjectName(self.name)
        self.colorgetter.setStyleSheet("QGroupBox { border: 0px;}")
        self.vbox.addWidget(self.colorgetter)
        self.colorgetter.changed.connect(self.set_color)

    def pick_piece(self) -> None:
        self.item["Shape"] = shape = self.shape_box.currentText()
        self.piece.set_active(shape)
        self.update_icons()

    def set_color(self) -> None:
        self.item["Color"] = self.piece.color = self.colorgetter.color
        self.piece.set_color()
        self.update_icons()

    def pick_blend(self) -> None:
        self.item["Blend"] = blend = self.blend_box.currentText()
        self.piece.set_blend(blend)
        self.update_icons()

    def update_icons(self) -> None:
        self.piece.set_icon()
        self.colorgetter.widgets["button"].setIcon(self.piece.active.qicon)
        GLOBALS["GUIBoard"].update_images()

    def update_player(self) -> None:
        self.item["Player"] = self.player_choice_box.currentText()
        self.changed = True
        self.set_player_info()
        GLOBALS["Window"].check_pairing()
