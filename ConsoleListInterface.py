from readchar import readkey, readchar, key
from typing import Callable, Any, Optional
from math import ceil as roundup
import cursor
import sys
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

def moveCursor(y: int, x: int):
    """Function for moving the cursor to a different position in the console.

    Args:
        y (int): column in console (characters).
        x (int): line in console (characters).

    """

    sys.stdout.write("\033[%d;%dH" % (max(y, 0), max(x, 0)))

# clear screen function
cls = lambda: os.system('cls' if os.name=='nt' else 'clear')

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


class ConsoleListInterface:
    """Class for interacting with the console list, an interface for selecting and searching in a list printed to the console.
    
    The default commands are explained in the DEFAULTHELP help page.
    Special commands (enter, escape) can be changed through the specialCommands parameter. 

    While in most cases it would make more sense for the list items to be sorted, it does not have to be.
    The list can have repeat values, next to each other or otherwise.
    Any newlines in item names are ignored because that causes undefined behaviour.

    Important note: All commands are changed to and treated in lowercase, to avoid confusion.
    """

    # the ( -> /    ) before list items
    _SPACESBEFORE = 4  

    _INTERNALCOMMANDS = [key.UP, key.DOWN, key.LEFT, key.RIGHT, key.CTRL_F, '\\', key.CTRL_N, key.CTRL_R, key.DELETE, key.CTRL_U, '=', '-', '?']


    def __init__(self, items: list[str] = [], specialCommands: list[str] = [key.ENTER, key.ESC], helpPage: str = DEFAULTHELP, startPos: int = 0, 
                 printFunc: Optional[Callable[[str, int], int]] = None, rebindCommand: dict[str, str] = {}, disableHelp: bool = False):
        """Intializes console interface.

        Args:
            items (list[str]): complete list of selectable items.
            specialCommands (list[str]): the commands that will be outputted from the 'interact' method; if empty, method will be stuck in an infite loop.
                                         Additionally, internal commands passed in this list will be ignored by the interface and returned by the 'interact' method.
            helpPage (str): user instructions for all application commands.
            startPos (int): current position in list, by default the first element.
            printFunc ((str, int) -> str): custom function for printing the item names (str is the name and int is the max accepted length).
            rebindCommand (str: str): dictionary for rebinding internal commands to other keys (e.g. rebindCommand[key.CTRL_F] = key.CTRL_S will bind searching by string to ctrl+s instead of ctrl+f). 
                                      Binding multiple commands to the same key will lead to only one of them being detected.
            disableHelp: disable the "Type '?' for help page." message and help page printing.

        Returns:
            ConsoleListInterface object.

        """
        if items == None:
            items = []

        self._consoleWidth   = os.get_terminal_size()[0] 
        self._itemsPerColumn = os.get_terminal_size()[1] - 2
        self._infoPos        = max(int(self._itemsPerColumn / 2 - 4), 0)
        
        self._maxColumns   = 3
        self._maxNameWidth = int(self._consoleWidth / self._maxColumns) - self._SPACESBEFORE

        self._column = int((startPos) / self._itemsPerColumn) + 1
        self._line   = (startPos) % self._itemsPerColumn + 1
        
        self._leftmostColumn = max(self._column - self._maxColumns + 1, 1)

        self._items           = [item.replace('\n', '') for item in items] # accidental '\n' fucks up printing
        self._specialCommands = [lowercaseKey(command) for command in specialCommands]
        self._helpPage        = helpPage
        self._printFunc       = printFunc
        self._commandBind     = {command: (command if command not in rebindCommand else lowercaseKey(rebindCommand[command])) for command in self._INTERNALCOMMANDS}
        self._actualCommands  = self._commandBind.values() # all the values that internal commands are bound to
        self._disableHelp     = disableHelp

        self._totalColumns      = roundup(len(self._items) / self._itemsPerColumn)
        self._lastColumnHeight  = len(self._items) % self._itemsPerColumn

        if self._lastColumnHeight == 0:
            self._lastColumnHeight = self._itemsPerColumn
                        
        if not self._items:
            self._totalColumns     = 1
            self._lastColumnHeight = 1

        self._searchStr = None # saved search string for repeated searches

        cursor.hide()

        self.printList()


    def printList(self):
        """Printing the items of the list currently in focus.
        
        As long as all printing to console is done only through the same ConsoleListInterface, the methods reprint the list automatically every time it is necessary. 
        Therefore, this method should only be used if printing is done from a different source, including another ConsoleListInterface object.
        """

        # console size has been changed
        if (self._consoleWidth != os.get_terminal_size()[0]) or (self._itemsPerColumn != os.get_terminal_size()[1] - 2):
            currPos = (self._column - 1) * self._itemsPerColumn + self._line - 1

            self._consoleWidth   = os.get_terminal_size()[0]
            self._itemsPerColumn = os.get_terminal_size()[1] - 2
            self._infoPos        = max(int(self._itemsPerColumn / 2 - 4), 0)
            
            self._totalColumns     = roundup(len(self._items) / self._itemsPerColumn)
            self._lastColumnHeight = len(self._items) % self._itemsPerColumn

            if self._lastColumnHeight == 0:
                self._lastColumnHeight = self._itemsPerColumn
                            
            if not self._items:
                self._totalColumns     = 1
                self._lastColumnHeight = 1

            self._maxColumns = int(self._consoleWidth / (self._SPACESBEFORE + self._maxNameWidth))

            if self._maxColumns <= (self._column - self._leftmostColumn):
                self._leftmostColumn = self._column - self._maxColumns + 1

            self.updatePos(currPos)

        focusItems = self._items[(self._leftmostColumn - 1) * self._itemsPerColumn:]

        cls()
        printColumn = 1
        printLine   = 1

        for item in focusItems:
            if self._maxColumns < printColumn:
                break
        
            moveCursor(printLine, (printColumn - 1) * (self._SPACESBEFORE + self._maxNameWidth))

            if self._printFunc:
                print(f'    {self._printFunc(item, self._maxNameWidth)}')
            
            else:
                itemName = item[0:self._maxNameWidth - 1]
                if self._maxNameWidth <= len(item):
                    itemName += '-'
                print(f'    {itemName}')
            
            printLine += 1
            if self._itemsPerColumn < printLine:
                printLine    = 1
                printColumn += 1
        
        moveCursor(self._itemsPerColumn + 2, 0)

        if not self._disableHelp:
            print(f"Type '{self._commandBind['?']}' for help page.", end='', flush=True)

    
    def interact(self, reprintList: bool = False) -> tuple[str, int]:
        """Interacting with the interface, until a special command is issued.

        Args:
            reprintList (bool): whether to reprint the list before the loop (if the list isn't already printed).

        Returns:
            tuple(str, int): the special command selected and the current position in list. 

        """

        cursor.hide()

        if reprintList:
            self.printList()

        while (True):
            moveCursor(self._line, (self._column - self._leftmostColumn) * (self._SPACESBEFORE + self._maxNameWidth))
            print(" -> ")
            # print(f'{self._column} {self._line}')                             # debugging, current column and line
            # print(f'{self._leftmostColumn} {self._column}')                   # debugging, leftmost column and current column
            # print((self._column - 1) * self._itemsPerColumn + self._line - 1) # debugging, current position in list
            moveCursor(self._line, (self._column - self._leftmostColumn) * (self._SPACESBEFORE + self._maxNameWidth))

            try:
                command = lowercaseKey(readkey())
            
            # ignoring ctrl+c interrupt
            except KeyboardInterrupt:
                command = key.CTRL_C

            
            # special command was issued
            if command in self._specialCommands:
                return command, (self._column - 1) * self._itemsPerColumn + self._line - 1


            # searching by first character in item names
            if command not in self._actualCommands:
                first_letter = command.lower()
                current_position = (self._column - 1) * self._itemsPerColumn + self._line - 1
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
                    moveCursor(self._infoPos, 0)
                    cursor.show()
                    self._searchStr = input("String to search by:\n").lower()
                    cursor.hide()
                    cls()
                    reprint = True

                if self._searchStr and not self._searchStr.isspace():
                    current_position = (self._column - 1) * self._itemsPerColumn + self._line - 1
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
                    if self._maxColumns < self._column:
                        self._leftmostColumn = self._totalColumns - self._maxColumns + 1
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

                if self._maxColumns <= (self._column - self._leftmostColumn):
                    self._leftmostColumn += 1
                    self.printList()

                # went to the last column from a position lower than its height
                if self._column == self._totalColumns and self._lastColumnHeight < self._line:
                    self._line = self._lastColumnHeight
                
                continue

            
            # adding new list item
            if command == self._commandBind[key.CTRL_N]:
                self._items += self.separateInteraction(function=lambda: input("Type name of new element:\n"), showCursor=True)
                self.printList()

                # updating position to last element, which is where the new one will be
                self.updatePos(len(self._items) - 1)

                # returns command and the position of the new item
                return command, (self._column - 1) * self._itemsPerColumn + self._line - 1

            # renaming selected item
            if command == self._commandBind[key.CTRL_R]:
                if not self._items:
                    continue

                pos = (self._column - 1) * self._itemsPerColumn + self._line - 1
                newName = self.separateInteraction(function=lambda: input(f"Rename '{self._items[pos]}' to (or leave empty to cancel):\n"), showCursor=True)
                
                if newName and not newName.isspace():
                    self._items[pos] = newName
                    self.printList()

                    # returns command and the position of the renamed item
                    return command, (self._column - 1) * self._itemsPerColumn + self._line - 1

            # deleting selected item
            if command == self._commandBind[key.DELETE]:
                if not self._items:
                    continue

                pos = (self._column - 1) * self._itemsPerColumn + self._line - 1
                delete = self.separateInteraction(message=f"Type 'y' to remove '{self._items[pos]}'.", function=readkey)
                
                if delete == 'y':
                    self._items.pop(pos)
                    self.UpdatePos(pos - 1)
                    self.printList() 

                # returns command and the position of the deleted item in the non-updated list
                return command, (self._column - 1) * self._itemsPerColumn + self._line - 1

            # making item names longer
            if command == self._commandBind['='] and 1 < self._maxColumns:
                # changing the width of item names to maximum possible if we have one less column
                self._maxColumns  -= 1
                self._maxNameWidth = int(self._consoleWidth / self._maxColumns) - self._SPACESBEFORE

                if self._maxColumns <= (self._column - self._leftmostColumn):
                    self._leftmostColumn += 1

                self.printList()

                continue

            # making item names shorter
            if command == self._commandBind['-'] and 8 <= self._maxNameWidth:
                # changing the width of item names to leave space for an additional column
                self._maxColumns  += 1
                self._maxNameWidth = int(self._consoleWidth / self._maxColumns) - self._SPACESBEFORE

                self.printList()

                continue

            # printing help page
            if not self._disableHelp and command == self._commandBind['?']:
                cls()
                moveCursor(0, 0)
                print(self._helpPage + "\nPress enter to continue.")
                waitForEnter()
                cls()
                self.printList()

                continue

            # refreshing list (for console size change)
            if command == self._commandBind[key.CTRL_U]:
                self.printList()

                continue

    def separateInteraction(self, message: Optional[str] = None, function: Optional[Callable[[Any], Any]] = None, functionArgs: Optional[Any] = None, startAtTop: bool = False, showCursor: bool = False):
        """This method is for user interaction separate from the list interface.
        Once finished, it will reprint the list.
        
        Args:
            message (str): message to print.
            function (Any -> Any): function for interaction.
            functionArgs (Any): arguments for function.
            startAtTop (bool): instead of starting at infoPos, the printing starts at the top of the console.
            showCursor (bool): show cursor during interaction.

        """

        cls()

        if showCursor:
            cursor.show()
        
        if startAtTop:
            moveCursor(0, 0)
        else:
            moveCursor(self._infoPos, 0)

        if message:
            print(message)
            if not function:
                cursor.hide()
                print("Press enter to continue.\n")
                waitForEnter()

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

        moveCursor(self._line, (self._column - self._leftmostColumn) * (self._SPACESBEFORE + self._maxNameWidth))
        print("    ")

        if newPos < 0:
            newPos = 0

        if len(self._items) <= newPos:
            newPos = len(self._items) - 1 if self._items else 0 

        self._column = int(newPos / self._itemsPerColumn) + 1
        self._line   = newPos % self._itemsPerColumn + 1

        savedLeftMost = self._leftmostColumn
        
        self._leftmostColumn = max(self._column - self._maxColumns + 1, 1)

        if savedLeftMost != self._leftmostColumn:
            self.printList()
        
        moveCursor(self._line, (self._column - self._leftmostColumn) * (self._SPACESBEFORE + self._maxNameWidth))
        print(" -> ")
        
    def updatePrint(self, newPrintFunc: Optional[Callable[[str, int], int]] = None):
        """Change printing function for items.

        Args:
            newPrintFunc ((str, int) -> str): the new function for printing the item names (str is the name and int is the max accepted length).

        """
        self._printFunc = newPrintFunc
    
    def updateSpecialCommands(self, newSpecialCommands: list[str]):
        """Change the special command list (overwritting the original one).

        Args:
            newSpecialCommands (list[str]): new list of special commands, with the same function as the one in the class initializer.
        
        """

        self._specialCommands = [lowercaseKey(command) for command in newSpecialCommands]

    def updateRebinds(self, rebindCommand: dict[str, str]):
        """Update the rebinds of internal commands.
        Commands not in rebindCommand remain untouched.

        Args:
            rebindCommand: dict[str, str]: dictionary for rebinding internal commands, same as the one in the class initializer.
        
        """

        self._commandBind     = {command: (self._commandBind[command] if command not in rebindCommand else lowercaseKey(rebindCommand[command])) for command in self._commandBind}
        self._actualCommands  = self._commandBind.values() # all the values that internal commands are bound to

    def updateHelpPage(self, newHelpPage: str):
        """Update the help page of the application. 

        Args:
            newHelpPage (str): new user instructions for all application commands.
        
        """

        self._helpPage = newHelpPage

    def toggleHelpPage(self, disableHelp: Optional[bool] = None):
        """Change whether the "Type '?' for help page." message is shown and the help page is printed.

        Args:
            disableHelp (bool): if None, help disabling will be toggled to the opposite value (True -> False, False -> True).
                                Otherwise it will be changed to the bool value of disableHelp.
        
        """

        if disableHelp:
            self._disableHelp = disableHelp
        else:
            self._disableHelp = not self._disableHelp

    def exitInterface(self):
        """Clears screen, shows cursor, moving it to the beginning of the console."""
        cls()
        cursor.show()
        moveCursor(0, 0)

