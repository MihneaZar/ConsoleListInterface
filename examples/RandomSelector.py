from ConsoleListInterface.Interface import ConsoleListInterface
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

def main():
    console = ConsoleListInterface(disableHelp=True)

    # name_list = console.separateInteraction(function=get_names, startAtTop=True, showCursor=True)
    name_list = [line.replace('\n', '') for line in open("example.txt").readlines()]

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

        console.separateInteraction(message=f'{name_list[pos]} is a loser!\n')
        
    console.exitInterface()


if __name__ == "__main__":
    main()