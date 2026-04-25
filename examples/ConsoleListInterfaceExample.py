import sys
sys.path.append('C:\\Users\\Mihnea\\Desktop\\Random thoughts\\Cool stuff\\ConsoleListInterface')

from ConsoleListInterface import ConsoleListInterface # pyright: ignore[reportMissingImports]
from readchar import key
import sys

sys.stderr = open(f'C:/Users/Mihnea/Desktop/Random thoughts/Cool stuff/ConsoleListInterface/example/errors.txt', "a")

def main():
    console = ConsoleListInterface([line.replace('\n', '') for line in open("example.txt").readlines()])
    while True:
        command, curr_pos = console.interact()

        if command == key.ENTER:
            console.separateInteraction(message=f"You have chosen {console.getItems()[curr_pos]}!\n")
        
        if command == key.ESC:
            console.exitInterface()
            quit()  # quit is useful for simplifying exiting the program when in subfunctions and not in main


if __name__ == "__main__":
    main()