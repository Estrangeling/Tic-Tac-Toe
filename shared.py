import numpy as np
from basic_data import *
from copy import deepcopy
from itertools import cycle
from logic import STATES_P1, STATES_P2, STATES_P1_COUNTER, STATES_P2_COUNTER
from theme import *
from PIL import Image

BLACK = """QLabel#Disabled {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 0.75, x3: 0, y3: 1, stop: 0 #000000, stop: 0.75 #808080, stop: 1 #000000);
    color: #ffffff;
    border: 3px outset #202020;
    border-radius: 6px;
}"""

X = bytearray(np.array(Image.open(f"{FOLDER}/icons/X.png")))
O = bytearray(np.array(Image.open(f"{FOLDER}/icons/O.png")))
RUN = cycle(["Stop", "Start"])
PAUSE = cycle(["Resume", "Pause"])
STATES = (STATES_P1, STATES_P2)
COUNTER_STATES = (STATES_P1_COUNTER, STATES_P2_COUNTER)
SEXDECIM = ["High"] + ["Mock"] * 15
SEXTET = ("Cell", "Hover", "P1", "P2", "P1Win", "P2Win")
NONSENSE = [
    "Lorem",
    "ipsum",
    "dolor",
    "sit",
    "amet",
    "consectetur",
    "adipiscing",
    "elit",
    "sed",
    "do",
    "eiusmod",
    "tempor",
    "incididunt",
    "ut",
    "labore",
    "et",
]

PLAYERINFO = {
    "PX": ["PO", "cross", STATES_P1, STATES_P2],
    "PO": ["PX", "nought", STATES_P1_COUNTER, STATES_P2_COUNTER],
}
CONTROL = (
    ("Default", "restore_default"),
    ("OK", "apply_style"),
    ("Cancel", "revert_style"),
)
QUADDRUPLE = (
    "game",
    "turn",
    "active",
    "winner",
)
STYLIZER = Style_Combiner(CONFIG)
NONSENSE_COPY = NONSENSE.copy()
TRINITY = ["Base", "Hover", "Pressed"]
BUTTONS = TRINITY * 5
BUTTONS_COPY = BUTTONS.copy()
CHECKBOX_STATES = [(t, i) for i in (0, 1) for t in TRINITY]
CHECKBOXES = CHECKBOX_STATES * 3
CHECKBOXES_COPY = CHECKBOXES.copy()
RADIOBUTTONS = CHECKBOX_STATES * 2
RADIOBUTTONS_COPY = RADIOBUTTONS.copy()
CONFIG_COPY = deepcopy(CONFIG)


PLAYER_NAMES = (
    "Human",
    "Novice AI",
    "Adept AI",
    "Master AI",
    "Master AI+",
    "Super AI",
    "Super AI+",
)

PLAYERS = {
    "players": PLAYER_NAMES,
    "opponents": {
        k: PLAYER_NAMES[:i] + PLAYER_NAMES[i + 1 :] for i, k in enumerate(PLAYER_NAMES)
    },
}

BORDER_STYLES = (
    "dotted",
    "dashed",
    "solid",
    "double",
    "groove",
    "ridge",
    "inset",
    "outset",
    "none",
    "hidden",
)
