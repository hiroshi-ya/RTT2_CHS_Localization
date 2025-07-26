# This script repacks the sub level .FAT
# Author: HiroshiYa

import numpy as np
import os
import gzip
from time import sleep

def welcome_seq():
    space = 80
    strings = [
        "This script repacks the sub level .FAT files.",
        "You can enter the name of the FAT file manually.",
        "You can also enter \"all\" to perform multiple unpacks at once.",
        "Entering \"all\" will make the script try repacking every FAT's folder found.",
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
    # global FAT
    addr = 0
    for i in range(byte):
        addr += np.uint32(FAT[initAddr + i]) * (256 ** i)
    return addr

def little_endian_rvrt(initAddr, byte, value:int):
# A little-endian address reverter, replace the original value in the .FAT with the new one
# Only works for FAT, at least for now
# eg. initAddr = 0x00, byte = 4, value = 0x12345678
#   FAT[0x00] FAT[0x01] FAT[0x02] FAT[0x03]
#       0x78      0x56      0x34      0x12
    global FAT
    FAT[initAddr:initAddr+byte] = list(value.to_bytes(byte, "little"))
    # modifier = 0
    # for i in range(byte):
    #     print(i)
    #     value -= modifier
    #     FAT[initAddr + (3-i)] = int(value / (256 ** (3-i)))
    #     print(FAT[initAddr + (3-i)])
    #     modifier = FAT[initAddr + (3-i)] * (256 ** (3-i))
    return

def get_file_name(initAddr):
# Use the initAddr to get the file name in .FAT
# All the names end with 0x00
    # name = ""
    name = np.array([], dtype=np.uint8)
    curr = initAddr
    while FAT[curr] != 0:
        name = np.append(name, FAT[curr])
        curr += 1
    nameStr = name.tobytes().decode("sjis")
    
    return nameStr

def pad_file(fileContent, fileSize):
    pad = fileSize % 16
    result = np.append(fileContent, np.zeros(16-pad, dtype=np.uint8))
    return result

def main():
    global FAT
    fileQuantity = np.uint32(FAT[5]) * 256 + FAT[4]
    processedFileCounter = 0
    print("** Detected file quantity: " + str(fileQuantity) + "\n")
    # sleep(0.5)

    ####################################
    # This is the starting address of the file name section listed in the .FAT
    # Data is 4-byte little-endian
    fileNamesAddress = little_endian_conv(0xF8, 4)
    dataAddressOffset = little_endian_conv(0xFC, 4) # starting address of the data file

    ####################################
    # This is the address of the current file lying in the .DAT
    # Format (little-endian):
    #   {00  01  02  03}    {04  05  06  07}    {08  09  10  11}    {12  13  14  15}
    #   {File Init Addr}    {File Size}         {0000}              {FileName}
    fileIndex = 0x00000100  # initial file address's index in .FAT
    fileAddr  = 0x0         # initial file address in .DAT part of the .FAT
    while True:
        fileNameAddr = little_endian_conv(fileIndex+12, 4)  # The .FAT addr that contains the file's name
        fileName    = get_file_name(fileNameAddr)           # file's name
        fileNameExt = fileName.split('.')[-1]               # file's name's extension
        # readPath    = "general_pic/" + fileName # file's path
        readPath = "../sources/general_pic/" + fileName # file's path in general_pic

        if not os.path.exists(readPath): 
        # if this file is not in general_pic
            readPath = outPath + fileNameExt + "/MOD/" + fileName # file's path in MOD
            if not os.path.exists(readPath): 
            # if this file is not in MOD
                readPath = outPath + fileNameExt + "/" + fileName # file's path
                if not os.path.exists(readPath): 
                # file doesn't exist
                    print("** ERROR: \"" + readPath + "\" doesn't exist **")
                    return
            else:
                print("** MOD " + fileName + " detected **")
        else: 
        # this file is found in general_pic
            if FATName == "INTERMSN": 
            # special treatment for INTERMSN.FAT
                lowPath = "../sources/general_pic/low/" + fileName
                if os.path.exists(lowPath):
                    readPath = lowPath
                    print("** general_pic " + fileName + " (low) detected **")
            else:
                print("** general_pic " + fileName + " detected **")
            # print("** general_pic " + fileName + " detected **")

        # read the current file
        with open(readPath, "rb") as readFile:
            if compressFlag:
                fileContent = np.fromfile(readFile, dtype=np.uint8)     # read the file's content
                fileContentCompressed = np.array(                       # compress the file
                    list(gzip.compress(fileContent)), dtype=np.uint8
                ) 
                fileSize = np.size(fileContent)                         # file's original size
                fileCompressedSize = np.size(fileContentCompressed)     # file's compressed size

                FAT = np.append(                                        # append the padded compressed file to the .FAT
                    FAT, pad_file(fileContentCompressed, fileCompressedSize)
                ) 

                little_endian_rvrt(fileIndex, 4, fileAddr)              # write the address of the current file in .FAT
                little_endian_rvrt(fileIndex+4, 4, fileCompressedSize)  # write the size of the current file after compression in .FAT
                little_endian_rvrt(fileIndex+8, 4, fileSize)            # write the size of the current file before compression in .FAT
                print("** Wrote Compressed " + fileName + " in FATNewContent")
            else:
                fileContent = np.fromfile(readFile, dtype=np.uint8)     # read the file's content
                fileSize = np.size(fileContent)                         # file's original size
                
                FAT = np.append(FAT, pad_file(fileContent, fileSize))   # append the padded file to the .FAT

                little_endian_rvrt(fileIndex, 4, fileAddr)              # write the address of the current file in .FAT
                little_endian_rvrt(fileIndex+4, 4, fileSize)            # write the size of the current file after compression in .FAT
                # little_endian_rvrt(fileIndex+8, 4, 0)            # write the size of the current file before compression in .FAT
                print("** Wrote " + fileName + " in FATNewContent")

        fileAddr = FAT.size - int(dataAddressOffset) # the starting address of the next file
        fileIndex += 0x00000010

        processedFileCounter += 1
        if fileIndex >= fileNamesAddress:
            print("** All detected files processed")
            print("** Detected  file quantity: " + str(fileQuantity))
            print("** Processed file quantity: " + str(processedFileCounter))
            break
    
    ####################################
    # Create the new .FAT
    FATNewFile = dirSuffix + FATName + "_NEW.FAT"
    # os.makedirs(os.path.dirname(FATNewFile), exist_ok=True) # so that open() doesn't complain
    with open(FATNewFile, "wb") as writeFile:
        FAT.tofile(writeFile)
        print("** Wrote " + FATName + "_NEW in " + FATNewFile)

    return

welcome_seq()

dirSuffix = "../CMN/CMN/FAT/"
try:
    keepLooping = True
    while keepLooping:
        userInput = input("File name (enter \"all\" for all FATs): ")
        if userInput == 'all':
            # dirList = next(os.walk('.'))[1]
            dirList = next(os.walk(dirSuffix))[1]
            # keepLooping = False
        elif userInput.lower() == "quit":
            exit_seq()
        else:
            dirList = [userInput]

        for FATName in dirList:
            if FATName.lower() == "general_pic":
                continue
            
            print("** Handling " + FATName + ".FAT **")
            
            outPath = dirSuffix + FATName + "/"
            findPath = outPath + FATName + ".FAT"
            if os.path.exists(findPath):
                FATfile = open(findPath, "rb")
                compressFlag = True
            else:
                findPath = outPath + FATName + "_UNCOMPRESSED.FAT"
                if os.path.exists(findPath):
                    FATfile = open(findPath, "rb")
                    compressFlag = False
                else:
                    print("** " + FATName + " is either not extracted or non-existing **\n")
                    continue

            global FAT
            FAT = np.fromfile(FATfile, dtype=np.uint8)
            if FAT[0:4].tobytes().decode("sjis") != "FAT\x20":
                print("** Invalid FAT file **")
            else:
                # FATNewContent = np.copy(FAT)
                print("** Valid FAT file. Start processing **")
                main()

            FATfile.close()

            print("** Done **\n")
        
except KeyboardInterrupt:
    exit_seq()