# This script unpacks the sub level .FAT
# Author: HiroshiYa

import numpy as np
import os
import gzip
from time import sleep

def welcome_seq():
    space = 80
    strings = [
        "This script unpacks the sub level .FAT files.",
        "You can enter the name of the FAT file manually.",
        "You can also enter \"[your_list].txt\" to perform multiple unpacks at once.",
        "For example, if your list is named as \"sub_list.txt\", enter \"sub_list.txt\".",
        "Each line of the text file is treated as a .FAT file's name.",
        "To Exit, enter \"quit\" or press [Ctrl + C]."
    ]
    print(f"\n{'':*<{space}}")
    for s in strings:
        print(f"* {s:<{space-4}} *")
    print(f"{'':*<{space}}\n")
    return

def exit_seq():
    print("\n** See You **\n")
    quit()

def little_endian_conv(initAddr, byte):
# A little-endian address converter, use the initAddr to calculate the stored value
# Only works for FAT, at least for now
# eg. initAddr = 0x00 and byte = 4
#   yields (concatenate): FAT[0x03] FAT[0x02] FAT[0x01] FAT[0x00]
#                             0x67      0x45      0x23      0x01
    addr = 0
    for i in range(byte):
        addr += np.uint32(FAT[initAddr + i]) * (256 ** i)
    return addr

def get_file_name(initAddr):
# Use the initAddr to get the file name in .FAT
# All the names end with 0x00
    # name = ""
    name = np.array([], dtype=np.uint8)
    curr = initAddr
    while FAT[curr] != 0:
        name = np.append(name, FAT[curr])
        curr += 1
    # print(curr)
    nameStr = name.tobytes().decode("sjis")
    return nameStr

def fileContent_decompress_validater(fileContent):
# Check if the fileContent is a valid gzip file
# If it is, locate its magic number and make a new validated fileContent
# If not, return None
    validated = None
    try:
        # firstNum = fileContent.index(0x1F)
        firstNum = np.where(fileContent == 0x1F)[0][0]
        # secondNum = fileContent.index(0x8B)
        secondNum = np.where(fileContent == 0x8B)[0][0]
    except IndexError:
        print("** Warning: This file is not a gzip file **")

    if (secondNum - firstNum) == 1:
        validated = fileContent[firstNum:] # start the file here
    else:
        print("** Warning: This file is not a gzip file **")

    return validated

def main():
    fileQuantity = np.uint32(FAT[5]) * 256 + FAT[4]
    processedFileCounter = 0
    print("** Detected file quantity: " + str(fileQuantity) + "\n")
    compressFlag = True
    sleep(0.5)

    ####################################
    # This is the starting address of the file name section listed in the .FAT
    # Data is 4-byte little-endian
    fileNamesAddress = little_endian_conv(0xF8, 4)
    DAToffset = little_endian_conv(0xFC, 4)
    # DAToffset = search_offset(fileNamesAddress, fileQuantity)

    ####################################
    # This is the address of the current file lying in the .DAT
    # Format (little-endian):
    #   {00  01  02  03}    {04  05  06  07}    {08  09  10  11}    {12  13  14  15}
    #   {File Init Addr}    {File Size}         {0000}              {FileName}
    fileIndex = 0x00000100 # initial file address's index
    while True:
        # fileIndex    = 0x00000100
        fileAddr     = little_endian_conv(fileIndex, 4)         # Location of the current file in .DAT according to the .FAT
        fileSize     = little_endian_conv(fileIndex+4, 4)       # Size of the current file according to the .FAT
        fileOrigSize = little_endian_conv(fileIndex+8, 4)       # Size of the current file before compression according to the .FAT
        fileNameAddr = little_endian_conv(fileIndex+12, 4)      # The .FAT addr that contains the file's name
        fileName    = get_file_name(fileNameAddr)               # file's name
        fileNameExt = fileName.split('.')[-1]                   # file's name's extension
        fileContent = FAT[fileAddr+DAToffset:fileSize+fileAddr+DAToffset]   # file's content
        writePath   = outPath + fileNameExt + "/" + fileName                # file's output path
        
        os.makedirs(os.path.dirname(writePath), exist_ok=True) # so that open() doesn't complain
        with open(writePath, "wb") as writeFile:
            if fileOrigSize != 0:
                if processedFileCounter == 0:
                    compressFlag = True
                elif compressFlag == False:
                    print("\n** WARNING! Hybrid Compression Detected! **")
                    return
                writeFile.write(gzip.decompress(fileContent))
                print("** Decompressed " + fileName + " in " + writePath)
            else:
                if processedFileCounter == 0:
                    compressFlag = False
                elif compressFlag == True:
                    print("\n** WARNING! Hybrid Compression Detected! **")
                    return
                fileContent.tofile(writeFile)
                print("** Extracted " + fileName + " in " + writePath)

        if fileNameExt[0].upper() == 'X': # special case when the file is individually compressed
            print("** File " + fileName + " is compressed")
            fileContent_decompressable = fileContent_decompress_validater(fileContent) # check if file is valid
            if fileContent_decompressable is not None: # if valid
                decompressedFileName = "".join(fileName.split('.')[0:-1]) + '.G' + fileNameExt[1:]
                writeDecompressPath = outPath + fileNameExt + "/DECOMPRESSED/" + decompressedFileName
                os.makedirs(os.path.dirname(writeDecompressPath), exist_ok=True) # so that open() doesn't complain
                with open(writeDecompressPath, "wb") as writeDecompressedFile:
                    writeDecompressedFile.write(gzip.decompress(fileContent_decompressable))
                    print("** Decompressed " + decompressedFileName + " in " + writeDecompressPath)

        # create an empty folder MOD
        modPath = outPath + fileNameExt + "/MOD"
        os.makedirs(modPath, exist_ok=True)

        fileIndex += 0x00000010
        processedFileCounter += 1
        if fileIndex >= fileNamesAddress:
            print("** All detected files processed")
            print("** Detected  file quantity: " + str(fileQuantity))
            print("** Processed file quantity: " + str(processedFileCounter))
            break
    
    # output the file (create directory accordingly)
    if not compressFlag:
        writePath = outPath + FATName + "_UNCOMPRESSED.FAT"
    else:
        writePath = outPath + FATName + ".FAT"
    os.makedirs(os.path.dirname(writePath), exist_ok=True) # so that open() doesn't complain
    with open(writePath, "wb") as writeFile:
        fileContent = FAT[0:DAToffset]
        fileContent.tofile(writeFile)
        print("** Wrote " + FATName + " in " + writePath)
        # print(fileSize)

    return

welcome_seq()

try:
    while True:
        usrInput = input("File name: ")

        try:
            if usrInput.split('.')[1] == "txt":
                try:
                    with open(usrInput, "r", encoding="UTF-8") as inputFile:
                        FATNames = [line.rstrip() for line in inputFile]
                except FileNotFoundError:
                    print("\n** Error: File doesn't exist **\n")
                    continue
            else:
                print("\n** Error: Not a txt file **\n")
                continue
        except IndexError:
            if usrInput.lower() == "quit":
                exit_seq()
            else:
                FATNames = [usrInput]

        for FATName in FATNames:
            dirSuffix = "../CMN/CMN/FAT/"
            outPath = dirSuffix + FATName + "/"
            try:
                FATfile = open(dirSuffix + FATName + ".FAT", "rb")

                FAT = np.fromfile(FATfile, dtype=np.uint8)
                if FAT[0:4].tobytes().decode("sjis") != "FAT\x20":
                    print("** Invalid FAT file **")
                else:
                    print("** Valid FAT file. Start processing **")
                    main()

                FATfile.close()
                print("** Done **\n")
            except FileNotFoundError:
                print("\n** Error: File \"" + FATName + ".FAT\" doesn't exist **\n")
                continue

except KeyboardInterrupt:
    exit_seq()