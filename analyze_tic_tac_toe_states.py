import json
import pickle
from collections import Counter
from itertools import accumulate, product
from logic import LINES
from pathlib import Path
from typing import Tuple


FOLDER = str(Path(__file__).parent).replace("\\", "/")


def check_state(board: str) -> Tuple[bool, str]:
    for start, stop, step in LINES:
        line = board[start:stop:step]
        if len(set(line)) == 1 and (winner := line[0]) in {"O", "X"}:
            return True, winner

    return " " not in board, None


def is_valid(board: str) -> bool:
    winners = set()
    winner = None
    for start, stop, step in LINES:
        line = board[start:stop:step]
        if len(set(line)) == 1 and (winner := line[0]) in {"O", "X"}:
            winners.add(winner)

    return (
        len(winners) <= 1
        and abs(board.count("O") - board.count("X")) <= 1
        and (not winner or board.count(winner) >= board.count("OX".replace(winner, "")))
    )


VALID_BOARDS = [board for board in product(" OX", repeat=9) if is_valid(board)]


def repr_board(board: str, indent: int) -> str:
    return (
        " " * indent
        + "[\n"
        + ",\n".join(" " * (indent + 1) + repr(board[i : i + 3]) for i in (0, 3, 6))
        + "\n"
        + " " * indent
        + "]"
    )


Path(f"{FOLDER}/Data/tic-tac-toe-boards.txt").write_text(
    "[\n" + ",\n".join(repr_board(board, 1) for board in VALID_BOARDS) + "\n]"
)

Path(f"{FOLDER}/Data/tic-tac-toe-boards.json").write_text(
    "[\n" + ",\n".join('\t"' + "".join(board) + '"' for board in VALID_BOARDS) + "\n]"
)


STATES_P1 = {}
STATES_P2 = {}


class Board_Analyzer:
    def __init__(self, board: str, move: str, states: dict) -> None:
        self.other = "OX".replace(move, "")
        self.total_wins = 0
        self.total_ties = 0
        self.win_moves = Counter()
        self.tie_moves = Counter()
        self.high_stakes = Counter()
        self.legal_moves = []
        self.board = board
        self.states = states
        self.move = move

    def set_board_state(self) -> None:
        state = {
            "over": False,
            "repr": [self.board[i : i + 3] for i in (0, 3, 6)],
            "wins": self.total_wins,
            "ties": self.total_ties,
            "legal_moves": tuple(self.legal_moves),
        }
        if self.total_wins:
            state["win_moves"] = self.win_moves

        if self.total_ties:
            state["tie_moves"] = self.tie_moves

        if self.high_stakes:
            state["high_stakes"] = self.high_stakes

        self.states[self.board] = state

    def analyze(self) -> Tuple[int, int]:
        for i, s in enumerate(self.board):
            if s == " ":
                self.legal_moves.append(i)
                wins, ties = build_state_tree(
                    self.board[:i] + self.move + self.board[i + 1 :],
                    self.other,
                    self.states,
                )
                if wins:
                    self.win_moves[i] = wins
                    self.total_wins += wins

                if ties:
                    self.tie_moves[i] = ties
                    self.total_ties += ties

                if (wins := wins - ties) > 0:
                    self.high_stakes[i] = wins

        self.set_board_state()
        return self.total_wins, self.total_ties


def build_state_tree(board: str, move: str, states: dict) -> Tuple[int, int]:
    if board in states:
        return states[board]["wins"], states[board]["ties"]

    over, winner = check_state(board)
    if over:
        states[board] = {
            "over": True,
            "repr": [board[i : i + 3] for i in (0, 3, 6)],
            "wins": (wins := int(winner == "O")),
            "ties": (ties := int(winner is None)),
        }
        return wins, ties

    return Board_Analyzer(board, move, states).analyze()


build_state_tree(" " * 9, "O", STATES_P1)
build_state_tree(" " * 9, "X", STATES_P2)

STATES_P1 = dict(
    sorted(
        STATES_P1.items(), key=lambda x: (x[1]["over"], -x[1]["wins"] - x[1]["ties"])
    )
)
STATES_P2 = dict(
    sorted(
        STATES_P2.items(), key=lambda x: (x[1]["over"], -x[1]["wins"] - x[1]["ties"])
    )
)
Path(f"{FOLDER}/Data/tic-tac-toe-states-p1.json").write_text(
    json.dumps(STATES_P1, indent=4)
)
Path(f"{FOLDER}/Data/tic-tac-toe-states-p2.json").write_text(
    json.dumps(STATES_P2, indent=4)
)
Path(f"{FOLDER}/Data/tic-tac-toe-states-p1-counter.pkl").write_bytes(
    pickle.dumps(STATES_P1, protocol=pickle.HIGHEST_PROTOCOL)
)
Path(f"{FOLDER}/Data/tic-tac-toe-states-p2-counter.pkl").write_bytes(
    pickle.dumps(STATES_P2, protocol=pickle.HIGHEST_PROTOCOL)
)


def convert_weights(dic: dict, key: str) -> None:
    if val := dic.get(key):
        moves, weights = zip(*val.items())
        dic[key] = (moves, tuple(accumulate(weights)))


for v in STATES_P1.values():
    v.pop("repr")
    convert_weights(v, "win_moves")
    convert_weights(v, "tie_moves")
    convert_weights(v, "high_stakes")

Path(f"{FOLDER}/Data/tic-tac-toe-states-p1.pkl").write_bytes(
    pickle.dumps(STATES_P1, protocol=pickle.HIGHEST_PROTOCOL)
)

for v in STATES_P2.values():
    v.pop("repr")
    convert_weights(v, "win_moves")
    convert_weights(v, "tie_moves")
    convert_weights(v, "high_stakes")

Path(f"{FOLDER}/Data/tic-tac-toe-states-p2.pkl").write_bytes(
    pickle.dumps(STATES_P2, protocol=pickle.HIGHEST_PROTOCOL)
)
assert not {"".join(e) for e in VALID_BOARDS} - set(STATES_P1) - set(STATES_P2)
