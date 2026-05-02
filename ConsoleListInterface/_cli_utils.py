from readchar import readchar, key
import sys
import os 

def moveCursor(y: int, x: int):
    """Function for moving the cursor to a different position in the console.

    Args:
        y (int): column in console (characters).
        x (int): line in console (characters).

    """

    sys.stdout.write("\033[%d;%dH" % (max(y, 0), max(x, 0)))

# clear screen function
cls = lambda: os.system('cls' if os.name=='nt' else 'clear')

# set title of terminal window
setTitle = (lambda title: os.system(f'title {title}')) if os.name=='nt' else (sys.stdout.write(f"\x1b]2;{title}\x07"))

def lowercaseKey(key: str):
    """Transforms a key to lowercase without affecting multi-character keys like the arrows.

    Args:
        key (str): key to convert.

    Returns:
        str: key converted to lowercase.
        
    """

    return key.lower() if len(key) == 1 else key

def waitForEnter():
    """Waits for the enter key to be pressed (for "Press enter to continue" messages)."""
    while not readchar() == key.ENTER:
        pass


