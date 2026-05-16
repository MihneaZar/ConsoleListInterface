from ConsoleListInterface._ConsoleListInterface import ConsoleListInterface
from ConsoleListInterface._cli_utils import moveCursor, waitForEnter, cls
from typing import Union, Optional
from termcolor import colored
from readchar import key
import string


_HELPPAGEMAIN = """Controls:
    - arrow keys -> moving between options in the current menu.
    - enter      -> if the selected item is a submenu, enter said submenu.
                 -> if the selected item is an option, choose said option.
    - ctrl+u     -> update printed menu (if the menu or the console size was changed).
    - '?'        -> display current help page.
    - escape     -> exit menu (also backspace).
"""

# help page for submenu when escOnAnyMenu is False
_HELPPAGESUB = """Controls:
    - arrow keys -> moving between options in the current menu.
    - enter      -> if the selected item is a submenu, enter said submenu.
                 -> if the selected item is an option, choose said option.
    - backspace  -> return to previous menu.
    - ctrl+u     -> update printed menu (if the menu or the console size was changed).
    - '?'        -> display current help page.
"""

# help page for submenu when escOnAnyMenu is True
_HELPPAGESUBESC = """Controls:
    - arrow keys -> moving between options in the current menu.
    - enter      -> if the selected item is a submenu, enter said submenu.
                 -> if the selected item is an option, choose said option.
    - backspace  -> return to previous menu.
    - ctrl+u     -> update printed menu (if the menu or the console size was changed).
    - '?'        -> display current help page.
    - escape     -> exit menu.
"""

class MenuInterface(ConsoleListInterface):
    """Class for interacting with a menu.

    This is a much more restrictive and specific version of the ConsoleListInterface class.
    It only allows movement between the various submenus.
    
    """

    # overwritting searching by first letter and adding esc, enter for choosing submenu/option and backspace for returning to previous menu
    _SPECIALCOMMANDS = list(string.ascii_lowercase) + list(string.digits) + list(string.punctuation) + [key.ESC, key.ENTER, key.BACKSPACE]
    
    # only internal commands used by this class extension
    _KEEPCOMMANDS = [key.UP, key.DOWN, key.LEFT, key.RIGHT, key.CTRL_U, '?']

    # setting collumn number to 1
    _STARTCOLUMNNO = 1


    def __init__(self, menuStructure: dict[str, dict], submenuColor: Union[str, tuple[int, int, int]] = 'blue', optionColor: Union[str, tuple[int, int, int]] = 'light_blue', 
                 supressColorWarning: bool = False, dontPrintMenu: bool = False, escOnAnyMenu: bool = False):
        """Intializes console interface.

        Args:
            menuStructure (str: dict): the structure of the menu and its submenus, in the form of a dictionary.
                                       The first level key represents the Main Menu title.
                                       A submenu is represented by a (str: dict) value.
                                       An option for a menu is represented by a (str: None or str: "") option.

            submenuColor (str | (int, int, int)): the color for printing submenu names (default blue).
                                                  If string, must be compatible with termcolor.colored.
                                                  If int tuple, it will be the RGB values.
            optionColor (str | (int, int, int)): the color for printing option names (default light blue). 
                                                  If string, must be compatible with termcolor.colored.
                                                  If int tuple, it will be the RGB values.

            supressColorWarning (bool): set this to True if the 'grey' color option prints visibly in the terminal, 
                                        in order to ignore the warning for it.

            dontPrintMenu (bool): set to True to stop the Main Menu from being printed on __init__.

            escOnAnyMenu (bool): set to True to accept key.ESC on any submenu, not just the main menu.  

        Returns: 
            A MenuInterface object.

        """
        if not supressColorWarning and "grey" in [submenuColor, optionColor]:
            cls()
            moveCursor(0, 0)
            print("MenuInterface.__init__ warning: termcolor 'grey' may not be visible in the terminal.\nConsider changing it to 'light_grey' - the standard color of text in terminal.\n\nPress enter to continue.\n")
            waitForEnter()

        self._menuStructure = menuStructure
        self._currentPath   = []
        self._currentMenu   = next(iter(menuStructure.values())) # obtaining Main Menu
        self._submenuColor  = submenuColor
        self._escOnAnyMenu  = escOnAnyMenu
        
        # rebinds to nothing for all the unused ConsoleListInterface internal commands
        rebindUnused = {command: "" for command in MenuInterface._INTERNALCOMMANDS if command not in MenuInterface._KEEPCOMMANDS}
        
        super(MenuInterface, self).__init__(items=list(self._currentMenu.keys()), specialCommands=self._SPECIALCOMMANDS, helpPage=_HELPPAGEMAIN, rebindCommand=rebindUnused, dontPrintList=True, # the list will be reprinted anyway in setTopText
                                            printFunc=lambda optionName, maxNameWidth: MenuInterface._menuPrintFunc(optionName, maxNameWidth, self._currentMenu, submenuColor, optionColor))

        self.setTopText(colored(next(iter(menuStructure.keys())), self._submenuColor) + '\n', dontPrintList=dontPrintMenu) # Main Menu name
    

    def _menuPrintFunc(optionName: str, maxNameWidth: int, currentMenu: dict[str: Optional[dict]], submenuColor: Union[str, tuple[int, int, int]], optionColor: Union[str, tuple[int, int, int]], ignoreMaxWidth: bool = True):
        """Special printing function for differentiating between submenus and options.

        Args:
            optionName (str): the name of the option.
            maxNameWidth (int): the total number of characters that the printed name can have (otherwise it will get cut-off).
            currentMenu (str: dict): the structure of the current menu (since it's a dictionary, Python passes it by reference - sort-of: https://stackoverflow.com/a/15078615/31936209).
            submenuColor (str | (int, int, int)): the color for printing submenu names.
            optionColor (str | (int, int, int)): the color for printing option names. 
            ignoreMaxWidth (bool): since the menus aren't likely to have more options than the height of the terminal, the cut-off is ignored by default.   

        Returns:
            The truncated name.

        """
        isMenu = (currentMenu[optionName] != "" and currentMenu[optionName] is not None)
        if len(optionName) <= maxNameWidth or ignoreMaxWidth:
            optionName = optionName
        else:
            optionName = optionName[:maxNameWidth - 1] + '-'
        optionName = colored(optionName, submenuColor) if isMenu else colored(optionName, optionColor)

        return optionName


    def interactWithMenu(self):
        """Interacting with the menu interface, until an option is chosen.

        Returns:
            list[str]: the path to the chosen option. 

        """
        while True:
            command, position = self.interact()

            if command == key.ESC:
                # checking if it is on main menu, or if escOnAnyMenu is set to True
                if self._currentPath == [] or self._escOnAnyMenu:
                    return [key.ESC]

            if command == key.ENTER:
                optionName = self._items[position]

                # no submenu means option was selected
                if not self._currentMenu[optionName]:
                    return self._currentPath + [optionName]

                # changing from main menu help page to submenu help page
                if self._currentPath == []:
                    self.configure(helpPage=_HELPPAGESUB if not self._escOnAnyMenu else _HELPPAGESUBESC)

                self._currentMenu = self._currentMenu[optionName]
                self._currentPath.append(optionName) 
                self.updateList(list(self._currentMenu.keys()))
                self.updatePos(0)
                self.setTopText(colored(optionName, self._submenuColor) + '\n')

                return self._currentPath # returning current path, for title changes

            if command == key.BACKSPACE:
                if self._currentPath == []:
                    return [key.BACKSPACE]

                submenuName = self._currentPath.pop()
                self._currentMenu = next(iter(self._menuStructure.values()))
                menuName = next(iter(self._menuStructure.keys()))
                for submenu in self._currentPath:
                    menuName = submenu
                    self._currentMenu = self._currentMenu[submenu]

                self.updateList(list(self._currentMenu.keys()))
                self.updatePos(self._items.index(submenuName))
                self.setTopText(colored(menuName, self._submenuColor) + '\n')

                # changing to main menu help page when returning to it
                if self._currentPath == []:
                    self.configure(helpPage=_HELPPAGEMAIN)

                return self._currentPath # returning current path, for title changes
                

    def changeMainMenuTitle(self, newMainMenu: str):
        """Change the title of the Main Menu.

        Args:
            newMainMenu (str): the new title for the main menu.
        
        """
        self._menuStructure[newMainMenu] = self._menuStructure.pop(next(iter(self._menuStructure.keys())))

        if self._currentPath == []:
            self.setTopText(colored(newMainMenu, self._submenuColor) + '\n')

    def changeOptionNames(self, path: list[str], changes: dict[str, str]):
        """Change the name of options for a menu.

        Args:
            path (list[str]): path to the menu to change.
            changes (str: str): dictionary with the old names of the options as the keys, and the new names as values.
                                Only needed for the options whose name changes.

        """
        menu = next(iter(self._menuStructure.values()))
        for submenu in path:
            menu = menu[submenu]

        # all options need to be re-put into the submenu, to keep the order
        changes = {option: changes[option] if option in changes else option for option in menu}
        for option in list(menu):
            menu[changes[option]] = menu.pop(option)

        # changing option names in the current submenu
        if path == self._currentPath:
            self.updateList(list(self._currentMenu.keys()))
            return

        # changing name of submenu in the current path
        if path and self._currentPath[:len(path)] == path:
            self._currentPath[len(path)] = changes[self._currentPath[len(path)]]

            # changing name of current submenu
            if len(self._currentPath) == len(path) + 1:
                self.setTopText(colored(self._currentPath[-1], self._submenuColor) + '\n')
            return

                
    def addOptions(self, path: list[str], options: dict[str, dict], insertBefore: str = None):
        """Add options to a submenu.

        Args:
            path (list[str]): path to the menu to change.
            options (str: dict): dictionary with the new submenus and options.
            insertBefore (str): if this option exists in the menu set to change, the new options will be inserted before it.
                                Otherwise, the new options are inserted at the bottom of the menu.

        """
        menu = next(iter(self._menuStructure.values()))
        for submenu in path:
            menu = menu[submenu]

        for option in options:
            menu[option] = options[option]

        if insertBefore in menu: 
            keys = [key for key in menu.keys() if key not in options]

            for keyPos in range(keys.index(insertBefore), len(keys)):
                menu[keys[keyPos]] = menu.pop(keys[keyPos]) 
            
        # if adding options in the current submenu
        if path == self._currentPath:
            self.updateList(list(self._currentMenu.keys()))

    def removeOptions(self, path: list[str], options: list[str]):
        """Remove options from a submenu.

        Important note: removing a previous submenu in the current path that is not the current submenu will create undefined behaviour,
        most likely crashing the program.

        Args:
            path (list[str]): path to the menu to change.
            options (list[str]): list of options to remove.

        """
        menu = next(iter(self._menuStructure.values()))
        for submenu in path:
            menu = menu[submenu]

        for option in options:
            # guardrail in case a non-existent option is added
            if option in menu:
                menu.pop(option)
            
        # if adding options in the current submenu
        if path == self._currentPath:
            self.updateList(list(self._currentMenu.keys()))

    
    def selectOption(selectedOption: str, newSelectedOption: str, options: list[str], padding: bool = True, selectText: str = "(selected)"):
        """Creates the changes dictionary for when a single selectable option is chosen.

        Args:
            selectedOption (str): the currently selected option (can be None).
            newSelectedOption (str): the newly selected option (also can be None).
            options (list[str]): the complete list of options.
            padding (bool): whether to pad the name of the selected option, so that the selectText is always at the same width.
                           Important: if padding is left True, the original menu structure must also contain that padding.
            selectedText (str): the text to be displayed to show an option is selected, by default '(selected)'.

        Returns:
            (str: str): the changes dictionary. 

        """
        maxOptionLength = max([len(option) for option in options])
        changes = {}
        for option in options:
            key = option
            if option == selectedOption:
                if padding:
                    key += " " * (maxOptionLength - len(option) + 1)
                key += selectText
                
            value = option
            if option == newSelectedOption:
                if padding: 
                    value += " " * (maxOptionLength - len(option) + 1)
                value += selectText

            changes[key] = value

        return changes
    
    def selectMultipleOptions(selectedOptions: list[str], newSelectedOption: str, options: list[str], selectText: str = "(selected)", padding: bool = True):    
        """Creates the changes dictionary for multiple selectable options.

        Args:
            selectedOptions (list[str]): the currently selected options.
            newSelectedOption (str): the newly selected option (can be None).
            options (list[str]): the complete list of options.
            padding (bool): whether to pad the name of the selected option, so that the selectText is always at the same width.
                           Important: if padding is left True, the original menu structure must also contain that padding.
            selectedText (str): the text to be displayed to show an option is selected, by default '(selected)'.

        Returns:
            (str: str): the changes dictionary. 

        """
        maxOptionLength = max([len(option) for option in options])
        changes = {}
        
        for option in options:
            key = option
            if option in selectedOptions:
                if padding:
                    key += " " * (maxOptionLength - len(option) + 1)
                key += selectText
                
            value = option
            if option == newSelectedOption:
                # selecting new option
                if option not in selectedOptions:
                    if padding: 
                        value += " " * (maxOptionLength - len(option) + 1)
                    value += selectText
                
                # by default, if the newSelectedOption has already been selected, the key will have selectText
                # and it's unselected by simply having its value be itself without the selectText

            else:
                # adding selectText for unchanged selected options
                if option in selectedOptions:
                    if padding: 
                        value += " " * (maxOptionLength - len(option) + 1)
                    value += selectText

            changes[key] = value

        return changes
    

    def getMenuStructure(self):
        """Get the menu structure of the interface.
        This is a dictionary, so it is passed by reference.
        Therefore, changes to the structure not implemented in this class can be made directly to the menu structure dictionary.
        
        Important note: changes made this way could cause undefined behaviour.
        
        Returns:
            (str: dict): the dictionary structure of the menu, with some potentially changed keys (options).
        
        """
        return self._menuStructure
    

    def helpMenu(helpPages: dict[str: str | list[str]], titleColor: Union[str, tuple[int, int, int]] = 'blue', 
                 helpOptionColor: Union[str, tuple[int, int, int]] = 'light_blue', supressColorWarning: bool = False, title: str = "Help page"):
        """Runs a help menu page, which splits all the command explanations into categories.
        Example uses of this function can be found at https://github.com/MihneaZar/dir-explorer and https://github.com/MihneaZar/link-master.
            
        Args:
            helpPages (str: str | list[str]): a dictionary where the keys represent the separate help pages / categories, and the values represent the info text to be printed.
                                              If the value is given as a list of strings, will print each string on a separate line. If string, it will simply print the string.
                                              The function will automatically append ':' to category title when in the help page of the category, if it doesn't already have punctuation.
            
            submenuColor (str | (int, int, int)): the color for printing the help menu title, equivalent to submenuColor from the init of the class.
                                                  If string, must be compatible with termcolor.colored.
                                                  If int tuple, it will be the RGB values.
            submenuColor (str | (int, int, int)): the color for printing the help menu categories, equivalent to optionColor from the init of the class.
                                                  If string, must be compatible with termcolor.colored.
                                                  If int tuple, it will be the RGB values.

            supressColorWarning (bool): set this to True if the 'grey' color option prints visibly in the terminal, 
                                        in order to ignore the warning for it.                  

            title (str): the title of the help page, by default simply "Help page".
            
        """
        # concatenating list of strings into a single string with '\n' between elements
        printHelpPages = {page: "\n".join(helpPages[page]) if isinstance(helpPages[page], list) else helpPages[page] for page in helpPages}

        # adding category title to help page
        for page in printHelpPages:
            categoryTitle = page
            if categoryTitle[-1] not in "?:.!":
                categoryTitle += ':'

            categoryTitle = colored(categoryTitle, helpOptionColor)
            printHelpPages[page] = categoryTitle + "\n\n" + printHelpPages[page]

        menuStructure = {title: {helpPage: None for helpPage in helpPages}}
        menuStructure[title]["Exit"] = None

        menu = MenuInterface(menuStructure, titleColor, helpOptionColor, supressColorWarning)

        while True:
            path = menu.interactWithMenu()

            # ignoring backspace to main menu
            if not path:
                continue

            path = path[0]

            if path in printHelpPages:
                menu.separateInteraction(message=printHelpPages[path] + '\n', startAtTop=True)

            if path in ["Exit", key.ESC, key.BACKSPACE]:
                return