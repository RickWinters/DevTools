from FileDescriptors.TempTable import TempTable
from FileDescriptors.File import File
from helperfunctions import Helperfunctions

class DataSet(File):

    def __init__(self, filepath, filename, indexes = None):
        super().__init__(filepath, filename)
        for i, line in enumerate(self.lines):
            if line == '{&reference-only}':
                self.lines.pop(i)
        self.temptables = []  # array of temptable ebojects
        self.type = "DataSet"
        self.name = ""
        self.indexes = indexes

    def __str__(self):
        text = self.filepath + self.filename
        if self.message:
            text += "\n\t" + self.message
        for temptable in self.temptables:
            text += str(temptable)
        return text + "\n\n"

    def analyse(self):
        super().analyse()
        self.getTempTables()
        self.getName()

    def getTempTables(self):
        if not self.indexes:
            hf = Helperfunctions()
            self.indexes = hf.getIndexFile()
        for include in self.includes:
            for index in self.indexes:
                if include.filename.lower() in index["Filename"].lower():
                    temptable = TempTable(include.filepath, include.filename)
                    self.temptables.append(temptable)
                    temptable.analyse(self)
                    break

    def checkToCompile(self): #Override checkToCompile Neccesary for correct checkline on Dataset. Called from File.py:Analyse()
        from helperfunctions import Helperfunctions

        hf = Helperfunctions()
        found = False
        filename = (self.filepath + self.filename).replace(hf.folder, "").replace(".i", "")[1:]
        checkline1 = "@mastertocompile(module=" + filename + ")."
        for line in self.lines:
            if line == checkline1:
                found = True
                break

        if not found:
            self.message = "MISSING " + checkline1

    def writexml(self, parentelement):
        element = super().writexml(parentelement)
        for temptable in self.temptables:
            temptable.writexml(element)

    def getName(self):
        hf = Helperfunctions()
        for line in self.lines:
            if line.startswith("define"):
                ind = line.find("dataset ")
                ind2 = line.find("{&ext}")
                if ind2 == -1:
                    self.name = line[ind+8:]
                else:
                    self.name = line[ind+8:ind2]
                self.name = hf.RemoveNumbersAtEnd(self.name)