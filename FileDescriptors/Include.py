import xml.etree.ElementTree as ET
from helperfunctions import Helperfunctions
from FileDescriptors.File import File

hf = Helperfunctions()

class Include(File):
    class Param:
        def __init__(self, paramName, paramValue):
            self.paramName = paramName.strip()
            self.paramValue = paramValue.strip()

    def __init__(self, filepath, filename, tocompilemessage, includedIn, lineStart, lineEnd, lines):
        super().__init__(filepath, filename)
        self.tocompilemessage = tocompilemessage
        self.found = False
        self.params = []
        self.includedIn = includedIn
        self.lineStart = lineStart
        self.lineEnd = lineEnd
        self.type = "Include"
        self.parsedLines = []
        self.recursive = False
        self.parentLines = lines[self.lineStart: self.lineEnd]
        pass

    def __str__(self):
        text = "\t" + self.filename + "\n" + (" RECURSIVE " * self.recursive)
        if not self.found:
            text += "\t\tMISSING " + self.tocompilemessage + "(module='" + self.filename.replace(".i", "") + "').\n"
        return text

    def cleanUp(self):
        super().cleanUp()
        self.params = []
        self.parsedLines = []

    def open(self):
        if not self.opened:
            hf.getCode(self)
            self.opened = True

    def analyse(self):
        if not self.recursive and not self.analysed:
            super().analyse()
        else:
            pass

    def writexml(self, parentelement):
        element = ET.SubElement(parentelement, "Include", name=self.filename)
        if not self.found:
            filename = (self.filepath + self.filename).replace(hf.folder, "").replace(".i", "")[1:]
            ET.SubElement(element, "Missing").text = self.tocompilemessage + "(module='" + filename + "')."

    def getParams(self):

        paramName = ""
        paramValue = ""
        inInclude = False
        multiLine = False
        i = 0
        while i < len(self.parentLines):
            line = self.parentLines[i].strip()
            #Single line include
            if line.lower().startswith("{") and line.lower().endswith("}"):
                while True:
                    ampind = line.lower().find("&")
                    isind = line.lower().find("=")
                    amp2ind = line.lower().find("&", isind)
                    bracket1ind = line.lower().find("{",ampind)
                    bracket2ind = line.lower().find("}",bracket1ind)        #to handle the stupid case of " &proc = "tempUpdate" &Table = {&kind}".. 2 params where once value is another param -_-
                    if ampind > -1:
                        paramName = line[ampind+1:isind].strip()
                        if amp2ind > -1 and isind < amp2ind:
                            paramValue = line[isind+1:amp2ind].strip()
                        else:
                            paramValue = line[isind+1:-1].strip()
                        self.params.append(self.Param(paramName, paramValue))
                        if amp2ind > -1 and isind < amp2ind:
                            line = line[amp2ind:]
                        else:
                            break
                    else:
                        break
                i += 1
                continue

            #multi line include
            if line.lower().startswith("{") and not line.lower().endswith("}"):
                inInclude = True
                i += 1
                continue
            if multiLine:
                ind = line.find("~")
                if ind > -1:
                    paramValue += line[ind:] + "\n"
                else:
                    paramValue += line + "\n"
                if i+1 == len(self.parentLines) or line.endswith('"'):
                    multiLine = False
                    self.params.append(self.Param(paramName, paramValue))
                i += 1
                continue
            if inInclude:
                ampind = line.lower().find("&")
                isind = line.lower().find("=")
                paramName = line[ampind+1:isind].strip()
                paramValue = line[isind+1:].strip()
                if paramValue.endswith('~'):
                    multiLine = True
                    paramValue = ""
                    i += 1
                    continue
                if paramValue.startswith('"') and not paramValue.endswith('"'):
                    while i < len(self.parentLines) - 1:
                        i += 1
                        line = self.parentLines[i].strip()
                        paramValue = paramValue + line
                        if line.endswith('"'):
                            break
                self.params.append(self.Param(paramName, paramValue))
                if line.lower().endswith("}"):
                    inInclude = False
            i += 1

    def parseInclude(self):
        if not self.recursive:
            lines = self.lines
            while True:
                oldlines = lines
                lines = self.parseParamIsValue(lines)
                #lines = self.parseSinglelineIfdefined(lines)
                lines = self.parseIfDefined(lines)
                lines = self.parseParamDefines(lines)
                lines = self.parseParams(lines)
                self.parsedLines = lines
                self.lines = lines

                if not (len(lines) == len(oldlines)):
                    continue

                i = 1
                stop = True
                while i < len(lines):
                    line = lines[i]
                    oldline = oldlines[i]
                    if not (line == oldline):
                        stop = False
                        break
                    i += 1
                if stop:
                    break

    def parseParamIsValue(self, oldlines):
        lines = []
        doAppend = True
        iflevel = 0
        i = 0
        while i < len(oldlines):
            line = oldlines[i]
            line = self.parseSinglelineIfdefined([line])[0]
            if line.lower().startswith("&if"):
                iflevel += 1
            elif line.lower().startswith("&endif"):
                iflevel -= 1
            if line.lower().startswith("&endif"):
                if iflevel == 0:
                    doAppend = True
                i+=1
                continue
            if doAppend:
                if line.lower().startswith("&if") or line.lower().startswith("&elseif"):
                    doAppend = False
                    i += 1
                    continue
                lines.append(line)
            if (line.lower().startswith("&if") or line.lower().startswith("&elseif")) and iflevel == 1:
                ind1 = line.lower().find("{&")
                ind2 = line.lower().find("}")
                isind = line.lower().find("=")
                thenind = line.lower().find("&then")
                paramName = line[ind1+2:ind2].strip()
                if thenind > -1:
                    paramValue = line[isind+1:thenind].strip()
                else: #then on next line
                    paramValue = line[isind+1:].strip()
                    i += 1
                for param in self.params:
                    if param.paramName.lower() == paramName.lower() and param.paramValue.lower() == paramValue.lower():
                        appendFromParam = True
                        doAppend = True
            i += 1
        return lines

    def parseIfDefined(self, oldlines):
        lines = []
        i = 0

        while i < len(oldlines):
            line = oldlines[i]
            if line.lower().startswith("&if defined("):
                ind1 = line.lower().find("(")
                ind2 = line.lower().find(")")
                param = line[ind1+1:ind2]
                startline = i
                while True:
                    i += 1
                    if self.lines[i].lower().startswith("&endif"):
                        endline = i
                        break
                if line.lower().find("= 0 &then") > -1:
                    lines += self.parseParamNotDefined(startline, endline, param)

                if line.lower().find("<> 0 &then") > -1:
                    lines += self.parseParamDefined(startline, endline, param)
                i += 1
            else:
                lines.append(line)
                i += 1
        return lines

    def parseSinglelineIfdefined(self, oldlines):
        lines = []

        for line in oldlines:
            ifInd = line.lower().find("&if defined(")
            isDefinedInd = line.lower().find(") > 0", ifInd)
            isNotDefinedInd = line.lower().find(") = 0", ifInd)
            thenInd = line.lower().find("&then")
            elseInd = line.lower().find("&else", thenInd)
            endIfInd = line.lower().find("&endif", thenInd)
            ifIsTrue = False
            if ifInd > -1 and thenInd > -1 and endIfInd > -1:
                if elseInd == -1:
                    elseInd = endIfInd
                if isDefinedInd > 0:
                    param = line[ifInd+12:isDefinedInd]
                    ifIsTrue = self.checkIsDefined(param)
                if isNotDefinedInd > 0:
                    param = line[ifInd+12:isNotDefinedInd]
                    ifIsTrue = not self.checkIsDefined(param)
                if ifIsTrue:
                    replacement = line[thenInd+5:elseInd]
                else:
                    replacement = line[elseInd+5:endIfInd]
                line = line[:ifInd] + replacement + line[endIfInd+6:]
            lines.append(line)
        return lines

    def parseParamDefines(self, oldlines):
        lines = []
        for line in oldlines:
            if line.lower().startswith("&scoped-define"):
                line = line[14:]
                ind = line.find(" ")
                paramName = line[:ind]
                paramValue = line[ind+1:]
                self.params.append(self.Param(paramName, paramValue))
            else:
                lines.append(line)
        return lines

    def parseParams(self, oldlines):
        lines = []

        for line in oldlines:
            ind1 = line.lower().find("{")
            ind2 = line.lower().find("}")
            if ind1 > -1 and ind2 > -1:
                paramName = line[ind1+2:ind2]
                for param in self.params:
                    if param.paramName == paramName:
                        part = line[ind1:ind2+1]
                        line = line.replace(part, param.paramValue).replace('"',"")
                        break
            lines.append(line)
        return lines

    def parseParamNotDefined(self, startline, endline, param):
        lines = []
        isDefined = self.checkIsDefined(param)
        if not isDefined:
            for line in self.lines[startline+1:endline]:
                lines.append(line)
        return lines

    def parseParamDefined(self, startline, endline, param):
        lines = []
        isDefined = self.checkIsDefined(param)
        if isDefined:
            for line in self.lines[startline+1:endline]:
                lines.append(line)
        return lines

    def checkIsDefined(self, paramName):
        isDefined = False
        for param in self.params:
            if param.paramName == paramName:
                isDefined = True
                break

        return isDefined

    def replaceInclude(self, oldlines, offset):
        if not self.recursive and len(self.lines) > 0:
            begin = oldlines[:self.lineStart+offset-1]
            end = oldlines[self.lineEnd+offset-1:]
            lines = begin + self.lines + end
            offset += len(self.lines)-1
            if len(self.parsedLines) > 0:
                return lines, offset, True
            else:
                return lines, offset, False
        else:
            return oldlines, offset, False

    def compareParentParams(self):
        doStop = False
        parent = self.includedIn

        while not doStop:
            if isinstance(parent, Include):
                if not (len(self.params) == len(parent.params)):
                    parent = parent.includedIn
                    continue
                i = 0
                while i < len(self.params):
                    if (self.params[i].paramName  == parent.params[i].paramName and
                        self.params[i].paramValue == parent.params[i].paramValue):
                        self.recursive = True
                        doStop = True
                        break
                    i += 1
                parent = parent.includedIn
            else:
                break


if __name__ == "__main__":
    filename = "pboverwerk"
    files = hf.readAnalysedFiles()
    for file in files:
        if filename.lower() in file.filename.lower():
            file.cleanUp()
            file.analyse()
            for line in file.lines:
                print(line)
            print("*********** END OF SOURCE CODE, START OF FILE PRINT ******************")
            print(file)
            break
