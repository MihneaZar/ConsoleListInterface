from ConsoleListInterface._ConsoleListInterface import ConsoleListInterface
from typing import Union, Optional
from termcolor import colored
from readchar import key
import string



_HELPPAGE = """Controls:
    - arrow keys -> moving between options in the current menu.
    - enter      -> if the selected item is a submenu, enter said submenu.
                 -> if the selected item is an option, choose said option.
    - ctrl+u     -> update printed menu (if the menu or the console size was changed).
    - '?'        -> display current help page.
"""

class MenuInterface(ConsoleListInterface):
    """Class for interacting with a menu.

    This is a much more restrictive and specific version of the ConsoleListInterface class.
    It only allows movement between the various submenus.
    
    """

    # overwritting searching by first letter and adding enter for choosing submenu/option and backspace for returning to previous menu
    _SPECIALCOMMANDS = list(string.ascii_lowercase) + [key.ENTER, key.BACKSPACE]
    
    # only internal commands used by this class extension
    _KEEPCOMMANDS = [key.UP, key.DOWN, key.LEFT, key.RIGHT, key.CTRL_U, '?']

    # setting collumn number to 1
    _STARTCOLUMNNO = 1


    def __init__(self, menuStructure: dict[str, dict], submenuColor: Union[str, tuple[int, int, int]] = 'blue', optionColor: Union[str, tuple[int, int, int]] = 'light_blue'):
        """Intializes console interface.

        Args:
            menuStructure (str: dict): the structure of the menu and its submenus, in the form of a dictionary.
                                       The first level key represents the Main Menu title.
                                       A submenu is represented by a (str: dict) value.
                                       An option for a menu is represented by a (str: None) value.

            submenuColor (str | (int, int, int)): the color for printing submenu names (default blue).
                                                  If string, must be compatible with termcolor.colored.
                                                  If int tuple, it will be the RGB values.
            optionColor (str | (int, int, int)): the color for printing option names (default light blue). 
                                                  If string, must be compatible with termcolor.colored.
                                                  If int tuple, it will be the RGB values.

        Returns: 
            A MenuInterface object.

        """

        self._menuStructure = menuStructure
        self._currentPath   = []
        self._currentMenu   = next(iter(menuStructure.values())) # obtaining Main Menu
        self._submenuColor  = submenuColor
        
        # rebinds to nothing for all the unused ConsoleListInterface internal commands
        rebindUnused = {command: "" for command in MenuInterface._INTERNALCOMMANDS if command not in MenuInterface._KEEPCOMMANDS}
        
        super(MenuInterface, self).__init__(items=list(self._currentMenu.keys()), specialCommands=self._SPECIALCOMMANDS, helpPage=_HELPPAGE, 
                                            printFunc=lambda optionName, maxNameWidth: MenuInterface._menuPrintFunc(optionName, maxNameWidth, self._currentMenu, submenuColor, optionColor), rebindCommand=rebindUnused)

        self.setTopText(colored(next(iter(menuStructure.keys())), self._submenuColor) + '\n') # Main Menu name
    

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
        isMenu = (currentMenu[optionName] is not None)
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

            if command == key.ENTER:
                optionName = self._items[position]

                # no submenu means option was selected
                if not self._currentMenu[optionName]:
                    return self._currentPath + [optionName]

                self._currentMenu = self._currentMenu[optionName]
                self._currentPath.append(optionName) 
                self.updateList(list(self._currentMenu.keys()))
                self.updatePos(0)
                self.setTopText(colored(optionName, self._submenuColor) + '\n')

            if command == key.BACKSPACE:
                if self._currentPath == []:
                    return self._currentPath

                submenuName = self._currentPath.pop()
                self._currentMenu = next(iter(self._menuStructure.values()))
                menuName = next(iter(self._menuStructure.keys()))
                for submenu in self._currentPath:
                    menuName = submenu
                    self._currentMenu = self._currentMenu[submenu]

                self.updateList(list(self._currentMenu.keys()))
                self.updatePos(self._items.index(submenuName))
                self.setTopText(colored(menuName, self._submenuColor) + '\n')
                
    
    def changeOptions(self, path: list[str], changes: dict[str, str]):
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

        # changing name of submenu
        if path == self._currentPath[:-1]:
            self._currentPath[-1] = changes[self._currentPath[-1]]
            self.setTopText(colored(self._currentPath[-1], self._submenuColor) + '\n')

    def changeMainMenu(self, newMainMenu: str):
        """Change the title of the Main Menu.

        Args:
            newMainMenu (str): the new title for the main menu.
        
        """
        self._menuStructure[newMainMenu] = self._menuStructure.pop(next(iter(self._menuStructure.keys())))

    
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
        """Get the menu structure of the interface, if selectable options have been changed.
        
        Returns:
            (str: dict): the dictionary structure of the menu, with some potentially changed keys (options).
        
        """
        return self._menuStructure