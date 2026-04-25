from console_list_interface import ConsoleInterface, cls, moveCursor
from time import sleep

# console = ConsoleInterface(sorted(open("test.txt").readlines()))
# for i in range(1, 30):
#     console.updatePos(i)
#     sleep(0.05)


# example with list items taken from "test.txt"
console = ConsoleInterface(sorted(open("test.txt").readlines()))
output = console.interact()
cls()
moveCursor(0, 0)
print(ord(output[0]))
print(sorted(open("test.txt").readlines())[output[1]].replace('\n', ''))

# example with rebinds
# console = ConsoleInterface(sorted(open("test.txt").readlines()))
# console.updateRebinds({key.CTRL_F: key.CTRL_S, key.UP: 'w', key.LEFT: 'a', key.RIGHT: 'd', key.DOWN: 's', '?': key.CTRL_H, key.CTRL_U: key.CTRL_R})
# console.updateSpecialCommands([key.ESC, key.ENTER, 'p'])
# output = console.interact()
# cls()
# moveCursor(0, 0)
# print(ord(output[0]))
# print(sorted(open("test.txt").readlines())[output[1]].replace('\n', ''))