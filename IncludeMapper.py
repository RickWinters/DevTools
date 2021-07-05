import sys
import uuid

from FileDescriptors.DataSet import DataSet
from FileDescriptors.TempTable import TempTable
from FileDescriptors.ProcedureFile import Procedurefile
from FileDescriptors.ClassFile import Classfile
from tqdm import tqdm

from helperfunctions import Helperfunctions

hf = Helperfunctions()
indexes = hf.getIndexFile()
files = hf.readAnalysedFiles()

print("Adding temptables and datasets to filelist")
tqdmloop = tqdm(indexes)
for index in tqdmloop:
    if index["Filename"].endswith(".i"):
        if index["Filename"].startswith("ds"):
            tqdmloop.set_description(index["Path"])
            file = DataSet(hf.folder, index["Path"], indexes)
            file.analysed = True
            hf.getCode(file)
            file.getIncludes()
            file.checkToCompile()
            files.append(file)
        if index["Filename"].startswith("tt"):
            tqdmloop.set_description(index["Path"])
            file = TempTable(hf.folder, index["Path"], indexes = indexes)
            files.append(file)

nodelist = []

class Node:
    def __init__(self, filename, filepath, file):
        self.filename = filename
        self.filepath = filepath
        self.file = file
        self.children = []
        self.parents = []
        self.level = 0
        self.id = uuid.uuid1()
        self.startingpoint = False
        self.hasParents = False
        self.analysed = False
        self.istemptable = False
        if filename.lower().startswith("tt") and filename.lower().endswith(".i"):
            self.istemptable = True

    def analyse(self):
        if self.level < 0:
            self.level = 0
            self.increaseChildLevels()
        if not self.analysed:
            print("Analysing " + self.filepath + "/" + self.filename)
            self.analysed = True
            if not self.file.analysed:
                self.file.analysed = True
                self.file.getIncludes()
            if self.filename.endswith(".i") and self.filename.startswith("ds"):
                self.setChildren()
            if (self.startingpoint == True and not self.hasParents) or (self.filename.endswith(".i") and self.filename.startswith("ds")):
                self.findParents()
            for child in self.children:
                child.analyse()
                if child.istemptable:
                    child.file.datasets.append(self.file)
                    hf.getCode(child.file)
            for parent in self.parents:
                parent.analyse()

    def findParents(self):
        for file in files:
            for include in file.includes:
                if include.filename == self.filename:
                    for parent in self.parents:
                        if parent.filename == file.filename and parent.filepath == file.filepath:
                            break
                    else:
                        for node in nodelist:
                            if node.filename == file.filename:
                                self.parents.append(node)
                                node.children.append(self)
                                self.hasParents = True
                                break
                        else:
                            parentNode = Node(file.filename, file.filepath, file)
                            parentNode.level = self.level - 1
                            parentNode.children.append(self)
                            nodelist.append(parentNode)
                            self.parents.append(parentNode)
                            self.hasParents = True
                    break

    def setChildren(self):
        for include in self.file.includes:
            childfound = False
            nodefound = False
            for child in self.children:
                if child.filename == include.filename:
                    childfound = True
                    break
            if childfound:
                continue
            for node in nodelist:
                if node.filename == include.filename and node.filepath == include.filepath:
                    self.children.append(node)
                    nodefound = True
                    break
            if nodefound:
                continue
            for file in files:
                if file.filename.lower() == include.filename.lower():
                    childnode = Node(include.filename, include.filepath, file)
                    childnode.level = self.level + 1
                    childnode.parents.append(self)
                    childnode.hasParents = True
                    self.children.append(childnode)
                    nodelist.append(childnode)
                    break


    def increaseChildLevels(self):
        for child in self.children:
            child.level = self.level + 1
            child.increaseChildLevels()

    def getText(self):
        text = ("| " * self.level) + self.filepath + self.filename + (" <---- " * self.startingpoint) + "  " + self.file.message
        if self.file.type == "ClassFile" or self.file.type == "ProcedureFile":
            for include in self.file.includes:
                if not include.found:
                    text += "\n\tMISSING " + include.tocompilemessage + "(module='" + include.filename.replace(".i", "") + "')"
        for child in self.children:
            text += "\n" + child.getText()
        return text

    def __str__(self):
        return self.getText()

nodes = []
parentnodes = []
inputfilename = "dsemployeerosterinfoout12.i"
doinput = False
runagain = False

if len(sys.argv) >= 2:
    if sys.argv[1] == "input":
        doinput = True

if doinput:
    inputfilename = input("Filename? -->: ")

for file in files:
    if inputfilename.lower() == file.filename.lower():
        node = Node(file.filename, file.filepath, file)
        node.startingpoint = True
        nodelist.append(node)
        break
else:
    print("File not found")
    quit()

node.analyse()

for node in nodelist:
    if not node.hasParents:
        node.level = 0
        node.increaseChildLevels()
        parentnodes.append(node)
    if node.istemptable:
        node.file.checkMasterToCompileOfDatase()
    else:
        node.file.analyse()

for node in parentnodes:
    print("\n")
    text = str(node)
    print(text)
