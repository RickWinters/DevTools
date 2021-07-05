import xml.etree.ElementTree as ET

try:
    from helperfunctions import Helperfunctions
    hf = Helperfunctions()
except:
    hf = []
    pass

class File:

    def __init__(self, filepath, filename):
        slashind = filename.rfind("/")
        filepath += filename[:slashind+1]
        filename = filename[slashind+1:]
        self.filepath = filepath.strip()
        self.filename = filename.strip()
        self.lines = []
        self.fulllines = []
        self.includes = []
        self.message = ""
        self.type = "File"
        self.tocompilemessage = "@mastertocompile"
        self.analysed = False
        self.opened = False
        self.handles = []
        self.importedInclude = False
        ind = self.filename.rfind("/")
        dotind = self.filename.find(".")
        if dotind > 0:
            self.name = self.filename[ind+1:dotind]
        else:
            self.name = self.filename[ind+1:]
        if not self.opened:
            hf.getCode(self)
            self.opened = True

    def __str__(self):
        text = self.filepath + self.filename + "\n"
        if self.message:
            text += "\t" + self.message + "\n"
        for include in self.includes:
            text += str(include)
        return text

    def cleanUp(self):
        self.lines = []
        self.includes = []
        self.handles = []
        self.analysed = False
        self.opened = False
        self.importedInclude = False

    def analyse(self):
        if not self.opened:
            hf.getCode(self)
            self.opened = True
        if not self.analysed:
            self.analysed = True
            self.getIncludes()
            self.checkToCompile()
            self.getHandles()
            self.parseIncludes()

    def getIncludes(self):
        from FileDescriptors.Include import Include

        for i, line in enumerate(self.lines):
            if line.startswith("{") and (line.endswith("}") or line.endswith(".i")):
                if not line.lower() == "{&reference-only}":
                    dotiInd = line.find(".i")
                    slashind = line.rfind("/")
                    filepath = hf.folder + "/" + line[1:slashind] + "/"
                    filename = line[slashind+1:dotiInd+2]
                    linestart = i
                    if line.endswith("}"):
                        lineend = i
                    else:
                        while True:
                            if len(self.lines) == i + 1 or self.lines[i+1].endswith("}"):
                                lineend = i
                                break
                            i += 1
                    self.includes.append(Include(filepath, filename, self.tocompilemessage, self, linestart, lineend+1, self.lines))

    def checkToCompile(self, filter = ""):
        for include in self.includes:
            if "ds" in include.filename:
                found = False
                filename = (include.filepath + include.filename).replace(hf.folder, "").replace(".i", "")[1:]
                checkline = "@tocompile(module=" + filename + ")."
                for line in self.lines:
                    if line == checkline:
                        include.found = True
                        break
            else:
                include.found = True

    def getHandles(self):
        for line in self.lines:
            if line.find("persistent set") > 0:
                dotpind = line.lower().find(".p")
                perssetind = line.lower().find("persistent set")
                runind = line.lower().find("run ")
                if dotpind > 0 and perssetind > 0:
                    handlename = line[perssetind + 15:]
                    filename = line[runind + 4 : dotpind + 2]
                    self.handles.append(hf.Handle(handlename, filename))

    def parseIncludes(self):
        offset = 0
        for include in self.includes:
            include.open()
            include.getParams()
            include.compareParentParams()
            include.parseInclude()
            include.analyse()
        for include in self.includes:
            self.lines, offset, self.importedInclude = include.replaceInclude(self.lines, offset)

    def writexml(self, parentelement):
        element = ET.SubElement(parentelement, self.type, name=self.filename)
        if self.message:
            ET.SubElement(element, "Missing").text = self.message.replace("MISSING ", "")
        for include in self.includes:
            include.writexml(element)
        return element

    def checkCorrectFile(self, inputfilename):
        slashind = inputfilename.rfind("/")
        pathending = inputfilename[:slashind + 1]
        dotind = inputfilename.find(".")
        if dotind > 0:
            name = inputfilename[slashind + 1 : dotind]
        else:
            name = inputfilename[slashind + 1 :]
        if (self.filepath.lower().endswith(pathending.lower())
                and self.name.lower() == name.lower()):
            return True
        else:
            return False
