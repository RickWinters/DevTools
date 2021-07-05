import sys
import time

from helperfunctions import Helperfunctions
from FileDescriptors.DataSet import DataSet
from AutoTyper import AutoTyper
import pyperclip

hf = Helperfunctions()

code = []
datasetName = "dsrostercopy"
write = False
copy = False
doInput = False
onlyVars = False

if len(sys.argv) >= 2:
    datasetName = sys.argv[1]
    if sys.argv[1] == "input":
        doInput = True

if len(sys.argv) >= 3:
    if sys.argv[2] == "write":
        write = True
    elif sys.argv[2] == "copy":
        copy = True

if doInput:
    datasetName = input("Dataset Name? -->: ")
    onlyVarsInput = input("Only get var names? [yes, no] -->: ")
    if onlyVarsInput == "yes":
        onlyVars = True

if not datasetName.startswith("ds"):
    datasetName = "ds" + datasetName
if not datasetName.endswith(".i"):
    datasetName += ".i"

indexes = hf.getIndexFile()
for index in indexes:
    if datasetName.lower() in index["Filename"].lower():
        dataset = DataSet(hf.folder, index["Path"])
        dataset.analyse()
        break

#extract included temptables
ttnames = []
amount = 0
maxlength = len(dataset.name) + 6

for temptable in dataset.temptables:
    ttnames.append(temptable.name)

line = dataset.name + "Handle"
if not onlyVars:
    line = "define variable " + line
if not onlyVars:
    line += " " * (maxlength - len(dataset.name))
if not onlyVars:
    line += " as handle no-undo."
code.append(line)
#add temptables in method definition
for i, ttname in enumerate(ttnames):
    line = ttname + "BufferHandle"
    if not onlyVars:
        line = "define variable " + line
    if not onlyVars:
        line += " " * (maxlength - len(ttname))
    if not onlyVars:
        line += " as handle no-undo."
    code.append(line)

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
