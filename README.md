## Description
A library for interacting with a list of items in the console/terminal.

## Requirements (installed on setup)
- The [python-readchar](https://pypi.org/project/readchar/) library for reading keystrokes;
- The [cursor](https://pypi.org/project/cursor/) library for hiding the cursor in console;
- The [termcolor](https://pypi.org/project/termcolor/) library for printing colored names;
- (Optional) The [PyYAML](https://pypi.org/project/PyYAML/) library for loading menu structures - this library is not installed on setup, and the Python [JSON](https://docs.python.org/3/library/json.html) standard library can be used instead for loading menus models.

## Setup 
Simply run 'pip3 install .' in the root directory, and pip will install this library as an importable Python package. <br>
The package name is 'ConsoleListInterface'. <br>
Import with 'from ConsoleListInterface import [ConsoleListInterface | moveCursor | lowercaseKey | waitForEnter | cls]'. <br>
Uninstall with 'pip3 uninstall ConsoleListInterface.

## Menu Interface
As a much more specific use-case and extension of the ConsoleListInterface, the MenuInterface class implements a simple interface for a menu tree. <br>
As is shown in this [example](examples/Menu%20Interface), the menu can be easily structured in the [YAML](https://yaml.org/) or [JSON](https://www.json.org/json-en.html) formats. <br>
The 'Main Menu' (its name can be changed through the first key) and its subsequent submenus can have a combination of options and submenus - a submenu is a list item which leads to another menu, and an option is a the end of an option path (a leaf in the menu tree). <br>
The example includes possible implementations for single-select options, multi-select options, and controlling the level of an option. <br>
Note: to simplify the implementation, the options are string-key dictionary entries with a None or an empty string value (instead of simply being a string, since mixing strings with dicts that way would get quite stuffy and confusing).  

## Additional Functions
- moveCursor(y: int, x: int) -> places the console cursor at given position (implementation might not work in all console environments);
- lowercaseKey(key: str)     -> transforms key to lowercase for case-insensitive searches, without changing multi-character keys (like the arrow keys);
- waitForEnter()             -> function for waiting specifically for enter to be pressed (also using readchar);
- cls()                      -> clears the screen (should work both on Windows and Linux).

## Example Usages
- [This example](examples/Simple%20Console%20Interface) is the simplest version of using the ConsoleListInterface class;
- [This example](examples/Random%20Selector) is how the class can be used for a simple visual random selector; 
- [This example](examples/Menu%20Interface) is how the MenuInterface class can be used for a simple menu implementation

## Extra Info
Class functions are explained in the comments. <br>
Only tested on Windows 11.

-------------------------------------------------------------------------

*Copyright (c) 2026 Mihnea Bogdan Zarojanu*
