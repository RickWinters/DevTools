import sys
import time
from helperfunctions import Helperfunctions
from FileDescriptors.TempTable import TempTable
from AutoTyper import  AutoTyper
from tqdm import tqdm

hf = Helperfunctions()

temptablename = "ttPlanPeriodOut.i"
doInput = False

if len(sys.argv) >= 2:
    datasetname = sys.argv[1]
    if sys.argv[1] == "input":
        doInput = True

if doInput:
    temptablename = input("Temptable Name? -->: ")
    if not temptablename.startswith("tt"):
        temptablename = "tt" + temptablename
    if not temptablename.endswith(".i"):
        temptablename += ".i"

filenames = hf.ListFiles(hf.folder, hf.folderending, temptablename)
filename = filenames[0]
temptable = TempTable(hf.folder, filename)
temptable.analyse(None)

print("Alt-tab to confluence now within 2 seconds")
time.sleep(2)

keyboard = AutoTyper()
keyboard.waittime = 0.10
keyboard.linewrite(temptable.name)
keyboard.tab()
for field in tqdm(temptable.fields, desc=temptable.name+":names"):
    keyboard.linewrite(field.name)
    keyboard.shiftenter()
keyboard.backspace()
keyboard.tab()
for field in tqdm(temptable.fields, desc=temptable.name+":types"):
    keyboard.linewrite(field.type.upper())
    keyboard.shiftenter()
keyboard.backspace()
keyboard.tab()
for field in tqdm(temptable.fields, desc=temptable.name+":commentary"):
    keyboard.linewrite(field.commentary)
    keyboard.shiftenter()
keyboard.backspace()



