import pickle
import random
from bisect import bisect
from collections import Counter, defaultdict
from pathlib import Path
from typing import Tuple

FOLDER = str(Path(__file__).parent).replace("\\", "/")
MENACE_MEMORY = (
    pickle.loads(file.read_bytes())
    if (file := Path(f"{FOLDER}/Data/menace-memory.pkl")).is_file()
    else defaultdict(Counter)
)
MOVESETS = ("high_stakes", "win_moves", "tie_moves")
STATES_P1 = pickle.loads(Path(f"{FOLDER}/Data/tic-tac-toe-states-p1.pkl").read_bytes())
STATES_P2 = pickle.loads(Path(f"{FOLDER}/Data/tic-tac-toe-states-p2.pkl").read_bytes())
STATES_P1_COUNTER = pickle.loads(
    Path(f"{FOLDER}/Data/tic-tac-toe-states-p1-counter.pkl").read_bytes()
)
STATES_P2_COUNTER = pickle.loads(
    Path(f"{FOLDER}/Data/tic-tac-toe-states-p2-counter.pkl").read_bytes()
)

LINES = (
    (0, 3, 1),
    (3, 6, 1),
    (6, 9, 1),
    (0, 7, 3),
    (1, 8, 3),
    (2, 9, 3),
    (0, 9, 4),
    (2, 7, 2),
)


def check_state(board: str) -> Tuple[bool, str, range]:
    for start, stop, step in LINES:
        line = board[start:stop:step]
        if len(set(line)) == 1 and (winner := line[0]) in {"O", "X"}:
            return True, winner, range(start, stop, step)

    return " " not in board, None, None


class Menace:
    deltas = {"Win": 5, "Tie": 1, "Loss": -1}
    boards = []
    moves = []

    @staticmethod
    def get_move(board: str) -> int:
        Menace.boards.append(board)
        choices = [i for i in range(9) if board[i] == " "]
        states = MENACE_MEMORY[board]
        move = random.choices(choices, weights=[states.get(c, 1) for c in choices])[0]
        Menace.moves.append(move)
        return move

    @staticmethod
    def back_propagate(state: str) -> None:
        delta = Menace.deltas[state]
        for board, move in zip(Menace.boards, Menace.moves):
            weight = MENACE_MEMORY[board][move]
            MENACE_MEMORY[board][move] = max(weight + delta, 1)

        Menace.boards.clear()
        Menace.moves.clear()


def fill_line(board: str, piece: str) -> int:
    for start, end, step in LINES:
        line = board[start:end:step]
        if line.count(piece) == 2 and " " in line:
            return start + line.index(" ") * step


def fill_move(board: str) -> int:
    for p in ("O", "X"):
        if (pos := fill_line(board, p)) is not None:
            return pos

    return random.choice([i for i, p in enumerate(board) if p == " "])


def stochastic_move(board: str, states: dict, low_stakes: bool = True) -> int:
    for p in ("O", "X"):
        if (pos := fill_line(board, p)) is not None:
            return pos

    state = states[board]
    for moveset in MOVESETS[low_stakes:]:
        if entry := state.get(moveset):
            moves, weights = entry
            return moves[bisect(weights, random.random() * weights[-1])]

    return random.choice(state["legal_moves"])


def optimal_move(board: str, states: dict, low_stakes: bool = True) -> int:
    for p in ("O", "X"):
        if (pos := fill_line(board, p)) is not None:
            return pos

    state = states[board]
    for moveset in MOVESETS[low_stakes:]:
        if entry := state.get(moveset):
            return entry.most_common()[0][0]

    return random.choice(state["legal_moves"])


OTHER_PIECE = {"O": "X", "X": "O"}


class Game_Board:
    def __init__(self) -> None:
        self.choices = list(range(9))
        self.state = [" "] * 9

    @property
    def state_string(self) -> str:
        return "".join(self.state)

    @property
    def alternate_state(self) -> str:
        return "".join(OTHER_PIECE.get(i, i) for i in self.state)

    def submit(self, choice: int, player: str) -> None:
        self.choices.remove(choice)
        self.state[choice] = player

    def reset(self) -> None:
        self.__init__()
