import xml.etree.ElementTree as ET
from FileDescriptors.File import File
from FileDescriptors.shared.Property import Property

try:
    from helperfunctions import Helperfunctions
    hf = Helperfunctions()
    Parameter = hf.Parameter
except:
    pass

class Procedurefile(File):
    class Procedure:

        def __init__(self, parent, name, linenumber, lines, handles):
            self.lines = lines
            self.parent = parent
            spaceind = name.find(" ")
            if spaceind > -1:
                name = name[:spaceind]
            self.name = name.strip()
            self.linenumber = linenumber
            self.commentary = ""
            self.parameters = []
            self.internalcalls = []
            self.analysed = False
            self.handles = handles

        def __str__(self):
            text = "\n\tProcedure " + self.name
            if self.commentary:
                text += self.commentary
            return text + "\n"

        def analyse(self):
            if not self.analysed:
                self.analysed = True
                self.getcommentary()
                self.getInternalCall()

        def getcommentary(self):
            hascommentary = False
            line = self.lines[self.linenumber + 1]
            if line.startswith("/*---"):
                hascommentary = True

            if hascommentary:
                incommentary = False
                for line in self.lines[self.linenumber + 1:-1]:
                    if line.startswith("/*---"):
                        incommentary = True
                        continue
                    if line.endswith("--*/"):
                        incommentary = False
                        break
                    if incommentary:
                        self.commentary += "\n\t\t" + line

        def getInternalCall(self):
            start = self.linenumber
            ind = start
            end = start
            incomment = False
            for line in self.lines[start + 1:]:
                if line.endswith("end procedure."):
                    end = ind
                    break
                if line.startswith("procedure ") and ind > start and not incomment:
                    end = ind - 2
                    break
                if line.startswith("/*-"):
                    incomment = True
                if line.endswith("-*/"):
                    incomment = False
                else:
                    ind += 1
            fragment = self.lines[start:end]

            extractInternalCalls(self, self.lines, start, end, self.parent.filename)

        def writexml(self, parentelement):
            element = ET.SubElement(parentelement, "Procedure", name=self.name)
            ET.SubElement(element, "commentary").text = self.commentary.replace("\n", "\t")
            for parameter in self.parameters:
                ET.SubElement(element, "parameter").text = str(parameter)

    def __init__(self, filepath, filename):
        super().__init__(filepath, filename)
        self.commentary = ""
        self.procedures = []
        self.properties = []
        self.type = "ProcedureFile"
        self.tocompilemessage = "@tocompile"
        self.internalcalls = []
        self.parameters = []

    def __str__(self):
        text = super().__str__()
        if self.commentary:
            text += "\n" + self.commentary
        for procedure in self.procedures:
            text += str(procedure)
        return text + "\n\n"

    def cleanUp(self):
        super().cleanUp()
        self.procedures = []
        self.internalcalls = []
        self.parameters = []

    def analyse(self):
        if not self.analysed:
            super().analyse()
            self.getParameters()
            self.getclasscommentary()
            self.getProcedures()
            Property.getProperties(self)
            for procedure in self.procedures:
                procedure.analyse()
            self.getInternalCalls()

    def getParameters(self):
        for line in self.lines:
            if line.startswith("define") and "parameter" in line and not "table" in line:
                defineind = line.find("define")
                parameterind = line.find("parameter")
                asind = line.find(" as ")
                noundoind = line.find(" no-undo")
                direction = line[defineind + 6:parameterind].strip()
                name = line[parameterind + 9:asind].strip()
                type = line[asind + 4:noundoind].strip()
                self.parameters.append(Parameter(name, direction, type))
            if line.startswith("procedure"):
                break

    def getclasscommentary(self):
        inClassCommentary = False
        inModificationblok = False
        modifcounter = 0
        for line in self.lines:
            if line.startswith("/*--") or line.startswith("/****"):
                inClassCommentary = True
                continue
            if line.endswith("--*/") or line.endswith("***/") or line.endswith("===*/"):
                inClassCommentary = False
                break
            if inClassCommentary and (line.startswith("MODIFICATIE BLOK") or line.startswith("/* MODIFICATIE BLOK")):
                inModificationblok = True
                continue
            if inClassCommentary and line.endswith("==="):
                modifcounter += 1
                continue
            if modifcounter == 2:
                inModificationblok = False
            if inClassCommentary and not inModificationblok:
                self.commentary += "\t" + line + "\n"

    def getProcedures(self):
        for i, line in enumerate(self.lines):
            if line.lower().startswith("procedure"):
                name = line[10:-1]
                self.procedures.append(self.Procedure(self, name, i, self.lines, self.handles))

    def getInternalCalls(self):
        start = 1
        end = start
        ind = start
        for line in self.lines:
            if line.startswith("procedure "):
                end = ind
                break
            else:
                ind += 1
        else: #if no line.startswith("procedure") is found
            end = ind

        extractInternalCalls(self, self.lines, start, end, self.filename)

    def writexml(self, parentelement):
        element = super().writexml(parentelement)
        ET.SubElement(element, "commentary").text = self.commentary.replace("\n", "\t")
        for procedure in self.procedures:
            procedure.writexml(element)


def extractInternalCalls(object, lines, start, end, filename):
    lines = lines[start:end]
    for line in lines:
        if line.lower().find("run") > -1:
            dotpind = line.lower().find(".p")
            inind = line.lower().find(" in ")
            bracketind = line.lower().find("(")
            runind = line.lower().find("run ")
            if inind > 0:
                if bracketind == -1:
                    handlename = line[inind + 4:]
                else:
                    handlename = line[inind + 4:bracketind]
                for handle in object.handles:
                    if handle.handlename == handlename:
                        propertyname = handle.filename
                        methodname = line[runind + 4:inind]
                        object.internalcalls.append(hf.InternallCall(propertyname, methodname, line))
                continue
            if dotpind > 0:
                propertyname = line[4:dotpind + 2]
                object.internalcalls.append(hf.InternallCall(propertyname, "", line))
                continue
            else:
                if bracketind > 0:
                    methodname = line[runind + 4:bracketind]
                else:
                    methodname = line[runind + 4:]
                if methodname.endswith("."):
                    methodname = methodname[:-1]
                object.internalcalls.append(hf.InternallCall(filename, methodname, line))
                continue
