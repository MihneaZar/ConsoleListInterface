from readchar import readchar, key
from termcolor import colored
from typing import Union
import sys
import os 

def autocomplete(autocompleteList: list[str] = [], prompt: str = "", inputColor: Union[str, tuple[int, int, int]] = "light_grey", 
                 autocompleteColor: Union[str, tuple[int, int, int]] = "white", exitOnEsc: bool = False):
    """Function for console input with autocomplete feature.
    
    Args:
        autocompleteList (list[str]): list of possible autocomplete candidates.

        prompt (str): the prompt for the user input.

        inputColor (str | (int, int, int)): the color for the user-inputed text (the default is the standard console light gray).
                                            If string, must be compatible with termcolor.colored.
                                            If int tuple, it will be the RGB values.

        autocompleteColor(str | (int, int, int)): the color for the autocomplete text (default is white).
                                                  If string, must be compatible with termcolor.colored.
                                                  If int tuple, it will be the RGB values.

        exitOnEsc (bool): allows exiting this function by pressing ESC (function returns None).
    
    Returns:
        The entered input, or None if Esc was pressed and exitOnEsc is True.
    
    """

    print(prompt, end='', flush=True)
    
    lastAutocomplete = ""
    string = ""
    while True: 
        char = readchar()

        # confirmed input
        if char == key.ENTER:
            print()
            return string

        # exiting by pressing Esc, if active
        if char == key.ESC and exitOnEsc:
            return None

        # tab and backspace are treated separately from the other characters
        printChar = True

        # removing previous autocomplete
        print(' ' * len(lastAutocomplete) + '\b' * len(lastAutocomplete), end = '', flush=True)

        # tab (for autocomplete)
        if char == key.TAB:
            string += lastAutocomplete
            print(colored(lastAutocomplete, inputColor), end='', flush=True)
            printChar = False

        # backspace
        if char == key.BACKSPACE:
            if string != "": # only allow backspace when string is not empty!!
                string = string[:-1]
                print("\b \b", end='', flush=True)
                    
            printChar = False

        # normal char to be printed
        if printChar:
            print(colored(char, inputColor), end='', flush=True)
            string += char

        # update autocomplete and print it
        if string:
            lastAutocomplete = next((complete for complete in autocompleteList if complete.startswith(string)), "")[len(string):]
            print(colored(lastAutocomplete, autocompleteColor), end='', flush=True)
            print("\b" * len(lastAutocomplete), end='', flush=True)

def moveCursor(y: int, x: int):
    """Function for moving the cursor to a different position in the console.

    Args:
        y (int): column in console (characters).
        x (int): line in console (characters).

    """

    sys.stdout.write("\033[%d;%dH" % (max(y, 0), max(x, 0)))

# clear screen function
cls = lambda: os.system('cls' if os.name=='nt' else 'clear')

def setTitle(title: str): 
    """Sets the title of the console window.

    Args:
        title (str): the title for the window.
    
    """

    try:
        if os.name=='nt':
            os.system(f'title {title}')  
        else:
            sys.stdout.write(f"\x1b]2;{title}\x07")
    except:
        pass

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
