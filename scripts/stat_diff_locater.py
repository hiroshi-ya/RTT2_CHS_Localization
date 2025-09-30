# This script locates the address of the modified stats
# Author: HiroshiYa

# import os
import numpy as np

binPath = "../eboots/EBOOT.BIN"
binOrigPath = "../eboots/eboot_backup/EBOOT.BIN"

# check the following intervals in format (smaller address, larger address)
# Note: These are the addresses in psp RAM (i.e. has an offset of 0x08800000)
addrInterval = np.array(
    [
        (0x8B24F9C, 0x8B295B8),
        (0x8B2BE6C, 0x8B3B97C),
        (0x8B739B4, 0x8B7B664)
    ], dtype=np.uint32
)

addrInterval -= 0x88FFFAC # RAM to EBOOT conversion
addrInterval >>= 2 # Each element is a uint32 (4 bytes) instead of byte

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


    # if line.strip():
    #     lineAddr = int(line.split(',')[0], 16)
    #     print(f"Checking: {lineAddr}\r", end='')
    #     offsetAddr = lineAddr + 0x088FFFAC # addr in RAM
    #     # offsetAddrLE = num_to_little_endian(offsetAddr)
    #     binAddrList = np.where(BIN == offsetAddr)[0]
    #     if len(binAddrList) == 0:
    #         print("\nCan't locate: " + line[:-1])
    #         print(f"lineAddr = {hex(lineAddr)}\noffsetAddr = {hex(offsetAddr)}\n")
    #         break
    #     else:
    #         binAddr = binAddrList[0]
    #         binOrigVal = BINorig[binAddr]
    #         if binOrigVal != offsetAddr:
    #             inconsistent.add((binAddr*4, binOrigVal, offsetAddr))

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


# if len(binAddrList) != 0:
#     print("\n** Done **\n")
print("\n** Done **\n")