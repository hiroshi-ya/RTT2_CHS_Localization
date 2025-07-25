from time import sleep
import subprocess

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

defaultRowLength = 36
rowLengthSet = defaultRowLength

while True:
    # user input string
    inOri = input("\nEnter Kanji Line: ")
    if inOri.isnumeric():
        rowLengthSet = int(inOri) * 2
        print("* Set Row: " + str(rowLengthSet) + " bytes *")
        continue
    text = list(inOri)
    num = len(text)

    # load dictionaries
    first_dict, first_dict_rev, first_set = load_first_dict('Shift-JIS-work.tbl', 'utf-16-le')
    second_dict_rev, second_set = load_first_dict('Shift-JIS-ru.tbl', 'utf-16-le')[1:]

    # special characters flag
    specialFlag = False
    specialNameFlag = False
    specialColorFlag = False

    # data init.
    print("")
    codeLength = 0 # byte length
    notFound = set() # hash that shows the character that doesn't exist
    notFoundru = set() # hash that shows the character that doesn't exist in work but in ru
    
    # find existence and calculate byte length
    found = True
    for i in range(num):
        u = text[i]
        if u in first_set:
            char_code = first_dict_rev.get(u)
            codeLength += len(char_code)/2
            # print(char_code.encode("utf-8"))
            # continue
        else:
            if u in second_set:
                char_code = second_dict_rev.get(u)
                codeLength += len(char_code)/2
                if char_code in first_dict:
                    text[i] = first_dict.get(char_code)
                else:
                    text[i] = first_dict.get("81AC")
                notFoundru.add(u)
            else:
                found = False
                notFound.add(u)

    inOri = ''.join(text)
    if found:
        # display the string according to the format
        
        # get rid of $c registers
        inOri = inOri.replace('$cf', '')
        for i in range(10):
            inOri = inOri.replace('$c'+str(i), '')
        
        # list for displaying
        finalDisplayList = []

        # swap the $e2$ec register
        if inOri.find('$e2$ec') != -1:
            finalDisplayList.append(inOri.replace('$e2$ec', '三个字'))
            finalDisplayList.append(inOri.replace('$e2$ec', '五个字中尉'))
            finalDisplayList.append(inOri.replace('$e2$ec', '四字成语中尉'))
        else:
            finalDisplayList.append(inOri)

        # display all the final strings
        for finalString in finalDisplayList:
            rowLength = 0 # row length counter
            for char in finalString:
                rowLength += len(first_dict_rev.get(char))/2
                if char != '↙' and rowLength <= rowLengthSet:
                    print(char, end='')
                else:
                    print('')
                    if char != '↙':
                        print(char, end='')
                        rowLength = len(first_dict_rev.get(char))/2
                    else:
                        rowLength = 0
            print('\n-------------------------\n')

        if len(notFoundru) != 0:
            for nf in notFoundru:
                print("** Not found: " + nf + " but found in ru")
            print("")
        print("Byte Length = ", codeLength)

    else:
        for nf in notFound:
            print("** Not found: " + nf + "!")
        # for nf in notFoundru:
        #     print("Not found: " + nf + " but found in ru")