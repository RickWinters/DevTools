import pathlib
import pickle
import time
import regex as re
import json
import os
from tqdm import tqdm
import xml.etree.ElementTree as ET

class Helperfunctions:

    filelist = []
    indexlist = []
    nperfile = 1000

    def __init__(self):
        self.curaversion = "10303"
        self.folder = "C:/dev/cura-117/prj/cura" + self.curaversion
        self.folderending = ""
        self.previousResults = []
        self.printListing = False
        self.indexFilePath = "C:\dev\cura-117\prj\cura" + self.curaversion + "\indexfile.txt"
        self.analysedFilPath = "C:\dev\cura-117\prj\cura" + self.curaversion + "\Analysedfiles\Analysedfile"
        self.indexes = []
        self.files = []

    class Parameter:

        def __init__(self, name, direction, type):
            self.name = name.replace("input", "").strip()
            self.direction = direction.strip()
            self.type = type.strip()

        def __str__(self):
            text = "\t\t" + self.direction
            text += " " + self.name
            text += " " + self.type
            return text

        def writexml(self, parentelement):
            ET.SubElement(parentelement, "Parameter", direction=self.direction, name=self.name, datatype=self.type)

    class Handle:
        def __init__(self, handlename, filename):
            self.handlename = handlename
            self.filename = filename

    class InternallCall:

        def __init__(self, propertyname, methodname, line = ""):
            dotind = methodname.lower().find(".")
            runind = methodname.lower().find("run ")
            slashind = propertyname.lower().rfind("/")
            if dotind > -1:
                methodname = methodname[:dotind]
            if runind > -1:
                methodname = methodname[runind+4:]
            if slashind > -1:
                propertyname = propertyname[slashind+1:]
            self.propertyname = propertyname.strip()
            self.methodname = methodname.strip()
            self.originalline = line

        def __str__(self):
            return self.propertyname + ":" + self.methodname

        def writexml(self, parentelement):
            ET.SubElement(parentelement, "InternallCall", file=self.propertyname, method=self.methodname)

    def getCode(self, object, startline=0, endline=-1, includeCommentary=False):
        lines = []
        object.lines = []
        if not object.filename.startswith("/") and not object.filepath.endswith("/"):
            object.filename = "/" + object.filename
        try:
            file = open(object.filepath + object.filename, "r")
            lines = file.readlines()
            file.close()

            if not endline == -1:
                lines = lines[startline: endline]
            else:
                lines = lines[startline:]

            for line in lines:
                object.fulllines.append(line.lower())
                if not includeCommentary:
                    ind1 = 0
                    ind2 = 0
                    ind1 = line.find("/*")
                    ind2 = line.find("*/")
                    if ind1 > 0 and ind2 > ind1:
                        line = line[:ind1] + line[ind2+2:]
                    else:
                        ind1 = line.find("//")
                        if ind1 > 0:
                            line = line[:ind1]
                object.lines.append(self.cleanupLine(line).lower())

        except:
            object.message = "couldn't open file: " + object.filepath + object.filename
            pass

    def cleanupLine(self, line):
        line = line.strip()
        #line = line.lower()
        line = line.replace("'", "")
        #line = line.replace('"', "")
        line = line.replace("\\", "/")
        line = line.replace("&reference-only=reference-only", "")
        line = line.replace("&access-mode=private", "")
        line = line.replace("&access-mode=protected", "")
        line = line.replace("&ACCESS-MODE=PROTECTED", "")
        line = line.replace("{&*}", "")
        line = line.strip()
        return line

    def prettify(self, element, indent="  "):
        queue = [(0, element)]
        while queue:
            level, element = queue.pop(0)
            children = [(level + 1, child) for child in list(element)]
            if children:
                element.text = "\n" + indent * (level + 1)
            if queue:
                element.tail = "\n" + indent * queue[0][0]
            else:
                element.tail = indent * (level + 1) + "\n"
            queue[0:0] = children

    def rescanFiles(self, folder, printOutput = False):
        files = []

        if printOutput:
            print("LISTING FILES WITH FILTER: " + folder + "/")
        for path in pathlib.Path(folder).rglob("**/*"):
            files.append((str(path).replace("\\", "/")).replace(folder, ""))

        if printOutput:
            print("Indexing")
            i = 1
            filenum = 1
            for file in tqdm(files):
                slashind = file.rfind("/")
                filename = file[slashind+1:]
                dotind = filename.find(".")
                name = filename[:dotind]
                self.indexes.append({"Filename":filename, "Path":file, "Filenum":-1, "Name":name})
        else:
            for file in files:
                slashind = file.rfind("/")
                filename = file[slashind+1:]
                dotind = filename.find(".")
                name = filename[:dotind]
                self.indexes.append({"Filename":filename, "Path":file, "Filenum":-1, "Name":name})

        self.writeIndexFile(printOutput)
        self.getFilesAnalysed()

    def writeIndexFile(self, printOutput = False):
        output_file = open(self.indexFilePath, "w")
        output_file.write("")
        if printOutput:
            print("Writing index file")
            for index in tqdm(self.indexes):
                json.dump(index, output_file)
                output_file.write("\n")
        else:
            for index in self.indexes:
                json.dump(index, output_file)
                output_file.write("\n")
        output_file.close()
        Helperfunctions.indexlist = self.indexes

    def getIndexFile(self):
        if Helperfunctions.indexlist == []:
            if self.indexes == []:
                indexfile = open(self.indexFilePath, 'r')
                lines = indexfile.readlines()
                indexes = []
                for line in lines:
                    indexes.append(eval(line))
                indexfile.close()
                self.indexes = indexes
                Helperfunctions.indexlist = indexes
                return indexes
            else:
                Helperfunctions.indexlist = self.indexes
                return Helperfunctions.indexlist
        else:
            self.indexes = Helperfunctions.indexlist
            return Helperfunctions.indexlist

    def getFilesAnalysed(self):
        filenames = []
        indexes = self.getIndexFile()
        for index in indexes:
            if index["Path"].endswith(".cls") or index["Path"].endswith(".p") or index["Path"].endswith(".w"):
                filenames.append(index["Path"])

        print("Opening files")
        for filename in tqdm(filenames):
            self.files.append(self.openFile(filename))

        diskfiles = self.listAnalysedFiles(trimmainfolder=False)
        for diskfile in diskfiles:
            filehandle = open(diskfile, 'w')
            filehandle.write("")
            filehandle.close()

        print("Analysing all files")
        tqdmloop = tqdm(self.files)
        i = 0
        j = 1
        for file in tqdmloop:
            index = [index for index in self.indexes if index["Filename"] == file.filename][0]
            index["Filenum"] = j

            i+=1
            tqdmloop.set_description(file.filename)
            file.analyse()
            if i == 1000:
                tempfile = open(self.analysedFilPath + str(j) + ".txt", 'wb')
                files = [files for files in self.files if files.analysed == True]
                pickle.dump(files, tempfile)
                tempfile.close()
                for file in files:
                    file.cleanUp()
                Helperfunctions.filelist.clear()
                i = 0
                j += 1

        j += 1
        tempfile = open(self.analysedFilPath + str(j) + ".txt", 'wb')
        files = [files for files in self.files if files.analysed == True]
        pickle.dump(files, tempfile)
        for file in files:
            file.cleanUp()

        self.writeIndexFile(True)


    def openFile(self, filename):
        file = []
        from FileDescriptors.ClassFile import Classfile
        from FileDescriptors.ProcedureFile import Procedurefile

        if filename.endswith(".cls") or filename.endswith(".CLS"):
            file = Classfile(self.folder, filename)
        elif filename.endswith(".p") or filename.endswith(".P"):
            file = Procedurefile(self.folder, filename)
        elif filename.endswith(".w") or filename.endswith(".W"):
            file = Procedurefile(self.folder, filename)

        return file

    def getAnalysedFile(self, filename):
        path = ""
        slashind = filename.rfind("/")
        if slashind > -1:
            path = filename[:slashind]
            filename = filename[slashind+1:]
        dotind = filename.rfind(".")
        if dotind > -1:
            filename = filename[dotind+1:]
        file = []
        failed = False

        file = [file for file in Helperfunctions.filelist if filename.lower() == file.name.lower()]
        if file:
            return file[0]

        self.getIndexFile()
        index = [index for index in self.indexes if filename.lower() == index["Name"].lower()]
        if not index:
            return file
        if path:
            index = [ind for ind in index if path.lower() in ind["Path"].lower()]
        index = index[0]
        self.readAnalysedFiles(index["Filenum"])
        file = [file for file in Helperfunctions.filelist if filename.lower() == file.name.lower()]
        if not file:
            failed = True
        else:
            file = file[0]

        if failed and index:
            file = self.openFile(index["Path"])
            if file:
                found = []
                appendFile(file)
                file.analyse()

        return file

    def readAnalysedFiles(self, filenum):
        """
        Reads the analysed file and returns the analysed file objects. If 'filenum' = 0 than load all without checking
        :param filenum: which pickle dump to load, if 0 than all
        :type filenum: integer
        """
        fileslist = []
        diskfiles = []
        diskfilepaths = self.listAnalysedFiles()
        for path in diskfilepaths:
            ind1 = path.rfind("Analysedfile")
            ind2 = path.find(".txt")
            num = path[ind1 + 12 : ind2]
            diskfiles.append({"Path":path, "Num":num})

        if filenum == 0:
            for diskfile in tqdm(diskfiles):
                try:
                    if diskfile["Num"] == str(filenum) or filenum == 0:
                        filehandle = open(diskfile["Path"], 'rb')
                        fileslist += pickle.load(filehandle)
                        filehandle.close()
                except:
                    pass
        else:
            for diskfile in diskfiles:
                try:
                    if diskfile["Num"] == str(filenum) or filenum == 0:
                        filehandle = open(diskfile["Path"], 'rb')
                        fileslist += pickle.load(filehandle)
                        filehandle.close()
                except:
                    pass

        if filenum == 0:
            self.files = fileslist
        else:
            for file in fileslist:
                appendFile(file)
        return self.files

    def listAnalysedFiles(self, trimmainfolder = True):
        files = []
        for path in os.listdir(self.folder + "\Analysedfiles"):
            files.append(self.folder + "\Analysedfiles\\" + path)
        if trimmainfolder:
            for file in files:
                file.replace(self.folder, "")

        return files

    def ListFiles(self, folder, folderending, filefilter):
        files = []
        filefilter = filefilter.replace('"',"")
        #find first in memory.
        if not folderending.startswith("/"):
            folderending = "/" + folderending
        for file in self.previousResults:
            if filefilter in file:
                files.append(file)
        if not files == []:
            return files

        #first find from saved indexfile
        if self.printListing: print("Scanning index file for " + filefilter)

        slashind = filefilter.rfind("/")
        if slashind > -1:
            folderending = folderending + filefilter[:slashind].strip()
            filefilter = filefilter[slashind+1:].strip()

        indexes = self.getIndexFile()
        for index in indexes:
            if index["Filename"].startswith(filefilter) and index["Path"].startswith(folderending):
                if not index["Path"].startswith("/."):
                    files.append(index["Path"])

        self.AddPreviousResults(files)

        return files

    def AddPreviousResults(self, files):
        for file in files:
            file = file.lower()
            self.previousResults.append(file)

    def RemoveNumbersAtEnd(self, name):
        count = 0
        test = 0
        for c in name[::-1]:
            try:
                test += int(c)
                count += 1
            except:
                break
        if count > 0:
            return name[:-count]
        else:
            return name

def appendFile(newfile):
    found = [file for file in Helperfunctions.filelist if file.name == newfile.name]
    if not found:
        Helperfunctions.filelist.append(newfile)
    else:
        pass

if __name__ == "__main__":
    hf = Helperfunctions()
    files = hf.ListFiles(hf.folder, hf.folderending, "btrostertemplate")
    print(files)