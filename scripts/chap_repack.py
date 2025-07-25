# Rebuild the top level .DAT/.FAT

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

def little_endian_rvrt(initAddr, byte, value:int):
# A little-endian address reverter, replace the original value in the .FAT with the new one
# Only works for FAT, at least for now
# eg. initAddr = 0x00, byte = 4, value = 0x12345678
#   FAT[0x00] FAT[0x01] FAT[0x02] FAT[0x03]
#       0x78      0x56      0x34      0x12
    global FAT
    FAT[initAddr:initAddr+byte] = list(value.to_bytes(byte, "little"))
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
    # if pad == 0:
    #     return fileContent
    # else:
    result = np.append(fileContent, np.zeros(16-pad, dtype=np.uint8))
    # newSize = result.size
    # newRows = (newSize / 16) % 4 # pad zero-rows to make it aligned ((addr/0x10)%4 == 0)
    # if newRows != 0:
    #     result = np.append(result, np.zeros(int(16*(4-newRows)), dtype=np.uint8))
    return result

def main():
    global FAT
    # global DAT

    # write in the MOD folder instead of "[name]_NEW" folder
    # this is special for the CHAP000x_DAT.DAT
    DATNewFile = "MOD/" + FATName + ".DAT"
    os.makedirs(os.path.dirname(DATNewFile), exist_ok=True) # so that open() doesn't complain
    DATFile = open(DATNewFile, "wb")

    # DAT = np.array([], dtype=np.uint8)
    
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
    fileIndex = 0x00000100  # initial file address's index in .FAT
    fileAddr  = 0x0         # initial file address in .DAT
    
    while True:
        fileNameAddr = little_endian_conv(fileIndex+12, 4)      # The .FAT addr that contains the file's name
        fileName     = get_file_name(fileNameAddr)              # file's name
        fileNameExt  = fileName.split('.')[-1]                  # file's name's extension
        readPath     = outPath + fileNameExt + "/" + fileName       # file's path
        readPathMod  = outPath + fileNameExt + "/MOD/" + fileName   # moded file's path
        if fileNameExt == "FAT":                                    # if a FAT file, check for NEW version
            newName = fileName.split('.')[0] + "_NEW.FAT"
            newPath = outPath + "FAT/" + newName
            folderPath = outPath + "FAT/" + fileName.split('.')[0]
            if os.path.exists(newPath) and os.path.exists(folderPath): # only write NEW file if its folder exists
                print("** " + newName + " detected **")
                readPath = newPath

        elif fileNameExt == "GIM":
            newPath = outPath + "FAT/generalpic/" + fileName
            if os.path.exists(newPath):
                print("** MOD " + fileName + " detected **")
                readPath = newPath

        if os.path.exists(readPathMod):
            print("** MOD " + fileName + " detected **")
            readPath = readPathMod
        
        elif not os.path.exists(readPath):
            print("** ERROR: \"" + readPath + "\" doesn't exist **")
            return

        # read the current file
        with open(readPath, "rb") as readFile:
            fileContent = np.fromfile(readFile, dtype=np.uint8)     # read the file's content
            fileSize = np.size(fileContent)                         # file's original size

            # DAT = np.append(DAT, pad_file(fileContent, fileSize))   # append the padded compressed file to the .FAT
            currentFile = pad_file(fileContent, fileSize)
            currentFile.tofile(DATFile)

            little_endian_rvrt(fileIndex, 4, fileAddr)              # write the address of the current file in .FAT
            little_endian_rvrt(fileIndex+4, 4, fileSize)            # write the size of the current file after compression in .FAT
            print("** Wrote " + fileName + " in new FAT&DAT")

        fileAddr += currentFile.size # the starting address of the next file
        fileIndex += 0x00000010

        processedFileCounter += 1
        if fileIndex >= fileNamesAddress:
            print("** All detected files processed")
            print("** Detected  file quantity: " + str(fileQuantity))
            print("** Processed file quantity: " + str(processedFileCounter))
            break
    
    ####################################
    # Create the new .FAT and .DAT
    # FATNewFile = FATName + "_NEW/" + FATName + ".FAT"
    FATNewFile = "../FAT/" + FATName + "_NEW.FAT"
    # DATNewFile = FATName + "_NEW/" + FATName + ".DAT"
    os.makedirs(os.path.dirname(FATNewFile), exist_ok=True) # so that open() doesn't complain
    with open(FATNewFile, "wb") as writeFile:
        FAT.tofile(writeFile)
        print("** Wrote " + FATName + " in " + FATNewFile)

    DATFile.close()
    return

while True:
    FATName = input("File name: ")
    outPath = FATName + "/"
    # FATfile = open(FATName + ".FAT", "rb")
    FATfile = open("../FAT/" + FATName + ".FAT", "rb") # this is special for the CHAP000x_DAT.DAT

    global FAT
    FAT = np.fromfile(FATfile, dtype=np.uint8)
    if FAT[0:4].tobytes().decode("sjis") != "FAT\x20":
        print("** Invalid FAT file **")
    else:
        print("** Valid FAT file. Start processing **")
        main()

    FATfile.close()

    print("** Done **\n")