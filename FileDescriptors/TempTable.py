from FileDescriptors.File import File
from helperfunctions import Helperfunctions

hf = Helperfunctions()

class TempTable(File):
    class Field:
        def __init__(self, name, type, commentary):
            self.name = name
            self.type = type
            self.commentary = commentary

    def __init__(self, filepath, filename, dataset = None, indexes = None):
        super().__init__(filepath, filename)
        self.datasets = []
        self.type = "TempTable"
        self.fields = []
        self.checkedToCompile = False
        if indexes:
            self.indexes = indexes
        else:
            self.indexes = []
        self.indexes = indexes
        if dataset:
            self.datasets.append(dataset)

    def __str__(self):
        text = "\n\t"+self.filepath + self.filename
        if self.message:
            text += "\n\t\t" + self.message
        return text

    def analyse(self, dataset=None):
        if dataset:
            self.datasets.append(dataset)
        if not self.opened:
            hf.getCode(self)
            self.opened = True
        self.checkMasterToCompileOfDatase()
        self.getFields()
        self.getName()

    def checkMasterToCompileOfDatase(self):
        if not self.checkedToCompile:
            self.checkedToCompile = True
            for dataset in self.datasets:
                filename = (dataset.filepath + dataset.filename).replace(hf.folder, "").replace(".i", "")[1:]
                checkline1 = "@mastertocompile(module=" + filename + ")."
                found = False
                for line in self.lines:
                    if line == checkline1:
                        found = True
                        break

                if not found:
                    self.message += "MISSING " + checkline1

    def getDatasetParents(self):
        from FileDescriptors.DataSet import DataSet

        if len(self.indexes) == 0:
            self.indexes = hf.getIndexFile()

        for index in self.indexes:
            if index["Filename"].lower().startswith("ds") and index["Filename"].lower().endswith(".i"):
                for dataset in self.datasets:
                    if dataset.filename == index["Filename"]:
                        continue
                dataset = DataSet(hf.folder, index["Path"])
                hf.getCode(dataset)
                dataset.getIncludes()
                for include in dataset.includes:
                    if include.filename == self.filename:
                        self.datasets.append(dataset)

    def getFields(self):
        for i, line in enumerate(self.lines):
            line = line.lower()
            fullline = self.fulllines[i].lower()
            if line.startswith("field"):
                ind = line.find("field")
                ind2 = line.find(" ", ind+6)
                name = line[ind+6:ind2]
                ind = line.find("as")
                ind2 = line.find(" ", ind+3)
                if ind2 == -1:
                    type = line[ind+3:]
                else:
                    type = line[ind+3:ind2]

                ind = fullline.find("/*")
                ind2 = fullline.find("*/")
                ind3 = fullline.find("//")
                if ind > -1 and ind2 > -1:
                    commentary = fullline[ind+2:ind2].strip()
                elif ind3 > -1 and ind == -1:
                    commentary = fullline[ind3+2:].strip()
                else:
                    commentary = ""
                self.fields.append(self.Field(name, type, commentary))

    def getName(self):
        name = ""
        for line in self.lines:
            lowerline = line.lower()
            if line.startswith("define") or line.startswith("DEFINE"):
                ttind = lowerline.find("temp-table")
                extind = lowerline.find("{&ext}")
                undoind = lowerline.find("no-undo")
                if extind > -1:
                    name = line[ttind+11:extind]
                else:
                    name = line[ttind+11:undoind-1]
                break
        self.name = hf.RemoveNumbersAtEnd(name)
