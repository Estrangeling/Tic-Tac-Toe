import json
from basics import MessageBox
from itertools import cycle
from logic import *
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtTest import QTest
from shared import GLOBALS, PLAYER_NAMES


STATSPATH = Path(f"{FOLDER}/Data/stats.json")
AIPLAYERS = {
    "Novice AI": {"function": Menace.get_move, "extra_args": {"P1": (), "P2": ()}},
    "Adept AI": {"function": fill_move, "extra_args": {"P1": (), "P2": ()}},
    "Master AI": {
        "function": stochastic_move,
        "extra_args": {"P1": (STATES_P1, 1), "P2": (STATES_P2, 1)},
    },
    "Master AI+": {
        "function": stochastic_move,
        "extra_args": {"P1": (STATES_P1, 0), "P2": (STATES_P2, 0)},
    },
    "Super AI": {
        "function": optimal_move,
        "extra_args": {"P1": (STATES_P1_COUNTER, 1), "P2": (STATES_P2_COUNTER, 1)},
    },
    "Super AI+": {
        "function": optimal_move,
        "extra_args": {"P1": (STATES_P1_COUNTER, 0), "P2": (STATES_P2_COUNTER, 0)},
    },
}


class Game(QThread):
    gameover = pyqtSignal()
    playermove = pyqtSignal()
    change = pyqtSignal()
    clear = pyqtSignal()
    restore = pyqtSignal()
    orderchange = pyqtSignal()
    pieces = {"O": "P1", "X": "P2"}
    matches = {"O": "AI", "X": "Human"}
    other = {"P1": "P2", "P2": "P1"}

    def __init__(self) -> None:
        super().__init__()
        self.load_stats()
        self.gamestarted = False
        self.auto = False
        self.chosen = None
        self.players = {"P1": [None, None], "P2": [None, None]}
        self.match = {}
        self.new_players = {"P1": [None, None], "P2": [None, None], "changed": False}
        self.new_match = {}
        self.interactive = True
        self.over = False
        self.finished.connect(self.reset)
        self.messages = {
            "Win": MessageBox("Win", "You won!", "win_emoji", "Yes!!!"),
            "Loss": MessageBox("Loss", "You lost...", "loss_emoji", "NOO!!!"),
            "Tie": MessageBox("Tie", "It's a draw", "tie_emoji", "Okay..."),
        }

    def make_move(self, state: str, player: str, piece: str) -> None:
        self.gamestarted = True
        icon, name = self.players[player]
        GLOBALS["live_active"] = name
        self.playermove.emit()
        playerinfo = AIPLAYERS[name]
        move = playerinfo["function"](
            getattr(GLOBALS["GameBoard"], state), *playerinfo["extra_args"][player]
        )
        GLOBALS["GameBoard"].submit(move, piece)
        GLOBALS["gamestate"][move] = (icon, player)
        GLOBALS["live_turn_count"] += 1
        self.change.emit()

    def nought(self) -> None:
        self.make_move("state_string", "P1", "O")

    def cross(self) -> None:
        self.make_move("alternate_state", "P2", "X")

    def run(self) -> None:
        self.interactive = False
        self.auto = True
        while GLOBALS["rungame"]:
            self.over = False
            self.rungame()
            QTest.qWait(125)

        self.interactive = True
        self.quit()

    def rungame(self) -> None:
        turns = cycle([self.nought, self.cross])
        for _ in range(9):
            next(turns)()
            QTest.qWait(125)
            self.judge()
            if self.over:
                break

    def counter_human(self) -> None:
        self.auto = False
        self.make_move("state_string", self.match["AI"][0], "O")
        GLOBALS["live_active"] = "Human"
        self.playermove.emit()
        self.judge()

    def human_move(self) -> None:
        self.auto = False
        self.gamestarted = True
        GLOBALS["gamestate"][self.chosen] = self.match["Human"]
        GLOBALS["GameBoard"].submit(self.chosen, "X")
        GLOBALS["live_turn_count"] += 1
        self.change.emit()
        self.judge(True)

    def judge(self, move: bool = False) -> None:
        state, winner, line = check_state(GLOBALS["GameBoard"].state_string)
        if winner:
            self.process_win(winner, line)
        elif state:
            self.process_tie()
        elif move:
            self.counter_human()

    def process_tie(self) -> None:
        if GLOBALS["popup"] and self.match:
            self.messages["Tie"].show()
            while self.messages["Tie"].isVisible():
                QTest.qWait(42)

        for v in self.players.values():
            self.stats[v[1]]["Tie"] += 1

        if any(p[1] == "Novice AI" for p in self.players.values()):
            Menace.back_propagate("Tie")

        self.reset()

    def process_win(self, winner: str, line: range) -> None:
        if self.match:
            self.process_match_win(winner, line)
        else:
            win_number = self.pieces[winner]
            win_name = self.players[win_number][1]
            loss_number = self.other[win_number]
            loss_name = self.players[loss_number][1]
            self.show_winner(win_name, win_number, loss_name, line)

    def process_match_win(self, winner: str, line: range) -> None:
        if self.matches[winner] == "AI":
            win_number, win_name = self.match["AI"]
            loss_name = "Human"
        else:
            win_name = "Human"
            win_number = self.match["Human"][1]
            loss_name = self.match["AI"][1]

        self.show_winner(win_name, win_number, loss_name, line)

    def show_winner(
        self, win_name: str, win_number: str, loss_name: str, line: range
    ) -> None:
        GLOBALS["live_winner"] = win_name
        self.stats[win_name]["Win"] += 1
        self.stats[loss_name]["Loss"] += 1
        for i in line:
            GLOBALS["gamestate"][i] = (self.players[win_number][0], f"{win_number}Win")

        self.change.emit()
        self.gameover.emit()
        self.post_process(win_name, loss_name)
        QTest.qWait(125)
        self.reset()

    def post_process(self, win_name: str, loss_name: str) -> None:
        if win_name == "Novice AI":
            Menace.back_propagate("Win")
        elif loss_name == "Novice AI":
            Menace.back_propagate("Loss")

        if GLOBALS["popup"] and self.match:
            state = "Win" if win_name == "Human" else "Loss"
            self.messages[state].show()
            while self.messages[state].isVisible():
                QTest.qWait(42)

    def auto_start(self) -> None:
        if (ai := self.match.get("AI")) and ai[0] == "P1" and not self.gamestarted:
            self.counter_human()
            GLOBALS["POPUP"].setDisabled(False)

    def reset(self) -> None:
        self.over = True
        GLOBALS["gamestate"] = [[None, None] for _ in range(9)]
        GLOBALS["GameBoard"].reset()
        GLOBALS["live_game_count"] += 1
        GLOBALS["live_turn_count"] = 0
        GLOBALS["live_winner"] = "null"
        GLOBALS["live_active"] = self.players["P1"][1]
        QTest.qWait(125)
        self.clear.emit()
        if self.interactive:
            self.gamestarted = False
            self.switch_order()
            self.auto_start()

    def switch_order(self) -> None:
        if self.new_players["changed"] and not self.gamestarted:
            self.players = self.new_players.copy()
            self.players.pop("changed")
            GLOBALS["game_player_order"] = players = [
                p[1] for p in self.players.values()
            ]
            self.set_match(players)
            if self.match:
                GLOBALS["rungamebutton"].setDisabled(True)
            else:
                GLOBALS["rungamebutton"].setDisabled(False)

            self.new_players["changed"] = False
            self.gameover.emit()
            self.playermove.emit()
            self.orderchange.emit()

    def set_match(self, players: list) -> None:
        if not (interactive := "Human" in players):
            self.new_match.clear()
            GLOBALS["popup"] = False
            GLOBALS["POPUP"].setDisabled(True)
            GLOBALS["POPUP"].setChecked(False)
        elif "AI" not in self.new_match:
            human = self.new_match["Human"]
            self.new_match["AI"] = (
                (name := self.other[human[1]]),
                self.new_players[name][1],
            )
            GLOBALS["POPUP"].setDisabled(False)
        GLOBALS["GUIBoard"].set_interactive(interactive)
        self.match = self.new_match.copy()

    def load_stats(self) -> None:
        if STATSPATH.is_file():
            self.stats = json.loads(STATSPATH.read_text())
        else:
            self.stats = {
                k: {state: 0 for state in ("Win", "Loss", "Tie")} for k in PLAYER_NAMES
            }
            STATSPATH.write_text(json.dumps(self.stats, indent=4))

        GLOBALS["stats"] = self.stats
