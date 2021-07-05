import sys
import uuid

from tqdm import tqdm

from FileDescriptors.ProcedureFile import Procedurefile
from FileDescriptors.ClassFile import Classfile

from helperfunctions import Helperfunctions

hf = Helperfunctions()
nodecounter = 0
nodelist = []
maxLevels = 0

class Node:
    def __init__(self, filename, methodname, methodobject, findParents, reanalysefile, reverseLevels, forward, indexes = None):
        self.method = methodobject
        self.filename = filename
        self.methodname = methodname
        self.children = []
        self.parents = []
        self.hasParents = False
        self.findParents = findParents
        self.reverseLevels = reverseLevels
        self.findChilds = forward
        self.id = uuid.uuid1()
        self.analysed = False
        self.recursive = False
        self.isClassFile = False
        self.startingpoint = True
        self.reanalysefile = reanalysefile
        if not indexes:
            indexes = hf.getIndexFile()
        for index in indexes:
            filename = index["Filename"]
            dotind = filename.find(".")
            filename = filename[:dotind]
            if self.filename.lower() == filename.lower():
                self.filename = index["Filename"]
                break
        if self.filename.endswith(".cls"):
            self.isClassFile = True
        self.nodenumber = nodecounter
        nodelist.append(self)

    def analyse(self, files):
        if not self.analysed :
            print("analyisg " + self.filename + ":" + self.methodname)
            self.analysed = True
            if self.findChilds and self.reverseLevels <= maxLevels:
                self.recursive = [parent for parent in self.parents if parent.methodname == self.methodname] == True
                if not self.recursive:
                    if self.isClassFile:
                        self.analyseClassFile(files)
                    else:
                        self.analyseProcedureFile(files)
            if self.findParents and self.reverseLevels != 0:
                self.recursive = [child for child in self.children if child.methodname == self.methodname] == True
                if not self.recursive:
                    self.doFindParents(files)

    def analyseClassFile(self, files):
        for call in self.method.internalcalls:
            tempfiles = [file for file in files if call.propertyname.lower() in file.filename.lower()]
            for file in tempfiles:
                if self.reanalysefile:
                    file.cleanUp()
                file.analyse()
                if file.filename.endswith(".cls"):
                    [self.addChildNode(call.propertyname, call.methodname, method, files) for method in file.methods if
                     method.name == call.methodname]
                else:  # add procedurefile node
                    self.addChildNode(call.propertyname, call.methodname, file, files)
                break

    def analyseProcedureFile(self, files):
        for call in self.method.internalcalls:
            for file in files:
                if call.propertyname.lower() in file.filename.lower():
                    if self.reanalysefile:
                        file.cleanUp()
                    file.analyse()
                    if call.methodname == "":
                        self.addChildNode(call.propertyname, call.methodname, file, files)
                        break
                    else:
                        [self.addChildNode(call.propertyname, call.methodname, fileprocedure, files)
                            for fileprocedure in file.procedures
                            if fileprocedure.name.strip() == call.methodname.strip() and not call.methodname == self.methodname]

    def addChildNode(self, propertyname, methodname, method, files):
        for node in nodelist:
            if node.methodname == methodname and node.filename == propertyname and self.id != node.id:
                self.children.append(node)
                node.parents.append(self)
                node.hasParents = True
                return
        newNode = Node(propertyname, methodname, method, False, self.reanalysefile, self.reverseLevels + 1, self.findChilds)
        newNode.parents.append(self)
        newNode.hasParents = True
        newNode.startingpoint = False
        self.children.append(newNode)
        newNode.analyse(files)
        newNode.nodenumber = self.nodenumber + 1
        child = self.children[0]
        if child.filename == propertyname and child.methodname == methodname and child.startingpoint:
            newNode.startingpoint = True
            self.children.pop(0)

    def addParentNode(self, propertyname, methodname, parent, files):
        for node in nodelist:
            if node.methodname == methodname and node.filename == propertyname and self.id != node.id:
                node.children.append(self)
                self.parents.append(node)
                self.hasParents = True
                return
        newNode = Node(propertyname, methodname, parent, True, self.reanalysefile, self.reverseLevels - 1, self.findChilds)
        newNode.children.append(self)
        #newNode.findChilds = False
        newNode.startingpoint = False
        newNode.findParents = True
        newNode.nodenumber = self.nodenumber + 1
        self.hasParents = True
        self.parents.append(newNode)
        newNode.analyse(files)

    def increaseChildLevels(self):
        for child in self.children:
            child.level += 1
            child.increaseChildLevels()

    def doFindParents(self, files):
        for file in files:
            if file.filename.endswith(".cls"):
                self.doFindParentsClassFile(file,files)
            elif file.filename.endswith(".p"):
                self.doFindParentsProcedureFile(file,files)

    def doFindParentsClassFile(self, file, files):
        for method in file.methods:
            for call in method.internalcalls:
                if call.methodname == self.methodname and call.propertyname == self.filename:
                    self.addParentNode(file.filename, method.name, method, files)

    def doFindParentsProcedureFile(self, file, files):
        for procedure in file.procedures:
            for call in procedure.internalcalls:
                if call.methodname == self.methodname and call.propertyname == self.filename:
                    self.addParentNode(file.filename, procedure.name, procedure, files)

    def getText(self, level = 0):
        text = ("| " * level) + self.filename + ":" + self.methodname + (" RECURSIVE CALL" * self.recursive) + (" <----" * self.startingpoint)
        level += 1
        for child in self.children:
            text += "\n" + child.getText(level)
        return text

    def __str__(self):
        return self.getText()

def returnParentNodes(node):
    parentnodes = []
    if node.hasParents:
        for parent in node.parents:
            if parent.hasParents:
                parentnodes += returnParentNodes(parent)
            else:
                parentnodes.append(parent)
    else:
        parentnodes.append(node)
    return parentnodes

nodes = []
parentnodes = []
inputfilename = "btRosterCopy"
methodname = ""
doinput = False
runagain = True
reverse = False
forward = True
maxLevels = 5
reverseLevels = 3
reAnalyse = False

if len(sys.argv) >= 2:
    if sys.argv[1] == "input":
        doinput = True

while runagain:
    if doinput:
        reverse = False
        reAnalyse = False
        forward = True
        inputfilename = input("Filename? -->: ")
        methodname = input("method or procedurename? -->: ")
        reAnalyseInput = input("analyse inputfile again? [y:n] -->: ")
        if reAnalyseInput == "y" or reAnalyseInput == "yes":
            reAnalyse = True
        reverseinput = input("Do reverse search (can take up al lot of time) [y:n] -->: ")
        if reverseinput == "y" or reverseinput == "yes":
            reverse = True
            reverseLevels = int(input("How many levels back for reverse search? -->: "))
            forwardInput = input("Do Forward search as well? [y:n] -->: ")
            if not (forwardInput == "y" or forwardInput == "yes"):
                forward = False
        if forward:
            while True:
                maxLevels = int(input("How many levels forward? -->: "))
                if (not reverse and maxLevels <= 0) or (reverse and maxLevels <= 1):
                    if reverse:
                        print("Input value bigger than 0")
                    else:
                        print("Input value bigger than 1")
                else:
                    break
        maxLevels += reverseLevels

    isClassFile = True
    indexes = hf.getIndexFile()
    selectedfile = []
    files = []

    print("Searching file: " + inputfilename)
    selectedfile = hf.getAnalysedFile(inputfilename)
    files = hf.readAnalysedFiles(0)

    if selectedfile == []:
        print("file not found, checking index")
        for index in indexes:
            if index["Filename"].lower().startswith(inputfilename.lower()):
                if index["Filename"].lower().endswith(".p") or index["Filename"].lower().endswith(".w"):
                    isClassFile = False
                    selectedfile = Procedurefile(hf.folder, index["Path"])
                elif index["Filename"].lower().endswith(".cls"):
                    selectedfile = Classfile(hf.folder, index["Path"])
                reAnalyse = True
                break
        else:
            print("file not found")
            break
    if selectedfile != []:
        if reAnalyse:
            selectedfile.cleanUp()
        selectedfile.analyse()
        if isClassFile:
            for method in selectedfile.methods:
                if not methodname or methodname.lower() == method.name.lower():
                    print("found method: " + method.name)
                    nodes.append(Node(selectedfile.filename, method.name, method, reverse, reAnalyse, reverseLevels, forward, indexes))
            if nodes == []:
                print("method not found")

        else:
            if methodname:
                for procedure in selectedfile.procedures:
                    if procedure.name.lower() == methodname.lower():
                        nodes.append(Node(selectedfile.filename, procedure.name, procedure, reverse, reAnalyse, reverseLevels, forward, indexes))
                        break
                else:
                    print("procedure not found")
            else:
                nodes.append(Node(selectedfile.filename, "", selectedfile, reverse, reAnalyse, reverseLevels, forward, indexes))

        for node in nodes:
            node.analyse(files)

        for node in nodelist:
            if not node.hasParents:
                parentnodes.append(node)

        for node in parentnodes:
            print("\n")
            print(node)

    if doinput:
        nodes.clear()
        again = input("Another call map? [y:n]: --> ")
        if not (again == "y" or again == "yes"):
            runagain = False
    else:
        runagain = False
