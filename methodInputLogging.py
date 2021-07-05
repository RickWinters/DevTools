import sys
import time

from helperfunctions import Helperfunctions
from FileDescriptors.DataSet import DataSet
from AutoTyper import AutoTyper
import pyperclip

hf = Helperfunctions()

#initialize array and add first lines
code = []
inputFileName = "btRosterCopy"
methodname = "FetchRosterCopyList"
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
    inputFileName = input("Filename? -->: ")
    methodname = input("Method or procedurename? -->: ")

#open file
selectedFile = hf.getAnalysedFile(inputFileName)
if not selectedFile:
    print("Selected file not found.")
    quit()

if selectedFile.filename.endswith(".cls"):
    isClassFile = True
else:
    isClassFile = False

if isClassFile:
    selectedMethod = []
    for method in selectedFile.methods:
        if method.name.lower() == methodname.lower():
            selectedMethod = method
            break
    else:
        print("Selected method not found.")
else:
    if methodname:
        selectedMethod = []
        for procedure in selectedFile.procedures:
            if procedure.name.lower() == methodname.lower():
                selectedMethod = procedure
    else:
        selectedMethod = selectedFile

longestparam = 0
for parameter in selectedMethod.parameters:
    if len(parameter.name) > longestparam:
        longestparam = len(parameter.name)

code.append("message \"" + selectedMethod.name + ":\" skip")
code.append("        \" - caller" + (" " * (longestparam - 6)) + " = \" + program-name(2) skip" )
for parameter in selectedMethod.parameters:
    line = "        \" - " + parameter.name + (" "*(longestparam -len(parameter.name))) + " = \" + "
    if parameter.type == "date":
        line += "string(" + parameter.name + ", \"99-99-9999\")"
    elif parameter.type == "character":
        line += "quoter(" + parameter.name + ")"
    else:
        line += "string(" + parameter.name + ")"
    code.append(line + " skip")
code.append("view-as alert-box.")


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




