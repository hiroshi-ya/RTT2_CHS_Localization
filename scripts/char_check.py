# This script makes sure that all the characters in the text files can be found in the dictionary.
# Author: HiroshiYa

import time

def load_first_dict(first_dict_path, enc):
    hex_to_char = {} # dictionary
    chars_first = set() # hash lookup
    with open(first_dict_path, 'r', encoding=enc) as f:
        for line in f:
            if not line or '=' not in line:
                continue
            hex_code, char_NL = line.split('=', 1)
            char = char_NL[:-1] # ignore '\n'
            hex_to_char[hex_code] = char
            chars_first.add(char)
    return hex_to_char, chars_first

def load_second_dict(second_dict_path, enc, hex_to_char, chars_first) -> dict:
    # dictionary based on the first dictionary, return type is {char: char}
    replacement_map = {}
    with open(second_dict_path, 'r', encoding=enc) as f:
        for line in f:
            if not line or '=' not in line:
                continue
            hex_code, char_NL = line.split('=', 1)
            char = char_NL[:-1] # ignore '\n'
            # Map the character to its replacement from the first dictionary
            if char not in chars_first:
                char_from_first = hex_to_char.get(hex_code)
                if char_from_first != None:
                    replacement_map[char] = char_from_first # dictionary element swap
                else:
                    replacement_map[char] = hex_to_char['81AC'] # if first dictionary lacks the code
    return replacement_map

workPathPrefix = "../sources/work_texts/work_"

workList = {
    "CFG.BIN.TXT" : "../CMN/CMN/CFG/MOD/",
    "CHAP0000.BIN.TXT" : "../CMN/CMN/BIN/MOD/",
    "CHAP0001.BIN.TXT" : "../CMN/CMN/BIN/MOD/",
    "CHAP0002.BIN.TXT" : "../CMN/CMN/BIN/MOD/",
    "CHAP0003.BIN.TXT" : "../CMN/CMN/BIN/MOD/",
    "EBOOT.BIN.TXT" : "../eboots/"
}

table_path = "../sources/enc_table/"

start = time.time()
for name, destPath in workList.items():
    try:
        feboot = open(workPathPrefix + name, "r", encoding="utf-16-le")
        text = list(feboot.read())
        feboot.close()
    except FileNotFoundError:
        print(f"\n** Error: file \"{name}\" doesn't exist **\n")
        continue

    num = len(text)

    first_dict, first_set = load_first_dict(table_path + "Shift-JIS-work.tbl", "utf-16-le")
    replace_dict = load_second_dict(table_path + "Shift-JIS-ru.tbl", "utf-16-le", first_dict, first_set)

    substitute = True
    for i in range(num):
        u = text[i]
        if u in first_set or u.isascii() or i==0:
            continue
        else:
            replace_char = replace_dict.get(u)
            if replace_char == None:
                print("\n** Not found: " + u + "!" + str(i))
                substitute = False
                quit()
            else:
                text[i] = replace_char
                # substitute = True

    if substitute:
        feboot1 = open(destPath + name, "w", encoding="utf-16-le")
        feboot1.write("".join(text))
        feboot1.close()

print("** All found **")
print("   Time: ", time.asctime(time.localtime()))
print("   Cost: ", str(time.time() - start) + "\n")