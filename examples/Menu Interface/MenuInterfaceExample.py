from ConsoleListInterface import MenuInterface

# importing json if pyyaml is not installed
try:
    import yaml
    yaml_imported = True
except:
    import json
    yaml_imported = False


DIFFICULTIES = ["Hard", "Normal", "Easy"]

EXTRAS = ["Big Head Mode", "Invincibility", "Score x10"]


def main():
    selected_difficulty = "Normal"
    selected_extras = []
    volume_level = 50
    
    if yaml_imported:
        menu = MenuInterface(yaml.load(open("example_menu.yaml"), Loader=yaml.FullLoader))
    else:
        menu = MenuInterface(json.load(open("example_menu.json")))

    while True:
        path = menu.interactWithMenu()

        # backspace ignored on main menu
        if not path:
            continue

        if 'Start' in path:
            # note that this outputs options as '{OptionName}: null'
            # perhaps it's better to use json 
            if yaml_imported:
                with open("example_menu_output.yaml", 'w') as file:
                    yaml.safe_dump(menu.getMenuStructure(), file, indent=4, sort_keys=False)
                    filename = "example_menu_output.yaml"
            else:
                with open("example_menu_output.json", 'w') as file:
                    json.dump(menu.getMenuStructure(), file, indent=4, sort_keys=False)
                    filename = "example_menu_output.json"

            # removing null from output
            file_text = "".join(open(filename, 'r').readlines()).replace('null', '')
            with open(filename, 'w') as file:
                file.write(file_text)

            menu.separateInteraction(message="Starting game...\n")

        if path[-1].startswith("Play"):
            # note that this outputs options as '{OptionName}: null'
            # perhaps it's better to use json 
            if yaml_imported:
                with open("example_menu_output.yaml", 'w') as file:
                    yaml.safe_dump(menu.getMenuStructure(), file, indent=4, sort_keys=False)
                    filename = "example_menu_output.yaml"
            else:
                with open("example_menu_output.json", 'w') as file:
                    json.dump(menu.getMenuStructure(), file, indent=4, sort_keys=False)
                    filename = "example_menu_output.json"

            # removing null from output
            file_text = "".join(open(filename, 'r').readlines()).replace('null', '')
            with open(filename, 'w') as file:
                file.write(file_text)

            chapter_name = path[-1][len("Play "):]
            menu.separateInteraction(message=f"Playing {chapter_name}...\n")
        

        # changing selected difficulty
        if 2 <= len(path) and path[-2] == "Difficulty":
            # ignoring selection when it is the same difficulty
            if path[-1].startswith(selected_difficulty):
                continue
            
            changes = MenuInterface.selectOption(selected_difficulty, path[-1], DIFFICULTIES)
            selected_difficulty = path[-1]
            menu.changeOptionNames(path[:-1], changes)

            continue
        
        if 2 <= len(path) and path[-2].startswith("Sound"):
            volume_key = f"Sound ({volume_level}%)"

            if path[-1] == "Raise Volume":
                volume_level += 10
                if 100 < volume_level:
                    volume_level = 100

            if path[-1] == "Lower Volume":
                volume_level -= 10
                if volume_level < 0:
                    volume_level = 0

            volume_value = f"Sound ({volume_level}%)"

            menu.changeOptionNames(path[:-2], {volume_key: volume_value})


        # for single-option and multiple-option choices, the path returned will contain the selection character/text (in this case, 'x')
        # therefore, to check if the path returned is one of the options, the startswith function needs to be used  
        if len(path) == 3 and path[-2] == "Extras" and any((path[-1].startswith(extra) for extra in EXTRAS)):
            selected_extra = next((extra for extra in EXTRAS if path[-1].startswith(extra)))

            changes = MenuInterface.selectMultipleOptions(selected_extras, selected_extra, EXTRAS, 'x')

            # adding extra
            if selected_extra not in selected_extras:
                selected_extras.append(selected_extra)
            # removing extra
            else:
                selected_extras.remove(selected_extra)

            menu.changeOptionNames(path[:-1], changes)

            continue


        if 'Quit' in path:
            # note that this outputs options as '{OptionName}: null'
            # perhaps it's better to use json 
            if yaml_imported:
                with open("example_menu_output.yaml", 'w') as file:
                    yaml.safe_dump(menu.getMenuStructure(), file, indent=4, sort_keys=False)
                    yaml_text = "".join(open("example_menu_output.yaml", 'r').readlines()).replace('null', '')
                    with open("example_menu_output.yaml", 'w') as file:
                        file.write(yaml_text)

            else:
                with open("example_menu_output.json", 'w') as file:
                    json.dump(menu.getMenuStructure(), file, indent=4, sort_keys=False)
                
            menu.exitInterface()
            return


if __name__ == "__main__":
    main()