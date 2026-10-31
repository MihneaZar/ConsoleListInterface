from ConsoleListInterface import autocomplete

print('Input: ', end='', flush=True) # flush=True is required when the end argument is empty
print('\nOutput: ' + autocomplete([line.rstrip() for line in open("../example.txt").readlines()]))