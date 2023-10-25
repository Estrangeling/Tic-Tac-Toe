import re
import importlib
import inspect
from pathlib import Path
from types import FunctionType
from typing import Any


files = [
    "advanced",
    "analyze_tic_tac_toe_states",
    "animation",
    "basics",
    "basic_data",
    "blend_modes",
    "code_check",
    "color",
    "control",
    "gamecontrol",
    "logic",
    "main",
    "preview",
    "shared",
    "theme",
]

modules = {}

FOLDER = str(Path(__file__).parent).replace("\\", "/")
FUNCTIONS = {}


def analyze_function(func: FunctionType) -> None:
    annotations = func.__annotations__
    code = func.__code__
    FUNCTIONS[func.__qualname__] = {
        "annotated": bool(annotations),
        "annotations": {
            k: (s[8:-2] if (s := str(v))[0] == "<" else s)
            for k, v in annotations.items()
        },
        "return_annotated": "return" in annotations,
        "unannotated_vars": [
            name
            for name in code.co_varnames[: code.co_argcount]
            if name != "self" and name not in annotations
        ],
        "false_void": annotations.get("return", False) is None
        and re.match("\breturn\b", inspect.getsource(func)),
    }


def is_custom_function(
    obj: Any, kind: type[FunctionType] | type[staticmethod], module: str = "preview"
) -> bool:
    return isinstance(obj, kind) and obj.__module__ == module


s = 0
for file in files:
    print(file)
    script = Path(f"{FOLDER}/{file}.py").read_text()
    l = len(script)
    s += l
    print(f"Character Count: {l}")
    print(f"Nonsspace count: {sum(not c.isspace() for c in script)}")
    lines = script.splitlines()
    print(f"Line count: {len(lines)}")
    class_count = 0
    if file != "code_check":
        for obj in importlib.import_module(file).__dict__.values():
            if inspect.isclass(obj) and obj.__module__ == file:
                class_count += 1
                for key, attr in obj.__dict__.items():
                    if is_custom_function(attr, FunctionType, file):
                        analyze_function(attr)
                    elif is_custom_function(attr, staticmethod, file):
                        analyze_function(getattr(obj, key))

            elif is_custom_function(obj, FunctionType):
                analyze_function(obj)

    print(f"class count: {class_count}")
    print(f"function count: {len(FUNCTIONS)}")
    print(f"Non-blank line count: {sum(bool(line) for line in lines)}")
    print(f"Code characters count: {sum(len(line.rstrip()) for line in lines)}")
    print()
    print("functions with type hint errors")
    errors = 0
    for key, val in FUNCTIONS.items():
        if (
            val["unannotated_vars"]
            or not val["annotated"]
            or not val["return_annotated"]
            or val["false_void"]
        ):
            errors += 1
            print(key)

    print(f"No functions with type hint errors: {not errors}")
    FUNCTIONS.clear()
    print()
    print()

print(s)
