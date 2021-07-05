import sys
import time
from helperfunctions import Helperfunctions
from FileDescriptors.TempTable import TempTable
from AutoTyper import  AutoTyper
import pyperclip

hf = Helperfunctions()

code = []
temptablename = "employmenthirevalidity"
write = False
copy = False
doInput = False

if len(sys.argv) >= 2:
    temptablename = sys.argv[1]
    if sys.argv[1] == "input":
        doInput = True

if len(sys.argv) >= 3:
    print(sys.argv[2])
    if sys.argv[2] == "write":
        write = True
    if sys.argv[2] == "copy":
        copy = True

if doInput:
    temptablename = input("Temptable Name? -->: ")
    if temptablename.startswith("tt"):
        temptablename = temptablename[2:]

if not temptablename.startswith("tt"):
    temptablename = "tt" + temptablename
if not temptablename.endswith(".i"):
    temptablename += ".i"

code = []

temptable = None
indexes = hf.getIndexFile()
for index in indexes:
    if temptablename.lower() == index["Filename"].lower():
        temptable = TempTable(hf.folder, index["Path"])
        break

if temptable:
    code.append("method private void defaultNew" + temptable.name + "Record(")
    code.append("  " + temptable.name + "BufferHandle as handle):")
    code.append("  ")
    code.append("  assign")

    print("analysing file " + temptable.filename)
    temptable.analyse()
    for field in temptable.fields:
        line = "      " + temptable.name + "BufferHandle::" + field.name + " = "
        if field.type == "character":
            line += "\"unit-test\""
        elif field.type == "date" or field.type == "datetime" or field.type == "datetime-tz":
            line += "today"
        elif field.type == "int64" or field.type == "integer":
            line += "0"
        elif field.type == "logical":
            line += "true"
        code.append(line)
    code.append("      .")
    code.append("  end method. // defaultNew" + temptable.name + "Record")
    if write:
        print("tab to OEPDS now")
        time.sleep(2)
        keyboard = AutoTyper()
        keyboard.write(code)
        keyboard.pressdelete()
        keyboard.pressdelete()
    elif copy:
        text = ""
        for line in code:
            text += line + "\n"
            pyperclip.copy(text)
        print("\"code copied to clipboard\"")
    else:
        for line in code:
            print(line)
else:
    print("file not found")