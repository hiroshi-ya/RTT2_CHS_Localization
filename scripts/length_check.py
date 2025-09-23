# This script makes sure that all the lines in the text files are within byte-length limits.
# Author: HiroshiYa

import time

# def load_first_dict(first_dict_path, enc):
#     hex_to_char = {} # dictionary
#     chars_first = set() # hash lookup
#     with open(first_dict_path, 'r', encoding=enc) as f:
#         for line in f:
#             if not line or '=' not in line:
#                 continue
#             hex_code, char_NL = line.split('=', 1)
#             char = char_NL[:-1] # ignore '\n'
#             hex_to_char[hex_code] = char
#             chars_first.add(char)
#     return hex_to_char, chars_first

# def load_second_dict(second_dict_path, enc, hex_to_char, chars_first) -> dict:
#     # dictionary based on the first dictionary, return type is {char: char}
#     replacement_map = {}
#     with open(second_dict_path, 'r', encoding=enc) as f:
#         for line in f:
#             if not line or '=' not in line:
#                 continue
#             hex_code, char_NL = line.split('=', 1)
#             char = char_NL[:-1] # ignore '\n'
#             # Map the character to its replacement from the first dictionary
#             if char not in chars_first:
#                 char_from_first = hex_to_char.get(hex_code)
#                 if char_from_first != None:
#                     replacement_map[char] = char_from_first # dictionary element swap
#                 else:
#                     replacement_map[char] = hex_to_char['81AC'] # if first dictionary lacks the code
#     return replacement_map

def load_first_dict(first_dict_path, enc):
    hex_to_char = {} # dictionary
    char_to_hex = {} # reverse dictionary
    chars_first = set()
    with open(first_dict_path, 'r', encoding=enc) as f:
        for line in f:
            if not line or '=' not in line:
                continue
            hex_code, char_NL = line.replace("\ufeff", "", 1).split('=', 1)
            char = char_NL[:-1] # ignore '\n'
            hex_to_char[hex_code] = char
            char_to_hex[char] = hex_code
            chars_first.add(char)
    return hex_to_char, char_to_hex, chars_first



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
        # text = list(feboot.read())
        lines = list(feboot.readlines())
        feboot.close()
    except FileNotFoundError:
        print(f"\n** Error: file \"{name}\" doesn't exist **\n")
        continue

    # num = len(text)
    # num = len(lines)

    # load dictionaries
    first_dict, first_dict_rev, first_set = load_first_dict(table_path + "Shift-JIS-work.tbl", "utf-16-le")
    second_dict_rev, second_set = load_first_dict(table_path + "Shift-JIS-ru.tbl", "utf-16-le")[1:]

    for line in lines:
        lineSplit = line.split(',', maxsplit=2)
        if len(lineSplit) < 3:
            continue
        
        lineLimit = int(lineSplit[1])
        lineContent = lineSplit[2].rstrip('\n')
        codeLength = 0 # byte length

        # find existence and calculate byte length
        found = True
        withinLimit = True
        for char in lineContent:
            # u = text[i]
            if char in first_set:
                char_code = first_dict_rev.get(char)
                codeLength += len(char_code)/2
                # print(char_code.encode("utf-8"))
                # continue
            else:
                if char in second_set:
                    char_code = second_dict_rev.get(char)
                    codeLength += len(char_code)/2
                    # if char_code in first_dict:
                    #     text[i] = first_dict.get(char_code)
                    # else:
                    #     text[i] = first_dict.get("81AC")
                    # notFoundru.add(u)
                else:
                    found = False
                    break
        if codeLength > lineLimit:
            withinLimit = False
            print(f"*** Limit Exceeded:\n\"{line.rstrip('\n')}\" from [{name}]\n")
            exit()
        if not found:
            break

    if not found:
        break

    # substitute = True
    # for i in range(num):
    #     u = text[i]
    #     if u in first_set or u.isascii() or i==0:
    #         continue
    #     else:
    #         replace_char = replace_dict.get(u)
    #         if replace_char == None:
    #             print("\n** Not found: " + u + "!" + str(i))
    #             substitute = False
    #             quit()
    #         else:
    #             text[i] = replace_char
    #             # substitute = True

    # if substitute:
    #     feboot1 = open(destPath + name, "w", encoding="utf-16-le")
    #     feboot1.write("".join(text))
    #     feboot1.close()

if not found:
    print("** Some chars are not found **")
    print("** Please run char_check.py **")

else:
    print("** All passed **")
    print("   Time: ", time.asctime(time.localtime()))
    print("   Cost: ", str(time.time() - start) + "\n")