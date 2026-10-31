from ConsoleListInterface import autocomplete

print('Output: ' + autocomplete([line.rstrip() for line in open("../example.txt").readlines()], "Input: "))