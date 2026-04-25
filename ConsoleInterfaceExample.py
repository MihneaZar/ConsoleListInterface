from ConsoleListInterface import ConsoleListInterface
from readchar import key


def main():
    console = ConsoleListInterface(open("example.txt").readlines())
    while True:
        command, curr_pos = console.interact()

        if command == key.ENTER:
            console.separateInteraction()


if __name__ == "__main__":
    main()