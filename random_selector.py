from console_list_interface import ConsoleInterface
from time import sleep, time
from random import random

def get_names():
    print("Input names:")
    name_list = []
    
    name = input()
    while name and not name.isspace():
        name_list.append(name)
        name = input()

    return name_list

console = ConsoleInterface(disableHelp=True)

name_list = console.separateInteraction(function=get_names, startAtTop=True, showCursor=True)

console.updateList(name_list)

if name_list:
    pos = 0
    start = time()
    while (time() - start) < random() + 2:
        pos += 1
        if len(name_list) == pos:
            pos = 0

        console.updatePos(pos)
        sleep(0.1)

    console.separateInteraction(message=f'{name_list[pos]} is a loser!')
    
console.exitInterface()
