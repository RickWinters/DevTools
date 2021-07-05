from FileDescriptors import File

from helperfunctions import Helperfunctions
hf = Helperfunctions()

class Property:
    def __init__(self, name, referral):
        self.name = name
        self.referral = referral

    @staticmethod
    def getProperties(file):
        for i, line in enumerate(file.lines):
            if line.lower().startswith("define") and line.lower().find("property") > -1:
                asind = line.find("as")
                propertyind = line.find("property")
                name = line[propertyind + 9:asind - 1].strip()
                spaceind = line.find(" ", asind + 3)
                referral = line[asind + 3:spaceind].strip()
                if referral.startswith("be") or referral.startswith("bt"):
                    castfound = False
                    endproperty = False
                    while not (castfound or endproperty) and i < len(file.lines):
                        line = file.lines[i]
                        if line.find("cast") > 0:
                            castfound = True
                        if line.find("private set.") > -1:
                            endproperty = True
                        i += 1
                    if castfound:
                        leftind = line.rfind("(")
                        rightind = line.find(")")
                        referral = line[leftind + 1:rightind].replace(".", "/").replace('"', "")
                        indexes = hf.getIndexFile()
                        slashind = referral.rfind("/")
                        filename = referral[slashind + 1:]
                        for index in indexes:
                            dotind = index["Path"].find(".")
                            path = index["Path"][:dotind]
                            if path.lower().endswith(filename.lower()):
                                referral = index["Path"]
                                break
                    if endproperty:
                        for use in file.using:
                            if use.endswith(referral):
                                files = hf.ListFiles(hf.folder, hf.folderending, use)
                                for diskfile in files:
                                    if diskfile.startswith("/" + use + "."):
                                        referral = diskfile
                                        break
                                break
                file.properties.append(Property(name, referral))