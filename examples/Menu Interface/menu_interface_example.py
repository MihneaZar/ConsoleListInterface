from ConsoleListInterface import MenuInterface
import yaml


def main():
    menu = MenuInterface(yaml.load(open("example_menu.yaml"), Loader=yaml.FullLoader))
    while True:
        path = menu.interactWithMenu()

        if 'Quit' in path:
            menu.exitInterface()
            return
        
        if path:
            menu.separateInteraction(message=f"You have selected {path.pop()}.\n")


if __name__ == "__main__":
    main()