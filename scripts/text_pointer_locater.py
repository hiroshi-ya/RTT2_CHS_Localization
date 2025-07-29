# This script locates the address of the text pointer
# Author: HiroshiYa

# import os
import numpy as np

workText = "../sources/work_texts/work_EBOOT.BIN.TXT"
binPath = "../eboots/EBOOT.BIN"
binOrigPath = "../eboots/eboot_backup/EBOOT.BIN"

def num_to_little_endian(num:int):
# turns a number to its 32-bit little endian equivalent
# eg. num    = 0x12345678
#     result = 0x78563412
    result = 0
    for _ in range(4):
        result = result << 8
        lowestByte = num % (2**8)
        num = num >> 8
        result += lowestByte
    return result

try:
    feboot = open(workText, "r", encoding="utf-16-le")
    text = feboot.readlines()
    text[0] = text[0].replace('\ufeff','')
    feboot.close()
except FileNotFoundError:
    print(f"\n** Error: file \"{workText}\" doesn't exist **\n")
    quit()

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

for line in text:
    if line.strip():
        lineAddr = int(line.split(',')[0], 16)
        print(f"Checking: {lineAddr}\r", end='')
        offsetAddr = lineAddr + 0x088FFFAC # addr in RAM
        # offsetAddrLE = num_to_little_endian(offsetAddr)
        binAddrList = np.where(BIN == offsetAddr)[0]
        if len(binAddrList) == 0:
            print("\nCan't locate: " + line[:-1])
            print(f"lineAddr = {hex(lineAddr)}\noffsetAddr = {hex(offsetAddr)}\n")
            break
        else:
            binAddr = binAddrList[0]
            binOrigVal = BINorig[binAddr]
            if binOrigVal != offsetAddr:
                inconsistent.add((binAddr*4, binOrigVal, offsetAddr))

# for pair in inconsistent:
#     print(f"Address {hex(pair[0])} is inconsistent: orig = {hex(pair[1])}, work = {hex(pair[2])}")

print("********************")

addrModPath = "./eboot_addr_mod.txt"
# addrModPath = "tttest.txt"
textFileWelcomeMessage = """# Addresses with its value in the original EBOOT
# and the modified EBOOT.
# 
# Format: 
# Address -> Value in original EBOOT -> Value in modified EBOOT\n
"""

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
            addrModFile.write(f"\n0x{hex(pair[0]).upper()[2:]} -> 0x{hex(pair[1]).upper()[2:]} -> 0x{hex(pair[2]).upper()[2:]}")
            print(f"Wrote Address {hex(pair[0])} with Orig = {hex(pair[1])}, Work = {hex(pair[2])}")
        else:
            if pair[1:] != existingPair[pair[0]]:
                print(f"** Warning: address {hex(pair[0])} faces conflict and was ignored **")


if len(binAddrList) != 0:
    print("\n** Done **\n")