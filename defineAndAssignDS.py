import sys
import time

from helperfunctions import Helperfunctions
from FileDescriptors.DataSet import DataSet
from AutoTyper import AutoTyper
import pyperclip

hf = Helperfunctions()

code = []
datasetName = "drv/shared/dsemployment.i"
domain = "drv"
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
    domain = input("Domain -->: ")

if not "/" in datasetName:
    if not datasetName.startswith("ds"):
        datasetName = "ds" + datasetName
    if not datasetName.endswith(".i"):
        datasetName += ".i"

indexes = hf.getIndexFile()
for index in indexes:
    if datasetName.lower() in index["Path"].lower():
        dataset = DataSet(hf.folder, index["Path"])
        print("analysing " + dataset.filename)
        dataset.analyse()
        break

ttnames = []
amount = 0
maxlength = len(dataset.name) + 6

for temptable in dataset.temptables:
    ttnames.append(temptable.name)

## create define variable list
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
code.append("")

#create ds handle
code.append("run unit4/cura/" + domain + "/server/create"+dataset.name+".p")
code.append("  (output dataset-handle " + dataset.name + "Handle).")
code.append("")

## assign buffer hadles
code.append("assign")
for ttname in ttnames:
    line = "  "
    line += ttname
    line += "BufferHandle "
    line += " " * (maxlength - len(ttname))
    line += "= "
    line += dataset.name
    line += "Handle:get-buffer-handle(\""
    line += ttname
    line += "\")"
    code.append(line)
code.append("  .")




























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