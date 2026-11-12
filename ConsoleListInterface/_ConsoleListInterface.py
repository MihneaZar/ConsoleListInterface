from ConsoleListInterface._cli_utils import moveCursor, lowercaseKey, waitForEnter, cls, setTitle, autocomplete, stripANSIfromText
from typing import Callable, Any, Optional, Union
from readchar import readkey, key
from math import ceil as roundup
from termcolor import colored
from inspect import signature
from time import sleep
import cursor
import os

DEFAULTHELP = """
This is a help page example.

Controls:
    - arrow keys -> moving between items in the list.
    - character  -> move cursor to the next item which starts with character.
    - ctrl+f     -> search for the next item which contains string.
    - '\\'        -> find next item that contains string.
    - enter      -> choose selected item.
    - ctrl+n     -> create new list item.
    - ctrl+r     -> rename selected item.
    - delete     -> delete selected item.
    - ctrl+u     -> update printed list (if list or console size was changed).
    - '='/'-'    -> increase/decrease length of item names before they are cut off.
    - '?'        -> display current help page.
    - escape     -> quit application.
""" 

class ConsoleListInterface:
    """Class for interacting with the console list, an interface for selecting and searching in a list printed to the console.
    
    The default commands are explained in the DEFAULTHELP help page.
    Special commands (enter, escape) can be changed through the specialCommands parameter. 

    While in most cases it would make more sense for the list items to be sorted, they do not have to be.
    The list can have repeat values, next to each other or otherwise.
    Any newlines in item names are ignored because they cause undefined behaviour.

    Important note: All commands are changed to and treated in lowercase, to avoid confusion.
    """

    # the ( -> /    ) before list items
    _SPACESBEFORE = 4 

    # the minimum width of item names
    _MINNAMEWIDTH = 8

    # the commands recognized by default by the interface
    # the interface will ignore them if they are passed to the specialCommands list
    # and they can be rebound to other keys through the rebindCommands dictionary
    _INTERNALCOMMANDS = [key.UP, key.DOWN, key.LEFT, key.RIGHT, key.CTRL_F, '\\', key.CTRL_N, key.CTRL_R, key.DELETE, key.CTRL_U, '=', '-', '?']


    def defaultPrintFunc(item: str, maxNameWidth: int, itemColor: Union[str, tuple[int, int, int]]):
        """Default printing function for item names.

        Args:
            item (str): the full name of the item.
            maxNameWidth (int): the total number of characters that the printed name can have (otherwise it will get cut-off).
            itemColor (str | (int, int, int)): the color for the list items.
                                               If string, must be compatible with termcolor.colored.
                                               If int tuple, it will be the RGB values.

        Returns:
            The truncated name.

        """
        if len(item) <= maxNameWidth:
            itemName = colored(item, itemColor)
        else:
            itemName = colored(item[:maxNameWidth - 1] + '-', itemColor)

        return itemName


    def __init__(self, items: list[str] = [], specialCommands: list[str] = [key.ENTER, key.ESC], rebindCommands: dict[str, str] = {}, startPos: int = 0, 
                 shownColumns: int = 3, printFunc: Callable[[str, int], int] = defaultPrintFunc, helpPage: str = DEFAULTHELP, disableHelp: bool = False, 
                 topTextColor: Union[str, tuple[int, int, int]] = 'light_grey', itemColor: Union[str, tuple[int, int, int]] = 'light_grey', 
                 helpSearchColor: Union[str, tuple[int, int, int]] = 'light_grey', dontPrintList: bool = False, supressColorWarning: bool = False):
        """Intializes console interface.

        Args:
            items (list[str]): complete list of selectable items.
            
            specialCommands (list[str]): the commands that will be outputted from the 'interact' method; if empty, method will be stuck in an infite loop.
                                         Additionally, internal commands passed in this list will be ignored by the interface and returned by the 'interact' method.

            rebindCommands (str: str): dictionary for rebinding internal commands to other keys (e.g. rebindCommands[key.CTRL_F] = key.CTRL_S will bind searching by string to ctrl+s instead of ctrl+f). 
                                      Binding multiple commands to the same key will lead to only one of them being detected.

            startPos (int): current position in list, by default the first element.

            shownColumns (int): number of columns to be shown at a time in the console (by default 3).

            printFunc ((str, int, str | (int, int, int)) -> str): custom function for printing the item names.
                                                                  If it has one parameter, it is just the item to be printed.
                                                                  If it has two parameters, the second one is the maximum name width before cut-off.
                                                                  If it has three parameters, the third one is the color for the list items.

            helpPage (str): user instructions for all application commands.

            disableHelp (bool): disable the "Type '?' for help page." message and help page printing.

            topTextColor (str | (int, int, int)): the color for the text displayed above the list (the default is the standard console light gray).
                                                  If string, must be compatible with termcolor.colored.
                                                  If int tuple, it will be the RGB values.

            itemColor (str | (int, int, int)): the color for the list items (the default is the standard console light gray).
                                               If string, must be compatible with termcolor.colored.
                                               If int tuple, it will be the RGB values.
                                               
            helpSearchColor (str | (int, int, int)): the color for the help-page and search messages (the default is the standard console light gray).
                                                     If string, must be compatible with termcolor.colored.
                                                     If int tuple, it will be the RGB values.

            dontPrintList (bool): set True to stop the list from being printed on __init__.

            supressColorWarning (bool): set this to True if the 'grey' color option prints visibly in the terminal, 
                                        in order to supress the warning for it.

        Returns:
            ConsoleListInterface object.

        """
        if not supressColorWarning and "grey" in [topTextColor, itemColor, helpSearchColor]:
            cls()
            moveCursor(0, 0)
            print("ConsoleListInterface.__init__ warning: termcolor 'grey' may not be visible in the terminal.")
            print("Consider changing it to 'light_grey' - the standard color of text in terminal.")
            print("Otherwise, use 'supressColorWarning=True' to supress this warning.\n")
            print("Press enter to continue.\n")
            waitForEnter()

        if items == None:
            items = []

        self._topText = ""

        self._consoleWidth   = os.get_terminal_size()[0] 
        self._itemsPerColumn = max(os.get_terminal_size()[1] - 2 - self._getLinesOfSetText() + 1, 1) # help page message, then startPrintLine

        self._separateInteractionPos = max(int(os.get_terminal_size()[1] / 2) - 4, 0)
        
        self._shownColumns = shownColumns
        self._maxNameWidth = int(self._consoleWidth / self._shownColumns) - self._SPACESBEFORE

        self._column = int((startPos) / self._itemsPerColumn) + 1
        self._line   = (startPos) % self._itemsPerColumn + 1
        
        self._leftmostColumn = max(self._column - self._shownColumns + 1, 1)

        self._items           = [item.replace('\n', '') for item in items] # accidental '\n' fucks up printing
        self._specialCommands = [lowercaseKey(command) for command in specialCommands]
        self._commandBind     = {command: (command if command not in rebindCommands else lowercaseKey(rebindCommands[command])) for command in self._INTERNALCOMMANDS}
        self._actualCommands  = self._commandBind.values() # all the values that internal commands are bound to
        self._printFunc       = printFunc
        self._helpPage        = helpPage
        self._disableHelp     = disableHelp
        self._topTextColor    = topTextColor
        self._itemColor       = itemColor
        self._helpSearchColor = helpSearchColor

        self._totalColumns      = roundup(len(self._items) / self._itemsPerColumn)
        self._lastColumnHeight  = len(self._items) % self._itemsPerColumn

        if self._lastColumnHeight == 0:
            self._lastColumnHeight = self._itemsPerColumn
                        
        if not self._items:
            self._totalColumns     = 1
            self._lastColumnHeight = 1

        self._searchStr = None # saved search string for repeated searches

        cursor.hide()

        if not dontPrintList:
            self.printList()


    def _getPos(self):
        """Calculates the absolute position in the list based on the current line and column.
        
        Returns:
            int: position in the list of items.

        """
        return (self._column - 1) * self._itemsPerColumn + self._line - 1

    def _getLinesOfSetText(self):
        """Calculates the number of lines of the text set at top. 
        
        Returns:
            int: the number of lines of the text set at the top.

        """
        # fixed this calculation, for each separate line, it's the number of times it is over the terminal width
        # ANSI escape codes are removed from each line, to avoid counting them as overflow (since they aren't actual characters printed to console)
        return self._topText.count('\n') + sum([(len(stripANSIfromText(line)) // os.get_terminal_size()[0]) for line in self._topText.split('\n')]) + 1


    def printList(self):
        """Printing the items of the list that are currently in focus.
        
        As long as all printing outside a ConsoleListInterface is done through the separateInteraction function, 
        the interface will reprint the list automatically.
        """
        cls()
        moveCursor(0, 0)
        print(colored(self._topText, self._topTextColor))

        # console size has been changed
        if (self._consoleWidth != os.get_terminal_size()[0]) or (self._itemsPerColumn != os.get_terminal_size()[1] - 2):
            currPos = self._getPos()

            self._consoleWidth   = os.get_terminal_size()[0]
            self._itemsPerColumn = max(os.get_terminal_size()[1] - 2 - self._getLinesOfSetText() + 1, 1) # help page message, then startPrintLine
            self._separateInteractionPos = max(int(os.get_terminal_size()[1] / 2) - 4, 0)
            
            self._totalColumns     = roundup(len(self._items) / self._itemsPerColumn)
            self._lastColumnHeight = len(self._items) % self._itemsPerColumn

            if self._lastColumnHeight == 0:
                self._lastColumnHeight = self._itemsPerColumn
                            
            if not self._items:
                self._totalColumns     = 1
                self._lastColumnHeight = 1

            self._shownColumns = int(self._consoleWidth / (self._SPACESBEFORE + self._maxNameWidth))

            if self._shownColumns <= (self._column - self._leftmostColumn):
                self._leftmostColumn = self._column - self._shownColumns + 1

            self.updatePos(currPos)

        focusItems = self._items[(self._leftmostColumn - 1) * self._itemsPerColumn:]

        printColumn = 1
        printLine   = 1

        paramNo = len(signature(self._printFunc).parameters) # calling _printFunc with the appropriate number of parameters
        for item in focusItems:
            if self._shownColumns < printColumn:
                break
        
            moveCursor(printLine + self._getLinesOfSetText() - 1, (printColumn - 1) * (self._SPACESBEFORE + self._maxNameWidth))

            if paramNo == 1:
                print(f'    {self._printFunc(item)}')
            elif paramNo == 2:
                print(f'    {self._printFunc(item, self._maxNameWidth)}')
            elif paramNo == 3:
                print(f'    {self._printFunc(item, self._maxNameWidth, self._itemColor)}')
            
            printLine += 1
            if self._itemsPerColumn < printLine:
                printColumn += 1
                printLine    = 1
        
        moveCursor(self._itemsPerColumn + 2 + self._getLinesOfSetText() - 1, 0)

        if not self._disableHelp:
            print(colored(f"Type '{self._commandBind['?']}' for help page.", self._helpSearchColor), end='', flush=True)

    
    def interact(self, reprintList: bool = False) -> tuple[str, int]:
        """Interacting with the interface, until a special command is issued.

        Args:
            reprintList (bool): whether to reprint the list before the loop (if the console has been cleared by something other than this interface).

        Returns:
            tuple(str, int): the special command selected and the current position in list. 

        """

        cursor.hide()

        if reprintList:
            self.printList()

        while (True):
            moveCursor(self._line + self._getLinesOfSetText() - 1, (self._column - self._leftmostColumn) * (self._SPACESBEFORE + self._maxNameWidth))
            print(" -> ")
            # print(f'{self._column} {self._line}')           # debugging, current column and line
            # print(f'{self._leftmostColumn} {self._column}') # debugging, leftmost column and current column
            # print(self._getPos())                           # debugging, current position in list
            moveCursor(self._line + self._getLinesOfSetText() - 1, (self._column - self._leftmostColumn) * (self._SPACESBEFORE + self._maxNameWidth))

            try:
                command = lowercaseKey(readkey())
            
            # ignoring ctrl+c interrupt
            except KeyboardInterrupt:
                command = key.CTRL_C

            
            # special command was issued
            if command in self._specialCommands:
                return command, self._getPos()


            # searching by first character in item names
            if command not in self._actualCommands:
                first_letter = command.lower()
                current_position = self._getPos()
                new_position = next((i for i in range(len(self._items)) if self._items[i][0].lower() == first_letter and i > current_position), 
                                next((i for i in range(len(self._items)) if self._items[i][0].lower() == first_letter), current_position))


                if new_position != current_position:
                    print("   ")

                    self.updatePos(new_position)
                
                continue

            # searching by string in item names
            if command in [self._commandBind[key.CTRL_F], self._commandBind['\\']]:
                reprint = False
                if command == self._commandBind[key.CTRL_F]:
                    cls()
                    moveCursor(self._separateInteractionPos, 0)
                    cursor.show()
                    # using autocomplete for the ctrl+f search function
                    searchStr = autocomplete(self._items, colored("String to search by:\n", self._helpSearchColor), exitOnEsc=True)
                    self._searchStr = searchStr.lower() if searchStr else "" # since autocomplete can return None when esc is pressed
                    cursor.hide()
                    cls()
                    reprint = True

                if self._searchStr and not self._searchStr.isspace():
                    current_position = self._getPos()
                    new_position = next((i for i in range(len(self._items)) if self._searchStr in self._items[i].lower() and i > current_position), 
                                    next((i for i in range(len(self._items)) if self._searchStr in self._items[i].lower()), current_position))

                    if new_position != current_position:
                        print("   ")

                        self.updatePos(new_position)
                
                    
                if reprint:
                    self.printList()

                continue
            

            # arrowkeys for moving within list
            if command == self._commandBind[key.UP]:
                print("   ")

                self._line -= 1
                if self._line < 1:
                    self._line = self._itemsPerColumn if self._column < self._totalColumns else self._lastColumnHeight

                continue

            if command == self._commandBind[key.DOWN]:
                print("   ")

                self._line += 1
                if self._itemsPerColumn < self._line or (self._column == self._totalColumns and self._lastColumnHeight < self._line):
                    self._line = 1

                continue
                
            if command == self._commandBind[key.LEFT]:
                print("   ")

                self._column -= 1

                if self._column < self._leftmostColumn and 1 <= self._column:
                    self._leftmostColumn -= 1
                    self.printList()

                if self._column < 1:
                    self._column = self._totalColumns
                    if self._shownColumns < self._column:
                        self._leftmostColumn = self._totalColumns - self._shownColumns + 1
                        self.printList()
                    
                    # went to the last column from a position lower than its height
                    if self._lastColumnHeight < self._line:
                        self._line = self._lastColumnHeight
                
                continue
                
            if command == self._commandBind[key.RIGHT]:
                print("   ")

                self._column += 1

                if self._totalColumns < self._column:
                    self._column = 1
                    if 1 < self._leftmostColumn:
                        self._leftmostColumn = 1
                        self.printList()

                if self._shownColumns <= (self._column - self._leftmostColumn):
                    self._leftmostColumn += 1
                    self.printList()

                # went to the last column from a position lower than its height
                if self._column == self._totalColumns and self._lastColumnHeight < self._line:
                    self._line = self._lastColumnHeight
                
                continue

            
            # adding new list item
            if command == self._commandBind[key.CTRL_N]:
                self._items.append(self.separateInteraction(function=lambda: input("Type name of new element:\n"), showCursor=True))
                self.updateList(self._items)
                self.printList()

                # updating position to last element, which is where the new one will be
                self.updatePos(len(self._items) - 1)

                # returns command and the position of the new item
                return command, self._getPos()

            # renaming selected item
            if command == self._commandBind[key.CTRL_R]:
                if not self._items:
                    continue

                pos = self._getPos()
                newName = self.separateInteraction(function=lambda: input(f"Rename '{self._items[pos]}' to (or leave empty to cancel):\n"), showCursor=True)
                
                if newName and not newName.isspace():
                    self._items[pos] = newName
                    self.printList()

                    # returns command and the position of the renamed item
                    return command, pos

            # deleting selected item
            if command == self._commandBind[key.DELETE]:
                if not self._items:
                    continue

                pos = self._getPos()
                delete = self.separateInteraction(message=f"Type 'y' to remove '{self._items[pos]}'.", function=readkey)
                
                if delete == 'y':
                    self._items.pop(pos)
                    self.updateList(self._items)
                    self.printList() 

                    # returns command and the position of the deleted item in the non-updated list
                    # ONLY if it actually deletes
                    return command, pos

            # making item names longer
            if command == self._commandBind['='] and 1 < self._shownColumns:
                # changing the width of item names to maximum possible if we have one less column
                self._shownColumns -= 1
                self._maxNameWidth  = int(self._consoleWidth / self._shownColumns) - self._SPACESBEFORE

                if self._shownColumns <= (self._column - self._leftmostColumn):
                    self._leftmostColumn += 1

                self.printList()

                continue

            # making item names shorter
            if command == self._commandBind['-'] and self._MINNAMEWIDTH <= self._maxNameWidth:
                # changing the width of item names to leave space for an additional column
                self._shownColumns += 1
                self._maxNameWidth  = int(self._consoleWidth / self._shownColumns) - self._SPACESBEFORE

                self.printList()

                continue

            # printing help page
            if not self._disableHelp and command == self._commandBind['?']:
                cls()
                moveCursor(0, 0)
                print(self._helpPage + "\nPress enter to continue.", end='')
                waitForEnter()
                cls()
                self.printList()

                continue

            # refreshing list (for console size change)
            if command == self._commandBind[key.CTRL_U]:
                self.printList()

                continue

    def separateInteraction(self, message: Optional[str] = None, function: Optional[Callable[[Any], Any]] = None, functionArgs: Optional[Any] = None, 
                            startAtTop: bool = False, showCursor: bool = False, waitInsteadOfEnter: Optional[float] = None):
        """This method is for user interaction separate from the list interface.
        Once finished, it will reprint the list.
        
        Args:
            message (str): message to print.
            function (Any -> Any): function for interaction.
            functionArgs (Any): arguments for function.
            startAtTop (bool): instead of starting at _separateInteractionPos, the printing starts at the top of the console.
            showCursor (bool): show cursor during interaction.
            waitInsteadOfEnter (float): for interactions that are only a message, wait this many seconds before returning to the list interface.

        """
    
        cls() 

        if showCursor:
            cursor.show()
        
        if startAtTop:
            moveCursor(0, 0)
        else:
            moveCursor(self._separateInteractionPos, 0)

        if message:
            print(message)
            if not function:
                if not waitInsteadOfEnter:
                    print("Press enter to continue.\n")
                    waitForEnter()
                
                else:
                    sleep(waitInsteadOfEnter)

        functionReturn = None

        if function:
            if functionArgs:
                functionReturn = function(functionArgs)

            else:
                functionReturn = function()

        self.printList()

        cursor.hide()

        return functionReturn


    def getItems(self):
        """Returns the current list of items.
        Especially useful if ctrl+n, ctrl+r and delete are kept as internal commands.

        """

        return self._items


    def updateList(self, newItems: list[str]):
        """Update interface list.

        Args:
            newItems (list[str]): the new list of selectable items.

        """

        self._items = [item.replace('\n', '') for item in newItems] # accidental '\n' fucks up printing

        self._totalColumns     = roundup(len(self._items) / self._itemsPerColumn)
        self._lastColumnHeight = len(self._items) % self._itemsPerColumn

        if self._lastColumnHeight == 0:
            self._lastColumnHeight = self._itemsPerColumn
                        
        if not self._items:
            self._totalColumns     = 1
            self._lastColumnHeight = 1

        # in case the previous position is now outside the list 
        if self._itemsPerColumn < self._line:
            self._line = self._itemsPerColumn
        else:
            if (self._column == self._totalColumns and self._lastColumnHeight < self._line):
                self._line = self._lastColumnHeight

        self.printList()

    def updatePos(self, newPos: int):
        """Manually change position in list, and reprints it if needed.

        Args:
            newPos (int): the new position of the arrow (will be forced to 0...len(self._items), so update list first).

        """

        moveCursor(self._line + self._getLinesOfSetText() - 1, (self._column - self._leftmostColumn) * (self._SPACESBEFORE + self._maxNameWidth))
        print("    ")

        if newPos < 0:
            newPos = 0

        if len(self._items) <= newPos:
            newPos = len(self._items) - 1 if self._items else 0 

        self._column = int(newPos / self._itemsPerColumn) + 1
        self._line   = newPos % self._itemsPerColumn + 1

        savedLeftMost = self._leftmostColumn
        
        self._leftmostColumn = max(self._column - self._shownColumns + 1, 1)

        if savedLeftMost != self._leftmostColumn:
            self.printList()
        
        moveCursor(self._line + self._getLinesOfSetText() - 1, (self._column - self._leftmostColumn) * (self._SPACESBEFORE + self._maxNameWidth))
        print(" -> ")


    def setTopText(self, text = str, dontPrintList: bool = False):
        """Set text to be displayed above the list.

        Args:
            text (str): text to be displayed.
            dontPrintList (bool): will stop this function from reprinting list,
                                  to avoid some unnecessary reprints.
         
        """
        if not text:
            text = ""
        
        text += '\n'

        prevLines = self._getLinesOfSetText()
        pos = self._getPos()

        self._topText = text
        self._itemsPerColumn = max(os.get_terminal_size()[1] - 2 - self._getLinesOfSetText() + 1, 1) # help page message, then startPrintLine

        # if the new top text has the same number of lines as the old text, the list will be printed starting at the same line (so no need to reprint)
        if prevLines == self._getLinesOfSetText():
            # cleaning previous text
            moveCursor(0, 0)
            for _ in range(self._topText.count('\n')):
                print(' ' * os.get_terminal_size()[0])

            moveCursor(0, 0)
            print(colored(text, self._topTextColor))
            return

        # if the number of top text lines has changed, the relative _line and _column positions might have changed as well
        # therefore, _line and _column values are updated based on the absolute position in the list
        self.updatePos(pos)
        
        if not dontPrintList:
            self.printList()

    def setTitle(self, title = str):
        """Set title for the terminal console.
        
        Args:
            title (str): title for the terminal console.

        """
        setTitle(title)

    def configure(self, specialCommands: list[str] = None, rebindCommands: dict[str, str] = None, shownColumns: int = None, printFunc: Callable[[str, int], int] = None,  
                  helpPage: str = None, topTextColor: Union[str, tuple[int, int, int]] = None, itemColor: Union[str, tuple[int, int, int]] = None, 
                  helpSearchColor: Union[str, tuple[int, int, int]] = None, dontPrintList: bool = False, supressColorWarning: bool = False):
        """Change one or more of the configurable functionalities.

        Args:
            specialCommands (list[str]): new list of special commands, which will overwrite the original special commands list.

            rebindCommands: dict[str, str]: dictionary for rebinding internal commands (commands not in rebindCommands remain untouched).

            shownColumns (int): change the number of columns to be shown at a time in the console programmatically.
                                Important note: by default, the user can increase and decrease the number of columns with the '+' and '-' keys respectively.
                                '+' and '-' can be ignored as commands by adding them to the special commands.

            printFunc ((str, int) -> str): the new function for printing the item names (str is the name and int is the cut-off for the name length).
                                           Reset the printing function by configuring it to the 'ConsoleListInterface.defaultPrintFunc' function. 

            helpPage (str): new user instructions for all application commands.

            topTextColor (str | (int, int, int)): the color for the text displayed above the list (the default is the standard console light gray).
                                                  If string, must be compatible with termcolor.colored.
                                                  If int tuple, it will be the RGB values.
            
            itemColor (str | (int, int, int)): the color for the list items (the default is the standard console light gray).
                                               If string, must be compatible with termcolor.colored.
                                               If int tuple, it will be the RGB values.

            helpSearchColor (str | (int, int, int)): the color for the help-page and search messages (the default is the standard console light gray).
                                                     If string, must be compatible with termcolor.colored.
                                                     If int tuple, it will be the RGB values.

            dontPrintList (bool): set True to stop the list from being printed when the visible interface is changed.

            supressColorWarning (bool): set this to True if the 'grey' color option prints visibly in the terminal, 
                                        in order to supress the warning for it.

        """
        if not supressColorWarning and "grey" in [topTextColor, itemColor, helpSearchColor]:
            cls()
            moveCursor(0, 0)
            print("ConsoleListInterface.configure warning: termcolor 'grey' may not be visible in the terminal.")
            print("Consider changing it to 'light_grey' - the standard color of text in terminal.")
            print("Otherwise, use 'supressColorWarning=True' to supress this warning.\n")
            print("Press enter to continue.\n")
            waitForEnter()

        if specialCommands: 
            self._specialCommands = specialCommands

        if rebindCommands:
            self._commandBind     = {command: (self._commandBind[command] if command not in rebindCommands else lowercaseKey(rebindCommands[command])) for command in self._commandBind}
            self._actualCommands  = self._commandBind.values() # all the values that internal commands are bound to

        if shownColumns:
            self._shownColumns = shownColumns
        
        if printFunc:
            self._printFunc = printFunc

        if helpPage:
            self._helpPage = helpPage

        if topTextColor:
            self._topTextColor = topTextColor

        if itemColor:
            self._itemColor = itemColor

        if helpSearchColor:
            self._helpSearchColor = helpSearchColor

        # if any of these properties have been reconfigured, the visible interface will have changed
        if shownColumns or printFunc or topTextColor or itemColor or helpSearchColor and not dontPrintList:
            self.printList()

    def disableHelpPage(self, disableHelp: Optional[bool] = None):
        """Change whether the "Type '?' for help page." message is shown and the help page is printed.

        Args:
            disableHelp (bool): if None, help disabling will be toggled to the opposite value (True -> False, False -> True).
                                Otherwise it will be changed to the bool value of disableHelp.
        
        """
        if disableHelp:
            self._disableHelp = disableHelp
        else:
            self._disableHelp = not self._disableHelp

        self.printList() # reprint list to hide/unhide the "Type '?' for help page." message 


    def exitInterface(self):
        """Clears screen, shows cursor, moving it to the beginning of the console."""
        cls()
        cursor.show()
        moveCursor(0, 0)

