from ConsoleListInterface._ConsoleListInterface import ConsoleListInterface
from typing import Union, Optional
from termcolor import colored
from readchar import key
import string


class MenuInterface(ConsoleListInterface):
    """Class for interacting with a menu.

    This is a much more restrictive and specific version of the ConsoleListInterface class.
    It only allows movement between the various submenus.
    
    """

    _HELPPAGE = """
    Controls:
        - arrow keys -> moving between options in the current menu.
        - enter      -> if the selected item is a submenu, enter said submenu.
                     -> if the selected item is an option, choose said option.
        - ctrl+u     -> update printed menu (if the menu or the console size was changed).
        - '?'        -> display current help page.
    """

    # overwritting searching by first letter and adding enter for choosing submenu/option and backspace for returning to previous menu
    _SPECIALCOMMANDS = list(string.ascii_lowercase) + [key.ENTER, key.BACKSPACE]
    
    # only internal commands used by this class extension
    _KEEPCOMMANDS = [key.UP, key.DOWN, key.LEFT, key.RIGHT, key.CTRL_U, '?']

    def _menuPrintFunc(optionName: str, maxNameWidth: int, currentMenu: dict[str: Optional[dict]], ignoreMaxWidth: bool = True):
        """Special printing function for differentiating between submenus and options.

        Args:
            optionName (str): the name of the option.
            maxNameWidth (int): the total number of characters that the printed name can have (otherwise it will get cut-off).
            currentMenu (str: dict): the structure of the current submenu (since it's a dictionary, Python passes it by reference - sort-of: https://stackoverflow.com/a/15078615/31936209)
            ignoreMaxWidth (bool): since the menus aren't likely to have more options than the height of the terminal, the cut-off is ignored by default.   

        Returns:
            The truncated name.

        """
        isMenu = (currentMenu[optionName] is not None)
        if len(optionName) <= maxNameWidth or ignoreMaxWidth:
            optionName = optionName
        else:
            optionName = optionName[:maxNameWidth - 1] + '-'
        optionName = colored(optionName, 'blue') if isMenu else optionName

        return optionName


    def __init__(self, menuStructure: dict[str, dict]):
        """Intializes console interface.

        Args:
            menuStructure: the structure of the menu and its submenus, in the form of a dictionary.
                           The first level key represents the Main Menu title.
                           A submenu is represented by a (str: dict) value.
                           An option for a menu is represented by a (str: None) value.

        Returns: 
            A MenuInterface object.

        """

        self._menuStructure = menuStructure
        self._currentPath   = []
        self._currentMenu   = next(iter(menuStructure.values())) # obtaining Main Menu
        
        # rebinds to nothing for all the unused ConsoleListInterface internal commands
        rebindUnused = {command: "" for command in MenuInterface._INTERNALCOMMANDS if command not in MenuInterface._KEEPCOMMANDS}

        super(MenuInterface, self).__init__(items=list(self._currentMenu.keys()), specialCommands=self._SPECIALCOMMANDS, helpPage=self._HELPPAGE, 
                                            printFunc=lambda optionName, maxNameWidth: MenuInterface._menuPrintFunc(optionName, maxNameWidth, self._currentMenu), rebindCommand=rebindUnused)

        self.setTopText(next(iter(menuStructure.keys())) + '\n') # Main Menu name
    

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
                    self.exitInterface()
                    return self._currentPath + [optionName]

                self._currentMenu = self._currentMenu[optionName]
                self._currentPath.append(optionName) 
                self.updateList(list(self._currentMenu.keys()))
                self.updatePos(0)
                self.setTopText(optionName + '\n')

            if command == key.BACKSPACE:
                if not self._currentPath:
                    self.exitInterface()
                    return self._currentPath

                submenuName = self._currentPath.pop()
                self._currentMenu = next(iter(self._menuStructure.values()))
                menuName = next(iter(self._menuStructure.keys()))
                for submenu in self._currentPath:
                    menuName = submenu
                    self._currentMenu = self._currentMenu[submenu]

                self.updateList(list(self._currentMenu.keys()))
                self.updatePos(self._items.index(submenuName))
                self.setTopText(menuName + '\n')
                
    
