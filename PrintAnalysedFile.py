import sys
from helperfunctions import Helperfunctions


hf = Helperfunctions()

doInput = False

printcode = False
inputfilename = "beclient"
files = []

if len(sys.argv) >= 2:
    if sys.argv[1] == "input":
        doInput = True
        printcode = False

if doInput:
    inputfilename = input("Filename? -->: ")
    printcodeinput = input("Print analysed source code? -->: ")
    if printcodeinput == "y" or printcodeinput == "yes":
        printcode = True

file = hf.getAnalysedFile(inputfilename)
file.cleanUp()
file.analyse()
print(file)
if printcode:
    print("**********************************************************************")
    print("              END OF FILE ANALYSIS, START OF SOURCE CODE")
    print("**********************************************************************")
    for line in file.lines:
        print(line)