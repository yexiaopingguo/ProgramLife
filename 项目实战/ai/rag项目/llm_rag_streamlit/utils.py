import time
import random
from colorama import Fore, Back, Style

def print_colorful(
    *text,
    text_color=None,
    time_color=Back.GREEN + Fore.RED,
    sep: str = " ",
    end: str = "\n",
    file=None,
    flush: bool = False,
):
    timestamp = time.strftime("%y/%m/%d %H:%M:%S") + " : "
    text = sep.join(list(map(str, text)))
    text = text_color + text + Style.RESET_ALL if text_color is not None else text
    print(
        f"{time_color + timestamp + Style.RESET_ALL}{text}",
        end=end,
        file=file,
        flush=flush,
    )

def random_icon(idx=None):
    icons = "🍇🍈🍉🍊🍋🍌🍍🥭🍎🍏🍐🍑🍒🍓"  # 🐭🐁🐀🐹🐰
    n = len(icons)
    if idx is None:
        return random.sample(icons, 1)[0]
    else:
        return icons[idx % n]