import sys
import time

from helperfunctions import Helperfunctions
from FileDescriptors.DataSet import DataSet
from AutoTyper import AutoTyper
import pyperclip

hf = Helperfunctions()

#initialize array and add first lines
code = []
datasetName = "dsteamrosterout46"
dsName = ""
write = False
copy = False
doInput = False

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


if not datasetName.startswith("ds"):
    datasetName = "ds" + datasetName
dsName = hf.RemoveNumbersAtEnd(datasetName)
if not datasetName.endswith(".i"):
    datasetName += ".i"

#open file
dataset = ""
indexes = hf.getIndexFile()
for index in indexes:
    if datasetName in index["Filename"]:
        dataset = DataSet(hf.folder, index["Path"])
        print("analysing " + dataset.filename)
        dataset.analyse()

#extract included temptables
ttnames = []
amount = 0
maxlength = 0
for temptable in dataset.temptables:
    ttnames.append(temptable.name)

code.append("prepare" + dsName + "(")
code.append("dataset-handle " + dsName + "Handle by-reference,")

#add temptables in method definition
for i, ttname in enumerate(ttnames):
    line = "output " + ttname + "BufferHandle"
    if i == len(ttnames) - 1:
        line += ")."
    else:
        line += ","
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




