import sys
import time
from helperfunctions import Helperfunctions
from FileDescriptors.DataSet import DataSet
from FileDescriptors.TempTable import TempTable
from AutoTyper import  AutoTyper
import pyperclip
from tqdm.auto import trange
from tqdm import tqdm

hf = Helperfunctions()

datasetname = "dsstamprostercodeout.i"
doInput = False

if len(sys.argv) >= 2:
    datasetname = sys.argv[1]
    if sys.argv[1] == "input":
        doInput = True

if doInput:
    datasetname = input("Temptable Name? -->: ")
    # if datasetname.startswith("ds"):
    #     datasetname = datasetname[2:]

filenames = hf.ListFiles(hf.folder, hf.folderending, datasetname)
filename = filenames[0]
file = DataSet(hf.folder, filename)
file.analyse()

print("Alt-tab to confluence now within 2 seconds")
time.sleep(2)

keyboard = AutoTyper()
keyboard.waittime = 0.20
keyboard.linewrite(file.name)
keyboard.tab()
for temptable in tqdm(file.temptables, desc=file.name):
    keyboard.linewrite(temptable.name)
    keyboard.tab()
    for field in tqdm(temptable.fields, desc=temptable.name+":names"):
        keyboard.linewrite(field.name)
        keyboard.shiftenter()
    keyboard.tab()
    for field in tqdm(temptable.fields, desc=temptable.name+":types"):
        keyboard.linewrite(field.type.upper())
        keyboard.shiftenter()
    keyboard.tab()
    for field in tqdm(temptable.fields, desc=temptable.name+":commentary"):
        keyboard.linewrite(field.commentary)
        keyboard.shiftenter()
    keyboard.tab(2)

