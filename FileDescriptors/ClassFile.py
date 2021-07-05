import xml.etree.ElementTree as ET
from FileDescriptors.File import File
from FileDescriptors.shared.Property import Property
from FileDescriptors.ProcedureFile import Procedurefile

try:
    from helperfunctions import Helperfunctions
    hf = Helperfunctions()
    Parameter = hf.Parameter
except:
    hf = []
    pass

class Classfile(File):
    class Commentary:

        def __init__(self, file, purpose, syntax, description, author, created, notes):
            self.file = file
            self.purpose = purpose
            self.syntax = syntax
            self.description = description
            self.author = author
            self.created = created
            self.notes = notes

        def __str__(self):
            text = ""
            if self.file:
                text += "\t" + self.file + "\n"
            if self.purpose:
                text += "\t" + self.purpose + "\n"
            if self.syntax:
                text += "\t" + self.syntax + "\n"
            if self.description:
                text += "\t" + self.description + "\n"
            if self.author:
                text += "\t" + self.author + "\n"
            if self.created:
                text += "\t" + self.created + "\n"
            if self.notes:
                text += "\t" + self.notes + "\n"
            return text

        def writexml(self, parentelement):
            element = ET.SubElement(parentelement, "Commentary")
            if self.file:
                ET.SubElement(element, "file").text = self.file
            if self.purpose:
                ET.SubElement(element, "Purpose").text = self.purpose
            if self.syntax:
                ET.SubElement(element, "Syntax").text = self.syntax
            if self.description:
                ET.SubElement(element, "Description").text = self.description
            if self.author:
                ET.SubElement(element, "Author").text = self.author
            if self.created:
                ET.SubElement(element, "Created").text = self.created
            if self.notes:
                ET.SubElement(element, "notes").text = self.notes

    class Method:

        class Commentary:

            def __init__(self, purpose, notes, author, date, params):
                self.purpose = purpose.strip()
                self.notes = notes.strip()
                self.author = author.strip()
                self.date = date.strip()
                self.params = params

            def __str__(self):
                text = ""
                if self.purpose:
                    text += "\t\t" + self.purpose + "\n"
                if self.notes:
                    text += "\t\t" + self.notes + "\n"
                if self.author:
                    text += "\t\t" + self.author + "\n"
                if self.date:
                    text += "\t\t" + self.date + "\n"
                for param in self.params:
                    text += "\t\t" + param + "\n"
                return text

            def writexml(self, parentelement):
                element = ET.SubElement(parentelement, "Commentary")
                ET.SubElement(element, "Purpose").text = self.purpose
                ET.SubElement(element, "Notes").text = self.notes
                ET.SubElement(element, "Author").text = self.author
                for param in self.params:
                    ET.SubElement(element, "Param").text = param

        def __init__(self, name, scope, static, returns, linenumber, parent, lines, handles):
            self.parent = parent
            self.name = name.strip()
            self.scope = scope.strip()
            self.static = static.strip()
            self.returns = returns.strip()
            self.linenumber = linenumber
            self.commentary = ""
            self.parameters = []
            self.internalcalls = []
            self.variableUsing = []
            self.lines = lines
            self.handles = handles

            hf = Helperfunctions()

        def __str__(self):
            text = "\tMethod " + self.scope + " " + self.returns + " " + self.name + "\n"
            for parameter in self.parameters:
                text += str(parameter) + "\n"
            if not self.commentary == "":
                text += str(self.commentary) + "\n"
            if not self.internalcalls == []:
                text += "\t\tInternall calls:" + "\n"
                for internalcall in self.internalcalls:
                    text += "\t\t\t" + str(internalcall) + "\n"

            return text

        def analyse(self):
            self.getCommentary()
            self.getParameters()
            self.getVariableUsing()
            self.getInternalCalls()

        def getCommentary(self):
            purpose = ""
            notes = ""
            author = ""
            date = ""
            params = []
            flag = 1

            end = self.linenumber
            start = end
            line = self.lines[start - 1]
            if not line.endswith("--*/"):
                return  # skip to the next method is there is no commentary on the methods

            while True:  # find the start of the method commentary
                if line.startswith("/*---"):
                    break
                else:
                    start -= 1
                    line = self.lines[start]

            for line in self.lines[start + 1:end - 1]:
                if line.lower().startswith("notes"):
                    flag = 2
                elif line.lower().startswith("author"):
                    flag = 3
                elif line.lower().startswith("date"):
                    flag = 4
                elif line.lower().startswith("@param"):
                    flag = 5

                if flag == 1:
                    purpose += line
                elif flag == 2:
                    notes += line
                elif flag == 3:
                    author += line
                elif flag == 4:
                    date += line
                elif flag == 5:
                    params.append(line)

            self.commentary = self.Commentary(purpose, notes, author, date, params)

        def getParameters(self):
            start = self.linenumber
            end = start
            endmax = len(self.parent.lines)
            while True:
                line = self.lines[end]
                ind = line.find("):")
                if ind == -1:
                    end += 1
                    if end == endmax:
                        break
                else:
                    break

            for i, line in enumerate(self.lines[start:end+1]):  # for each line in the method definition,
                endchar = 0
                startchar = 0
                while True:  # we don't know how many parameter definitions are in here
                    if i == 0 and endchar == 0:
                        startchar = line.find("(", endchar) + 1
                    else:
                        startchar = endchar
                    endchar = line.find(",", startchar + 1)
                    if endchar == -1:
                        endchar = line.find("):", startchar + 1)
                    if endchar == -1:  # if no parameter description or method end on the same line, go to next line
                        break

                    text = line[startchar:endchar]
                    direction = "INPUT"
                    typestring = ""
                    namestart = 0
                    if not text.find("output") == -1:
                        direction = "OUTPUT"
                        namestart = text.find("output") + len("output")
                    elif not text.find("input-ouput") == -1:
                        direction = "INPUT-OUTPUT"

                    if not text.find("dataset") == -1:
                        typestring = "dataset"
                    elif not text.find("dataset-handle") == -1:
                        typestring = "dataset-hadle"

                    aschar = 0
                    if typestring == "":  # normal case
                        aschar = text.find("as ") # add a leading space to prevent 'as' to be found in 'wbasKy'
                        typestring = text[aschar + 3:]
                    else: # dataset or dataset-handle
                        aschar = text.find(typestring)

                    name = text[namestart:aschar].replace(",","").strip()
                    normalvartypes = ["date", "integer", "character", "int64", "datetime", "datetime-tz", "logical",
                                      "decimal", "longchar", "rowid"]
                    if not typestring in normalvartypes:
                        using = [using for using in self.parent.using if using.endswith(typestring)]
                        if using:
                            using = using[0]
                            self.variableUsing.append({"Varname":name, "Using":using})
                    self.parameters.append(Parameter(name, direction, typestring))

        def getVariableUsing(self):
            start = self.linenumber + 1
            ind = start
            end = start
            while True:
                if ind > len(self.lines) - 1 or self.lines[ind].endswith("end method."):
                    end = ind
                    break
                else:
                    ind += 1

            for line in self.lines[start:end]:
                if line.startswith("define variable"):
                    asind = line.find (" as ")
                    noundoind = line.find(" no-undo")
                    normalvartypes = ["date", "integer", "character", "int64", "datetime", "datetime-tz", "logical",
                                      "decimal", "longchar", "rowid"]
                    type = line[asind + 4:noundoind]
                    if type in normalvartypes:
                        continue
                    using = [using for using in self.parent.using if using.endswith(type)]
                    if not using:
                        continue
                    using = using[0]
                    varname = line[16:asind]
                    self.variableUsing.append({"Varname":varname, "Using":using})

        def getInternalCalls(self):
            start = self.linenumber + 1
            ind = start
            end = start
            while True:
                if (ind > len(self.lines) -1
                        or self.lines[ind].endswith("end method."))\
                        or self.lines[ind].startswith("method"):
                    end = ind
                    break
                else:
                    ind += 1

            #property call
            for line in self.lines[start:end]:
                if line.find("run") > -1:
                    dotpind = line.find(".p")
                    inind = line.find(" in ")
                    bracketind = line.find("(")
                    runind = line.find("run ")
                    if inind > 0:
                        handlename = line[inind + 4:bracketind]
                        for handle in self.handles:
                            if handle.handlename == handlename:
                                propertyname = handle.filename
                                methodname = line[runind + 4:inind]
                                self.internalcalls.append(hf.InternallCall(propertyname, methodname))
                        continue
                    if dotpind > 0:
                        propertyname = line[4:dotpind + 2]
                        self.internalcalls.append(hf.InternallCall(propertyname, ""))
                        continue
                    else:
                        if bracketind > 0:
                            methodname = line[runind + 4:bracketind]
                        else:
                            methodname = line[runind + 4:]
                        self.internalcalls.append(hf.InternallCall(self.parent.filename, methodname))
                        continue

                # case of method call in property
                bracketind = line.find("(")
                colonind = line.find(":")
                isind = line.find("=")
                if 1 < colonind < bracketind:  # property and methodcall found:
                    if isind > -1:
                        propertyname = line[isind+2:colonind]
                    else:
                        propertyname = line[:colonind]
                    methodname = line[colonind + 1:bracketind]
                    #self referring
                    if propertyname == "this-object":
                        self.internalcalls.append((hf.InternallCall(self.parent.name, methodname)))
                        continue
                    #variable that has a type in using
                    using = [using["Using"] for using in self.variableUsing if using["Varname"] == propertyname]
                    if using:
                        self.internalcalls.append(hf.InternallCall(using[0], methodname))
                        continue
                    #class variable pointing to another class
                    using = [using["Using"] for using in self.parent.variableUsing if using["Varname"] == propertyname]
                    if using:
                        self.internalcalls.append(hf.InternallCall(using[0], methodname))
                        continue
                    #defined property
                    referral = [property.referral for property in self.parent.properties if property.name == propertyname]
                    if referral:
                        self.internalcalls.append(hf.InternallCall(referral[0], methodname))
                        continue
                    #general using
                    using = [using for using in self.parent.using if using.endswith(propertyname)]
                    if using:
                        self.internalcalls.append(hf.InternallCall(using[0], methodname))
                        continue
                    else:
                        file = hf.getAnalysedFile(propertyname)
                        if file:
                            self.parent.properties.append(Property(propertyname, file.filename))
                            self.internalcalls.append(hf.InternallCall(propertyname, methodname))

                    continue

                if isind > -1 and bracketind > -1:
                    methodname = line[isind+2:bracketind]
                    for method in self.parent.methods:
                        if method.name == methodname:
                            self.internalcalls.append(hf.InternallCall(self.parent.filename, methodname))
                            break
                    continue

                #other method call
                if colonind == -1 and bracketind > 1 and not line.startswith("if"):
                    if isind > -1:
                        methodname = line[isind+2:bracketind]
                    else:
                        methodname = line[:bracketind]
                    for method in self.parent.methods:
                        if method.name == methodname:
                            self.internalcalls.append(hf.InternallCall(self.parent.filename, methodname))
                            break
                    else:
                        if not self.parent.inherit == "":
                            self.parent.inherit.analyse()
                            for method in self.parent.inherit.methods:
                                if method.name == methodname:
                                    self.internalcalls.append(hf.InternallCall(self.parent.inherit.filename, methodname))
                                    break

        def writexml(self, parentelement):
            element = ET.SubElement(parentelement, "Method", name=self.name)
            ET.SubElement(element, "scope").text = self.scope
            if self.static:
                ET.SubElement(element, "static").text = str(self.static)
            ET.SubElement(element, "returns").text = self.returns
            if str(self.commentary):
                self.commentary.writexml(element)
            for param in self.parameters:
                param.writexml(element)
            for call in self.internalcalls:
                call.writexml(element)

    def __init__(self, filepath, filename):
        super().__init__(filepath, filename)
        self.commentary = ""
        self.methods = []
        self.properties = []
        self.variableUsing = []
        self.type = "ClassFile"
        self.tocompilemessage = "@tocompile"
        self.using = []
        self.inherit = ""

    def __str__(self):
        text = super().__str__()
        if self.commentary:
            text += str(self.commentary)
        for method in self.methods:
            text += str(method) + "\n"

        text += "\n"
        return text

    def cleanUp(self):
        super().cleanUp()
        self.methods = []
        self.properties = []
        self.using = []

    def analyse(self):
        if not self.analysed:
            super().analyse()
            self.getclasscommentary()
            self.getUsing()
            self.getVariableUsing()
            self.getmethods()
            Property.getProperties(self)
            for method in self.methods:
                method.analyse()

    def getUsing(self):
        for line in self.lines:
            if line.startswith("using"):
                fromind = line.find("from")
                usingind = line.find("using")
                if fromind == -1:
                    usingline = line[usingind+6:-1].replace(".","/")
                else:
                    usingline = line[usingind+6:fromind-1].replace(".","/")
                if usingline.find("*") > -1:
                    filenames = hf.ListFiles(hf.folder, usingline[:-1], "*")
                    for filename in filenames:
                        self.using.append(filename)
                else:
                    self.using.append(usingline)
            if line.startswith("class"):
                inheritind = line.find("inherits")
                if inheritind > 0:
                    inheritclass = line[inheritind+9:-1]
                    for use in self.using:
                        slashind = use.rfind("/")
                        usage = use[slashind+1:]
                        if usage == inheritclass:
                            indexes = hf.getIndexFile()
                            for index in indexes:
                                ind = index["Filename"].find(".")
                                if index["Filename"][:ind] == usage:
                                    self.inherit = Classfile(hf.folder, index["Path"])
                                    break
                break

    def getVariableUsing(self):
        for line in self.lines:
            if line.startswith("constructor") or line.startswith("method"):
                return
            varind = line.find("variable")
            asind = line.find("as")
            noundoind = line.find("no-undo.")
            if varind > -1:
                varname = line[varind+9:asind].strip()
                typestring = line[asind+3:noundoind].strip()
                normalvartypes = ["date", "integer", "character", "int64", "datetime", "datetime-tz", "logical",
                                  "decimal", "longchar", "rowid"]
                if typestring in normalvartypes:
                    continue
                using = [using for using in self.using if using.endswith(typestring)]
                if using:
                    self.variableUsing.append({"Varname":varname, "Using":using[0]})


    def getclasscommentary(self):
        file = ""
        purpose = ""
        syntax = ""
        description = ""
        author = ""
        created = ""
        notes = ""
        flag = 1
        inClassCommentary = False
        for line in self.lines:
            if line.startswith("/*---"):
                inClassCommentary = True
                continue
            if line.endswith("---*/"):
                inClassCommentary = False
                break

            if inClassCommentary:
                if line.startswith("Purpose     :"):
                    flag = 2
                if line.startswith("Syntax      :"):
                    flag = 3
                if line.startswith("Description :"):
                    flag = 4
                if line.startswith("Author(s)   :"):
                    flag = 5
                if line.startswith("Created     :"):
                    flag = 6
                if line.startswith("Notes       :"):
                    flag = 7

                if flag == 1:
                    file += line
                if flag == 2:
                    purpose += line
                if flag == 3:
                    syntax += line
                if flag == 4:
                    description += line
                if flag == 5:
                    author += line
                if flag == 6:
                    created += line
                if flag == 7:
                    notes += line

        self.commentary = self.Commentary(file, purpose, syntax, description, author, created, notes)

    def getmethods(self):
        for i, line in enumerate(self.lines):
            if line.startswith("method"):
                static = ""
                start = line.find(" ")
                end = line.find(" ", start + 1)
                scope = line[start:end]
                start = end
                end = line.find(" ", start + 1)
                if line[start:end] == " static":
                    static = " static"
                    start = end
                    end = line.find(" ", start + 1)
                    returns = line[start:end]
                else:
                    static = ""
                    returns = line[start:end]
                start = end
                end = line.find("(", start + 1)
                name = line[start:end]
                self.methods.append(self.Method(name, scope, static, returns, i, self, self.lines, self.handles))

    def writexml(self, xml_doc):
        element = super().writexml(xml_doc)
        if not self.commentary:
            ET.SubElement(element, "Commentary").text = ""
        else:
            self.commentary.writexml(element)
        for method in self.methods:
            method.writexml(element)
