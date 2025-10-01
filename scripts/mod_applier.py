# This script reads the text file that stores the mod info and applies the mod
# Author: HiroshiYa

# import os
import numpy as np

def welcome_seq():
    strings = [
        "This script reads the text file that stores the mod",
        "info and applies the mod or revert the mod.",
        "Enter 1 to apply the mod for stats.",
        "Enter 2 to apply the mod for texts.",
        "Enter 3 to apply the mod for both.",
        "Enter 4 to revert the mod for stats.",
        "Enter 5 to revert the mod for texts.",
        "Enter 6 to revert the mod for both.",
        "To Exit, enter anything or press [Ctrl + C]."
    ]
    maxLen = 0
    for s in strings:
        currLen = len(s)
        if currLen > maxLen:
            maxLen = currLen
    space = maxLen + 5
    print(f"\n{'':*<{space}}")
    for s in strings:
        print(f"* {s:<{space-4}} *")
    print(f"{'':*<{space}}\n")
    return

def exit_seq():
    print("\n** See You **\n")
    quit()

binPath = "../eboots/EBOOT.BIN"
binOrigPath = "../eboots/eboot_backup/EBOOT.BIN"
binModPath = "../eboots/eboot_mod/EBOOT.BIN"
statMod = "./eboot_stat_mod.txt"
addrMod = "./eboot_addr_mod.txt"

welcome_seq()

try:
    choice = input("Please enter: ")
    revert = False
    textFilePaths = [statMod, addrMod]
    match choice:
        case '1': 
            textFilePaths.pop(1)
        case '2': 
            textFilePaths.pop(0)
        case '3': 
            pass
        case '4':
            revert = True
            textFilePaths.pop(1)
        case '5':
            revert = True
            textFilePaths.pop(0)
        case '6': 
            revert = True
        case _:
            exit_seq()

    # open EBOOT
    try:
        binFile = open(binPath, "rb")
        BIN = np.fromfile(binFile, dtype=np.uint32)
        binFile.close()
    except FileNotFoundError:
        print(f"\n** Error: file \"{binPath}\" doesn't exist **\n")
        quit()

    # iterate through text files
    for textFilePath in textFilePaths:
        try:
            textFile = open(textFilePath, "r")
            valueIndex = 1 if revert else 2
            for line in textFile:
                if line[0] != '0': # ignore invalid lines
                    continue
                lineSplit = line.split("->")
                if len(lineSplit) != 3:
                    print(f"\n** Error: file \"{textFile}\" is not valid **\n")
                    quit()
                addrInText = int(lineSplit[0], 16) >> 2 # those addr. are byte representing, convert to uint32 representing
                modValue = int(lineSplit[valueIndex], 16)
                BIN[addrInText] = modValue # change value accordingly
                print(f"Wrote value {hex(modValue):<10} in address {hex(addrInText<<2)}")
            textFile.close()
        except FileNotFoundError:
            print(f"\n** Error: file \"{textFile}\" doesn't exist **\n")
            quit()

    # write to ./eboot/eboot_mod/
    with open(binModPath, "wb") as writeFile:
        BIN.tofile(writeFile)
        print("** Wrote " + binModPath)
        exit_seq()

except KeyboardInterrupt:
    exit_seq()
