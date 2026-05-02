## Description
A class for interacting with a list of items in the console/terminal.

## Requirements
- The [python-readchar](https://pypi.org/project/readchar/) library for reading keystrokes;
- The [cursor](https://pypi.org/project/cursor/) library for hiding the cursor in console.

## Additional Functions
- moveCursor(y: int, x: int) -> places the console cursor at given position (implementation might not work in all console environments);
- lowercaseKey(key: str)     -> transforms key to lowercase for case-insensitive searches, without changing multi-character keys (like the arrow keys);
- waitForEnter()             -> function for waiting specifically for enter to be pressed (also using readchar);
- cls()                      -> clears the screen (should work both on Windows and Linux).

## Example Usage
- [This example](examples/ConsoleListInterfaceExample.py) is the simplest version of using the ConsoleListInterface class;
- [This example](examples/RandomSelector.py) is how the class can be used for a simple visual random selector. 

## Extra Info
Class functions are explained in the comments. <br>
Only tested on Windows 11.

-------------------------------------------------------------------------

*Copyright (c) 2026 Mihnea Bogdan Zarojanu*
