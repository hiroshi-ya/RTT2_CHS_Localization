# This script fuses all the font images into the UIMG1.BIN
# Author: HiroshiYa

from time import sleep
from PIL import Image
import os
import numpy as np

def error_trap():
    # while True:
    #     sleep(1E6)
    quit()
    return

def index_fuser(red, green):
# 1. Takes the rgb info from the red font image and the green font image
# 2. Compare the values and assign the index
# 3. Return the index
    if red[0] < 63:
        rindex = 0
    elif red[0] >= 63 and red[0] < 160:
        rindex = 1
    elif red[0] >= 160 and red[0] < 220:
        rindex = 2
    else:
        rindex = 3

    if green[1] < 63:
        gindex = 0
    elif green[1] >= 63 and green[1] < 160:
        gindex = 1
    elif green[1] >= 160 and green[1] < 220:
        gindex = 2
    else:
        gindex = 3

    return int(rindex*4 + gindex)

fontSize = 256

# redPath = "red/png/"
# greenPath = "green/png/"

fontPath = "../sources/font/"
binPath = "../CMN/CMN/BIN/"

red = "red/R"
green = "green/G"
redPNG = "red/png/R"
greenPNG = "green/png/G"
# indexPNG = "Index.png"
PNG = ".png"
BMP = ".bmp"

byteSize = int(fontSize*fontSize/2) # size of one pic
overallSize = 20 * byteSize # size of all pics combined
overallContent = np.zeros(overallSize, np.uint8) # the file array

# loop that fuses all 20 font pics
for i in range(20):
    print("** Processing pair number " + str(i) + " **")
    redImagePath = fontPath + redPNG + str(i) + PNG
    if not os.path.exists(redImagePath):
        redImagePath = fontPath + red + str(i) + BMP
        if not os.path.exists(redImagePath):
            print(f"\n** Error: missing tiles [{redPNG+str(i)}.png] **\n")
            quit()

    redImage = Image.open(redImagePath)
    redArr = np.array(redImage)

    greenImagePath = fontPath + greenPNG + str(i) + PNG
    if not os.path.exists(greenImagePath):
        greenImagePath = fontPath + green + str(i) + BMP
        if not os.path.exists(greenImagePath):
            print(f"\n** Error: missing tiles [{greenPNG+str(i)}.png] **\n")
            quit()

    greenImage = Image.open(greenImagePath)
    greenArr = np.array(greenImage)

    if (redArr.shape[0] != redArr.shape[1] or 
        greenArr.shape[0] != greenArr.shape[1] or 
        redArr.shape[0] != greenArr.shape[0] or 
        greenArr.shape[0] != fontSize):

        print("*** Error: Invalid Image File ***")
        error_trap()

    # fuse the red and green pixels into a byte file
    redArrRe = redArr.reshape((int(fontSize*fontSize), 3)) # flatten the first two indices of the image array
    greenArrRe = greenArr.reshape((int(fontSize*fontSize), 3)) # flatten the first two indices of the image array

    for j in range(byteSize):
    # note that the binary images are little endian, hence the first and second half are opposite
    # one byte is 8 bits = 2 pixels (4bpp font)
        firstHalf = index_fuser(redArrRe[2*j+1], greenArrRe[2*j+1])
        secondHalf = index_fuser(redArrRe[2*j], greenArrRe[2*j])
        currentByte = firstHalf * 16 + secondHalf
        overallContent[i*byteSize + j] = currentByte

try:
    fontFile = open(binPath + "UIMG1.BIN", "rb")
    fontFileContent = np.fromfile(fontFile, dtype=np.uint8)
    fontFile.close()

    # outputName = "fontMod.bin"
    # with open(binPath + "/MOD/" + outputName, "wb") as outputFile:
    #     overallContent.tofile(outputFile)

    print("** Building UIMG1 **")
    outputName = "UIMG1.BIN"
    with open(binPath + "/MOD/" + outputName, "wb") as outputFile:
        finalFile = np.concatenate((fontFileContent[0:138240], overallContent), dtype=np.uint8)
        finalFile.tofile(outputFile)

    print("* Done *")

except FileNotFoundError:
    print(f"\n** Error: file \"UIMG1.BIN\" doesn't exist **\n")
    quit()