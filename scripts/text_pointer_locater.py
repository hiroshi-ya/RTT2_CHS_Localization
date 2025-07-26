# This script locates the address of the text pointer
# Author: HiroshiYa

# import os
import numpy as np

workText = "../sources/work_texts/work_EBOOT.BIN.TXT"

binPath = "../eboots/EBOOT.BIN"

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

try:
    binFile = open(binPath, "rb")
    BIN = np.fromfile(binFile, dtype=np.uint32)
    binFile.close()
except FileNotFoundError:
    print(f"\n** Error: file \"{binPath}\" doesn't exist **\n")

print()

for line in text:
    if line.strip():
        lineAddr = int(line.split(',')[0], 16)
        print(f"Checking: {lineAddr}\r", end='')
        offsetAddr = lineAddr + 0x088FFFAC # addr in RAM
        # offsetAddrLE = num_to_little_endian(offsetAddr)
        binAddr = np.where(BIN == offsetAddr)[0]
        if len(binAddr) == 0:
            print("\nCan't locate: " + line[:-1])
            print(f"lineAddr = {hex(lineAddr)}\noffsetAddr = {hex(offsetAddr)}\n")
            break

if len(binAddr) != 0:
    print("\n** Done **\n")