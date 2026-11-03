from readchar import readkey, key
from termcolor import colored
from typing import Union
import sys
import os
import re

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

    # removing non-string autocomplete options, just in case
    autocompleteList = [option for option in autocompleteList if type(option) is str]

    print(prompt, end='', flush=True)
    
    lastAutocomplete = ""
    autocomplete_pos = -1 # using arrow keys up and down to cycle through autocomplete list
    string = ""
    while True: 
        char = readkey()

        # multiple-character keys like the arrow keys
        if 1 < len(char):
            # cycling through the autocomplete list with up/down
            if char in [key.UP, key.DOWN]:
                if char == key.UP:
                    autocomplete_pos += 1
                    if len(autocompleteList) - 1 < autocomplete_pos:
                        autocomplete_pos = 0
                if char == key.DOWN:
                    autocomplete_pos -= 1
                    if autocomplete_pos < 0:
                        autocomplete_pos = len(autocompleteList) - 1

                if autocompleteList:
                    # removing last autocomplete
                    print(' ' * len(lastAutocomplete) + '\b' * len(lastAutocomplete), end = '', flush=True)
                    # removing previous input for string and moving cursor to beginning position
                    print('\b' * len(string) + ' ' * len(string) + '\b' * len(string), end = '', flush=True)
                    string = autocompleteList[autocomplete_pos]
                    print(string, end = '', flush=True)

                continue
                

        # confirmed input
        if char == key.ENTER:
            print()
            return string

        # tab and backspace are treated separately from the other characters
        # (esc is ignored if exitOnEsc is False)
        printChar = True

        # exiting by pressing Esc
        if char == key.ESC: 
            # exit if active
            if exitOnEsc:
                return None
            # otherwise ignore the character
            else: 
                printChar = False

        # removing previous autocomplete
        print(' ' * len(lastAutocomplete) + '\b' * len(lastAutocomplete), end = '', flush=True)

        # tab (for autocomplete)
        if char == key.TAB:
            if string != "":
                string += lastAutocomplete
                print(colored(lastAutocomplete, inputColor), end='', flush=True)
            elif len(autocompleteList) != 0:
                string = autocompleteList[0]
                print(colored(string, inputColor), end='', flush=True)

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
            # searches for first autocomplete option that starts with the inputted string
            # the string != complete is so that when the string is one of the existing options, it autocompletes to the next match
            lastAutocomplete = next((complete for complete in autocompleteList if complete.startswith(string) and string != complete), "")[len(string):]
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

def stripANSIfromText(text: str):
    """Strips ANSI escape codes from text (such as the codes for writing to console in different colors, or moving the cursor to specific coordinates).
    
    Args:
        text (str): text to be stripped of ANSI escape codes.

    Returns:
        str: text stripped of ANSI escape codes.

    """
    # regular expression for ANSI escape codes
    ansiEscape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    return ansiEscape.sub('', text)

def waitForEnter():
    """Waits for the enter key to be pressed (for "Press enter to continue" messages)."""
    while not readchar() == key.ENTER:
        pass
