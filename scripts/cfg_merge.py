# This script merges all the .CFG file into one big CFG.BIN
# The CFG.BIN will be saved in the [../CMN/CMN/CFG/MOD/] folder
# Author: HiroshiYa

import numpy as np
import os

cfgPath = "../CMN/CMN/CFG/"
chap = "CHAP000"; online = "ONLINE0"; suffix = ".CFG"
fileNames = [
    chap+'0'+suffix,
    chap+'1'+suffix,
    chap+'2'+suffix,
    chap+'3'+suffix,
    online+"000"+suffix,
    online+"100"+suffix,
    online+"200"+suffix
]
mergeName = "CFG.BIN"

fileArr = np.array([], dtype=np.uint8)
print()
for subFileName in fileNames:
    try:
        subFile = open(cfgPath + subFileName, "rb")
        subFileArr = np.fromfile(subFile, dtype=np.uint8)
        fileArr = np.concatenate((fileArr, subFileArr))
        print(f"{subFileName} size: {np.size(subFileArr)}")
        subFile.close()
    except FileNotFoundError:
        print(f"\n** Error: file \'{subFileName}\" doesn't exist **\n")

print("\n** Concatenation Complete **")

file = open(cfgPath + "MOD/" + mergeName, "wb")
fileArr.tofile(file)
file.close()

print("** Writing Complete **\n")