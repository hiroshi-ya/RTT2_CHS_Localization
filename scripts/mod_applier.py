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

# # check the following intervals in format (smaller address, larger address)
# # Note: These are the addresses in psp RAM (i.e. has an offset of 0x08800000)
# addrInterval = np.array(
#     [
#         (0x8B24F9C, 0x8B295B8),
#         (0x8B2BE6C, 0x8B3B97C),
#         (0x8B739B4, 0x8B7B664)
#     ], dtype=np.uint32
# )

addrInterval -= 0x88FFFAC # RAM to EBOOT conversion
addrInterval >>= 2 # Each element is a uint32 (4 bytes) instead of byte

try:
    binFile = open(binPath, "rb")
    BIN = np.fromfile(binFile, dtype=np.uint32)
    binFile.close()
except FileNotFoundError:
    print(f"\n** Error: file \"{binPath}\" doesn't exist **\n")
    quit()

try:
    binOrigFile = open(binOrigPath, "rb")
    BINorig = np.fromfile(binOrigFile, dtype=np.uint32)
    binOrigFile.close()
except FileNotFoundError:
    print(f"\n** Error: file \"{binOrigPath}\" doesn't exist **\n")
    quit()

inconsistent = set() # address, original_value, work_value

print()

# for line in text:
for (small, large) in addrInterval:
    for i in range(small, large):
        binOrigVal = BINorig[i]
        binModVal = BIN[i]
        if binOrigVal != binModVal:
            inconsistent.add((i<<2, binOrigVal, binModVal)) # the index needs to be converted back to byte representing


print("********************")

addrModPath = "./eboot_stat_mod.txt"
# addrModPath = "tttest.txt"
textFileWelcomeMessage = """# This file is for stat tracking,
# not for pointer checking.
#
# Addresses with its value in the original EBOOT
# and the modified EBOOT.
# 
# Format: 
# Address -> Value in original EBOOT -> Value in modified EBOOT
"""

# read existing pairs in the txt file and don't re-write these value
existingPair = {}
try:
    with open(addrModPath, "r", encoding="utf-8") as addrModFile:
        exist = True
        for line in addrModFile:
            sline = line.strip().replace(' ','')
            if len(sline) != 0 and sline[0] != '#':
                pair = sline.split("->")
                if len(pair) == 3:
                    existingPair[int(pair[0], 16)] = (int(pair[1], 16), int(pair[2], 16))
except FileNotFoundError:
    exist = False


with open(addrModPath, "a", encoding="utf-8") as addrModFile:
    if not exist:
        addrModFile.write(textFileWelcomeMessage)
    for pair in inconsistent:
        if pair[0] not in existingPair:
            addrModFile.write(f"\n0x{hex(pair[0]).upper()[2:]} -> 0x{hex(pair[1]).upper()[2:]:<8} -> 0x{hex(pair[2]).upper()[2:]}")
            print(f"Wrote Address {hex(pair[0])} with Orig = {hex(pair[1]):<10}, Work = {hex(pair[2])}")
        else:
            if pair[1:] != existingPair[pair[0]]:
                print(f"** Warning: address {hex(pair[0])} faces conflict and was ignored **")

print("\n** Done **\n")