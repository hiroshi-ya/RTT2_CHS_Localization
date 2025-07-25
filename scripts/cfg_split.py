# This script splits the CFG.BIN back to individual .CFG files
# Author: HiroshiYa

import numpy as np
import os

cfgModPath = "../CMN/CMN/CFG/MOD/"
chap = "CHAP000"; online = "ONLINE0"; suffix = ".CFG"
cfgFiles = {
    chap+'0'+suffix : 168704,
    chap+'1'+suffix : 165008,
    chap+'2'+suffix : 165488,
    chap+'3'+suffix : 143904,
    online+"000"+suffix : 167472,
    online+"100"+suffix : 143056,
    online+"200"+suffix : 68736
}

fileName = "CFG.BIN"
# print(os.path.dirname(fileName))
# os.makedirs(os.path.dirname(fileName), exist_ok=True) # so that open() doesn't complain
try:
    file = open(cfgModPath + fileName, "rb")
    fileArr = np.fromfile(file, dtype=np.uint8)
    file.close()
    print("\n** File Read **")

    for subFileName, subFileSize in cfgFiles.items():
        subFileArr = fileArr[:subFileSize]
        # subFileName = fileName
        subFile = open(cfgModPath + subFileName, "wb")
        subFileArr.tofile(subFile)
        subFile.close()
        print(f"** Wrote {subFileName} **")
        fileArr = fileArr[subFileSize:]

    print("** Writing Complete **\n")

except:
    print(f"\n** Error: file \"{fileName}\" doesn't exist **\n")