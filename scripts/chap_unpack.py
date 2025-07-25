# Decompress the top level .DAT/.FAT

import numpy as np
import os
from time import sleep

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

def main():
    fileQuantity = np.uint32(FAT[5]) * 256 + FAT[4]
    processedFileCounter = 0
    print("** Detected file quantity: " + str(fileQuantity) + "\n")
    sleep(0.5)

    ####################################
    # This is the starting address of the file name section listed in the .FAT
    # Data is 4-byte little-endian
    fileNamesAddress = little_endian_conv(0xF8, 4)

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
        fileNameAddr = little_endian_conv(fileIndex+12, 4)      # The .FAT addr that contains the file's name
        fileName    = get_file_name(fileNameAddr)               # file's name
        fileNameExt = fileName.split('.')[-1]                   # file's name's extension
        fileContent = DAT[fileAddr:fileSize+fileAddr]           # file's content
        writePath   = outPath + fileNameExt + "/" + fileName    # file's output path

        # output the file (create directory accordingly)
        os.makedirs(os.path.dirname(writePath), exist_ok=True) # so that open() doesn't complain
        with open(writePath, "wb") as writeFile:
            fileContent.tofile(writeFile)
            print("** Wrote " + fileName + " in " + writePath)
            # print(fileSize)

        fileIndex += 0x00000010
        processedFileCounter += 1
        if fileIndex >= fileNamesAddress:
            print("** All detected files processed")
            print("** Detected  file quantity: " + str(fileQuantity))
            print("** Processed file quantity: " + str(processedFileCounter))
            break
    return

FATName = input("File name: ")
outPath = FATName + "/"
FATfile = open("../FAT/" + FATName + ".FAT", "rb") # this is special for the CHAP000x_DAT.DAT
DATfile = open(FATName + ".DAT", "rb")

FAT = np.fromfile(FATfile, dtype=np.uint8)
DAT = np.fromfile(DATfile, dtype=np.uint8)
if FAT[0:4].tobytes().decode("sjis") != "FAT\x20":
    print("** Invalid FAT file **")
else:
    print("** Valid FAT file. Start processing **")
    main()

FATfile.close()
DATfile.close()

# input("** Reached the end point. Press anykey to exit **")
print("** Done **")