import blend_modes
import json
from itertools import cycle
from logic import STATES_P1, STATES_P2_COUNTER
from pathlib import Path


SWITCH = cycle(["Stop", "Run"])
FOLDER = str(Path(__file__).parent).replace("\\", "/")
CONFIG_PATH = Path(f"{FOLDER}/config/theme.json")
CONFIG = json.loads(CONFIG_PATH.read_text())
DEFAULT_CONFIG = json.loads(Path(f"{FOLDER}/config/default_theme.json").read_text())
WIDGETS = json.loads(Path(f"{FOLDER}/config/widgets.json").read_text())
WIDGET_GROUPS = json.loads(Path(f"{FOLDER}/config/widget_groups.json").read_text())
SECRET = json.loads(Path(f"{FOLDER}/data/secret.json").read_text())
SECRET_TOO = json.loads(Path(f"{FOLDER}/data/secret_too.json").read_text())

BOX = ("background", "bordercolor", "borderstyle")
GRADIENT = (
    "qlineargradient(x1: 0, y1: 0, x2: 0, y2: 0.75, x3: 0, y3: 1, stop: 0 {lowlight}, stop: 0.75 {highlight}, stop: 1 {lowlight})",
    "qlineargradient(x1: 0, y1: 0, x2: 0.75, y2: 0, x3: 1, y3: 0, stop: 0 {lowlight}, stop: 0.75 {highlight}, stop: 1 {lowlight})",
)

NORMAL_KEYS = {
    "background",
    "bordercolor",
    "borderstyle",
    "highlight",
    "lowlight",
    "textcolor",
}

EXTRA_ATTRIBUTES = {
    "QLabel#Mock": {"margin-left": "1px"},
    "QLabel#Top": {"margin-left": "1px"},
    "DummyButton#Base": {
        "border-style": "outset",
        "border-width": "3px",
        "border-radius": "6px",
    },
    "DummyButton#Hover": {
        "border-style": "outset",
        "border-width": "3px",
        "border-radius": "6px",
    },
    "DummyButton#Pressed": {
        "border-style": "inset",
        "border-width": "3px",
        "border-radius": "6px",
    },
    "TitleBar": {"border": "0px"},
    "QTableWidget#Game::item:hover": {"margin": "4px"},
    "QScrollBar::vertical": {"width": "16px"},
    "QScrollBar::handle:vertical": {"min-height": "80px", "margin": "18px"},
    "QRadioButton#Base::indicator, QRadioButton#Hover::indicator, QRadioButton#Pressed::indicator, QRadioButton::indicator": {
        "width": "16px",
        "height": "16px",
        "border-radius": "10px",
    },
}

MOCK_MENU_BASE = """QGroupBox#Menu {{
    background: {background};
    border: 3px {borderstyle} {bordercolor};
}}
"""


BOARD_BASE = """QTableWidget {{
    background: {background};
}}
QTableWidget::item {{
    border: 3px {borderstyle} {bordercolor};
}}
"""

HOVER_LABEL_BASE = """QLabel#High, QLabel#Focus {{
    padding-left: 1px;
    margin-right: 6px;
    background: {hoverbase};
    color: {hovercolor};
}}
QLabel#High {{
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}
"""

COMBOBOX_BASE = """QComboBox {{
    border-radius: 6px;
    background: {background_1};
    border: 3px {borderstyle_1} {bordercolor_1};
    color: {textcolor};
    selection-background-color: {hoverbase};
    selection-color: {hovercolor};
}}
QComboBox QAbstractItemView {{
    border-radius: 6px;
    background: {background_2};
    border: 3px {borderstyle_2} {bordercolor_2};
}}
"""

SHAPES = (
    "Circle",
    "Triangle 0",
    "Triangle 1",
    "Triangle 2",
    "Triangle 3",
    "Square",
    "Diamond",
    "Pentagon 0",
    "Pentagon 1",
    "Pentagon 2",
    "Pentagon 3",
    "Hexagon 0",
    "Hexagon 1",
    "Ring",
    "Rhombus 0",
    "Rhombus 1",
    "Cross 0",
    "Cross 1",
    "Pentagram 0",
    "Pentagram 1",
    "Pentagram 2",
    "Pentagram 3",
    "Hexagram 0",
    "Hexagram 1",
)

BLEND_MODES = {
    "Lighten": blend_modes.blend_lighten,
    "Screen": blend_modes.blend_screen,
    "Color dodge": blend_modes.blend_color_dodge,
    "Linear dodge": blend_modes.blend_linear_dodge,
    "Darken": blend_modes.blend_darken,
    "Multiply": blend_modes.blend_multiply,
    "Color burn": blend_modes.blend_color_burn,
    "Linear burn": blend_modes.blend_linear_burn,
    "Overlay": blend_modes.blend_overlay,
    "Soft light": blend_modes.blend_soft_light,
    "Hard light": blend_modes.blend_hard_light,
    "Vivid light": blend_modes.blend_vivid_light,
    "Linear light": blend_modes.blend_linear_light,
    "Pin light": blend_modes.blend_pin_light,
    "Reflect": blend_modes.blend_reflect,
    "Difference": blend_modes.blend_difference,
    "Exclusion": blend_modes.blend_exclusion,
    "Subtract": blend_modes.blend_subtract,
    "Grain extract": blend_modes.blend_grain_extract,
    "Grain merge": blend_modes.blend_grain_merge,
    "Divide": blend_modes.blend_divide,
    "HSV color": blend_modes.blend_HSV_Color,
    "HSL color": blend_modes.blend_HSL_Color,
    "Color lux": blend_modes.blend_color_lux,
    "Color nox": blend_modes.blend_color_nox,
    "LCh D65": blend_modes.blend_color_LCh_D65,
    "LCh D50": blend_modes.blend_color_LCh_D50,
}


IMMUTABLE = """DummyButton#Base, DummyButton#Hover, QPushButton, QPushButton#P1, QPushButton#P2, SquareButton {{
    border-style: outset;
    border-width: 3px;
    border-radius: 6px;
}}
DummyButton#Pressed, QPushButton:pressed, QPushButton#P1:pressed, QPushButton#P2:pressed {{
    border-style: inset;
    border-width: 3px;
    border-radius: 6px;
}}
QPushButton:disabled {{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 0.75, x3: 0, y3: 1, stop: 0 #000000, stop: 0.75 #808080, stop: 1 #000000);
    color: #ffffff;
    border: 3px outset #202020;
}}
QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
    border: 0px;
    width: 10px;
    height: 10px;
}}
QSpinBox::up-button {{
    border-width: 0px;
}}
QSpinBox::down-button {{
    border-width: 0px;
}}
QSpinBox::down-arrow:hover, QSpinBox::up-arrow:hover {{
    background: #0000ff;
}}
QSpinBox::down-arrow:pressed, QSpinBox::up-arrow:pressed {{
    background: #404080;
}}
QComboBox::drop-down {{
    border: 0px;
    padding: 0px 0px 0px 0px;
}}
QCheckBox::indicator {{
    border: 0px;
    width: 16px;
    height: 16px;
}}
QCheckBox::indicator:unchecked, QCheckBox#Base::indicator:unchecked, QCheckBox#Hover::indicator:unchecked, QCheckBox#Pressed::indicator:unchecked  {{
    image: url({folder}/icons/checkbox-unchecked.png);
}}
QCheckBox::indicator:checked, QCheckBox#Base::indicator:checked, QCheckBox#Hover::indicator:checked, QCheckBox#Pressed::indicator:checked {{
    image: url({folder}/icons/checkbox-checked.png);
}}
QCheckBox::indicator:disabled {{
    image: url({folder}/icons/checkbox-disabled.png);
}}
QRadioButton::indicator:checked, QRadioButton#Base::indicator:checked, QRadioButton#Hover::indicator:checked, QRadioButton#Pressed::indicator:checked {{
    image: url({folder}/icons/radiobutton-checked.png)
}}
QRadioButton::indicator:unchecked, QRadioButton#Base::indicator:unchecked, QRadioButton#Hover::indicator:unchecked, QRadioButton#Pressed::indicator:unchecked {{
    image: url({folder}/icons/radiobutton-unchecked.png)
}}
QRadioButton::indicator:disabled {{
    image: url({folder}/icons/radiobutton-disabled.png)
}}
QComboBox::down-arrow {{
    image: url({folder}/icons/combobox-downarrow.png);
    width: 10px;
    height: 10px;
}}
QScrollBar::up-arrow:vertical {{
    image: url("{folder}/icons/scrollbar-uparrow.png")
}}
QScrollBar::down-arrow:vertical {{
    image: url("{folder}/icons/scrollbar-downarrow.png")
}}
QSpinBox::up-arrow, QSpinBox#Dummy::up-arrow {{
    image: url({folder}/icons/spinbox-uparrow.png);
}}
QSpinBox::down-arrow, QSpinBox#Dummy::down-arrow {{
    image: url({folder}/icons/spinbox-downarrow.png);
}}
QSpinBox::up-arrow:disabled, QSpinBox::up-arrow:off {{
    image: url({folder}/icons/spinbox-uparrow-disabled.png);
}}
QSpinBox::down-arrow:disabled, QSpinBox::down-arrow:off {{
    image: url({folder}/icons/spinbox-downarrow-disabled.png);
}}
""".format(
    folder=FOLDER
)


GLOBALS = {
    "pause": False,
    "run": False,
    "rungame": False,
    "popup": False,
    24: SECRET[0].copy(),
    15: SECRET_TOO[0].copy(),
    "24": cycle(range(24)),
    "15": cycle(range(15)),
    "PX": {
        "states": STATES_P1,
        "id": "P1",
        "name": "Master AI",
        "opponent": "PO",
        "stats": {"Win": 0, "Loss": 0, "Tie": 0},
    },
    "PO": {
        "states": STATES_P2_COUNTER,
        "id": "P2",
        "name": "Super AI",
        "opponent": "PX",
        "stats": {"Win": 0, "Loss": 0, "Tie": 0},
    },
    "game_count": 0,
    "turn_count": 0,
    "active": "Master AI",
    "winner": "null",
    "live_active": "Human",
    "live_game_count": 0,
    "live_turn_count": 0,
    "live_winner": "null",
    "order": ("cross", "nought"),
    "player_order": ["PX", "PO"],
    "game_player_order": ["Human", "Master AI"],
    "new_order": ["PX", "PO"],
    "groups": {
        "Board": [True, True],
        "Button": [True, True],
        "CheckBox": [True, True],
        "ComboBox": [True, True],
        "LineEdit": [True, True],
        "Miscellaneous": [True, True],
        "RadioButton": [True, True],
        "ScrollArea": [True, True],
        "SpinBox": [True, True],
    },
    "revertcheckboxes": {},
    "animate": {
        "Board": [True, "animate_game"],
        "Button": [True, "animate_buttons"],
        "CheckBox": [True, "animate_checkbox"],
        "ComboBox": [True, "animate_combobox"],
        "LineEdit": [True, "animate_lineedit"],
        "RadioButton": [True, "animate_radiobuttons"],
        "SpinBox": [True, "animate_spinbox"],
    },
    "revertible": False,
    "orderchanged": False,
}
