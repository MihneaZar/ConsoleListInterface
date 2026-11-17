from typing import Callable, Union, Optional
from readchar import readkey, key
from termcolor import colored
import sys
import os
import re

def autocomplete(autocompleteList: list[str] = [], updateAutocomplete: Callable[[str], Optional[list[str]]] = None, prompt: str = "", inputColor: Union[str, tuple[int, int, int]] = "light_grey", 
                 autocompleteColor: Union[str, tuple[int, int, int]] = "white", supressColorWarning: bool = False, exitOnEsc: bool = False):
    """Function for console input with autocomplete feature.
    
    Args:
        autocompleteList (list[str]): list of possible autocomplete candidates.

        updateAutocomplete (str -> list[str]): function for updating the autocomplete list based on current input string.
                                               Will be called on all accepted key strokes other than left-right arrow keys (which don't change the string).
                                               If the function returns a list of strings, that list of strings overwrites the autocomplete list.
                                               Otherwise, the autocomplete list remains unchanged.

        prompt (str): the prompt for the user input.

        inputColor (str | (int, int, int)): the color for the user-inputed text (the default is the standard console light gray).
                                            If string, must be compatible with termcolor.colored.
                                            If int tuple, it will be the RGB values.

        autocompleteColor(str | (int, int, int)): the color for the autocomplete text (default is white).
                                                  If string, must be compatible with termcolor.colored.
                                                  If int tuple, it will be the RGB values.

        supressColorWarning (bool): set this to True if the 'grey' color option prints visibly in the terminal, 
                                    in order to supress the warning for it.

        exitOnEsc (bool): allows exiting this function by pressing ESC (function returns None).
    
    Returns:
        The entered input, or None if Esc was pressed and exitOnEsc is True.
    
    """
    if not supressColorWarning and "grey" in [inputColor, autocompleteColor]:
        cls()
        moveCursor(0, 0)
        print("autocomplete warning: termcolor 'grey' may not be visible in the terminal.")
        print("Consider changing it to 'light_grey' - the standard color of text in terminal.")
        print("Otherwise, use 'supressColorWarning=True' to supress this warning.\n")
        print("Press enter to continue.\n")
        waitForEnter()

    # removing non-string autocomplete options and empty automcomplete options, just in case
    autocompleteList = [option for option in autocompleteList if type(option) is str and (option and not option.isspace())]

    print(prompt, end='', flush=True)
    
    lastAutocomplete    = ""
    currentAutocomplete = ""
    autocompletePos = -1 # using arrow keys up and down to cycle through all autocomplete option which include string
    stringPos = 0 # position for moving left and right through string 
    string = ""
    while True: 
        char = readkey()

        # not printing special keys (backspace, tab, arrow keys)
        printChar = True

        # 1 < len(char) for multiple-character keys like the arrow keys 
        if 1 < len(char):
            # moving left/right through string
            if char in [key.LEFT, key.RIGHT]:
                if char == key.LEFT:
                    if 1 <= stringPos:
                        print('\b', end='', flush=True)
                        stringPos -= 1
            
                if char == key.RIGHT:
                    if stringPos <= len(string) - 1:
                        print(string[stringPos], end='', flush=True)
                        stringPos += 1
            
                continue

            # cycling through the autocomplete list with up/down
            if char in [key.UP, key.DOWN]:
                if autocompletePos == -1: # new up/down cycle
                    upDownMatches = [option for option in autocompleteList if string in option]

                if char == key.UP:
                    autocompletePos += 1
                    if len(upDownMatches) - 1 < autocompletePos:
                        autocompletePos = 0
                if char == key.DOWN:
                    autocompletePos -= 1
                    if autocompletePos < 0:
                        autocompletePos = len(upDownMatches) - 1

                # at least two autocomplete matches to cycle between or string is not already equal to the singular match
                if 2 <= len(upDownMatches) or (upDownMatches and string != upDownMatches[0]):
                    # removing last autocomplete
                    print(string[stringPos:] + ' ' * len(lastAutocomplete) + '\b' * len(lastAutocomplete), end='', flush=True)
                    # removing previous input for string and moving cursor to beginning position
                    print('\b' * len(string) + ' ' * len(string) + '\b' * len(string), end='', flush=True)
                    string = upDownMatches[autocompletePos]
                    print(string, end='', flush=True)

                    stringPos = len(string)

                # printChar = False rather than continue so that the next autocomplete option can be shown
                # (think 'test' and 'testing')
                printChar = False

            # ignoring all other multiple-character keys
            else:
                continue

        elif char != key.ESC: # ignoring ESC when exitOnEsc is False
            # reseting up/down cycle if arrow keys are not pressed
            # even if it is left/right being pressed, those are the only ones which don't change the actual string
            autocompletePos = -1


        # confirm input
        if char == key.ENTER:
            print()
            return string

        # exiting by pressing Esc
        if char == key.ESC: 
            # exit if active
            if exitOnEsc:
                return None
            # otherwise ignore the character
            else: 
                continue


        # first, changing the input string based on key
        # tab (for autocomplete)
        if char == key.TAB:
            stringPos = len(string) # stringPos will save the position from where the autocomplete was triggered
        
            if string != "":
                string += lastAutocomplete
            elif autocompleteList:
                string = autocompleteList[0]

        # backspace
        elif char == key.BACKSPACE:
            # only allow backspace when string is not empty and when not in the first position in string
            if 1 <= stringPos:
                string = string[:stringPos - 1] + string[stringPos:]

        # normal char to be printed
        # ctrl+j is '\n' and that fucks things up
        elif char not in [key.UP, key.DOWN, '\n']:
            string = string[:stringPos] + char + string[stringPos:]


        # update autocompleteList
        if updateAutocomplete:
            newAutocomplete = updateAutocomplete(string)
            if newAutocomplete:
                autocompleteList = newAutocomplete
                autocompletePos = -1 # if the autocomplete list is updated, the previous up/down position is not valid anymore
                
        # find next autocomplete option
        if string:
            # searches for first autocomplete option that starts with the inputted string
            # the string != complete is so that when the string is one of the existing options, it autocompletes to the next match
            currentAutocomplete = next((complete for complete in autocompleteList if complete.startswith(string) and string != complete), "")[len(string):]
            # input(string)
            # input(lastAutocomplete)

        # delete autocomplete when string becomes empty
        else:
            currentAutocomplete = ""


        # printing the changes to string and to the autocomplete
        if char == key.TAB:
            print(colored(string[stringPos:], inputColor), end='', flush=True)
            if currentAutocomplete: 
                print(colored(currentAutocomplete, autocompleteColor) + '\b' * len(currentAutocomplete), end='', flush=True)
            stringPos = len(string)

        # backspace
        elif char == key.BACKSPACE:
            # only allow backspace when string is not empty and when not in the first position in string
            if 1 <= stringPos: 
                # treating backspace at the very end separately, since it functions differently
                if stringPos == len(string) + 1: 
                    # autocomplete option has been changed
                    if lastAutocomplete != currentAutocomplete[1:]:
                        print(' ' * len(lastAutocomplete) + '\b' * len(lastAutocomplete), end='', flush=True)
                    # the actual deletion of the character
                    print('\b \b', end='', flush=True)
                    if currentAutocomplete:
                        print(colored(currentAutocomplete[0] + '\b', autocompleteColor), end='', flush=True)

                else:
                    # removing the tail end of the string (after the backspace) and the previous autocomplete
                    replaceString = ' ' * (len(string) - stringPos + 1) + ' ' * len(lastAutocomplete) + '\b' * len(lastAutocomplete) + '\b' * (len(string) - stringPos + 2)

                    # re-adding tail end without deleted character
                    replaceString += colored(string[stringPos - 1:], inputColor)

                    # adding new autocomplete option
                    replaceString += colored(currentAutocomplete, autocompleteColor)

                    # returning to actual position in string
                    replaceString += '\b' * (len(string) - stringPos + 1 + len(currentAutocomplete))

                    # printing it all in one go to avoid glitchiness
                    print(replaceString, end='', flush=True)

                stringPos -= 1

        elif char not in [key.UP, key.DOWN, '\n']:
            # treating characters being added at the very end separately, since it functions differently
            if stringPos == len(string) - 1: 
                # autocomplete option has been changed
                if lastAutocomplete[1:] != currentAutocomplete:
                    print(' ' * len(lastAutocomplete) + '\b' * len(lastAutocomplete), end='', flush=True)
                print(colored(char, inputColor) + colored(currentAutocomplete, autocompleteColor) + '\b' * len(currentAutocomplete), end='', flush=True)

            else:
                # for priting the string from where the character was added, then the new autocomplete 
                replaceString = colored(string[stringPos:], inputColor) + colored(currentAutocomplete, autocompleteColor)

                # clearing the previous autocomplete option if it's longer than the current one plus the new character added
                if len(currentAutocomplete) + 1 < len(lastAutocomplete):
                    lengthDiff = len(lastAutocomplete) - len(currentAutocomplete) - 1
                    replaceString += ' ' * lengthDiff + '\b' * lengthDiff

                # returning to current position in string
                replaceString += '\b' * (len(string) - stringPos - 1 + len(currentAutocomplete))

                # printing it all in one go to avoid glitchiness
                print(replaceString, end='', flush=True)

            stringPos += 1

        lastAutocomplete = currentAutocomplete

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
    while not readkey() == key.ENTER:
        pass
