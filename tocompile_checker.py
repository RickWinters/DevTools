from tqdm import tqdm
import xml.etree.ElementTree as ET
from helperfunctions import Helperfunctions
from FileDescriptors.DataSet import DataSet
from FileDescriptors.ClassFile import Classfile
from FileDescriptors.ProcedureFile import Procedurefile

hf = Helperfunctions()

text_file = open("C:/Users/rick.winters/Desktop/tocompile_overview.txt", "w")
text_file.write("")
text_file.close()

xml_doc = ET.Element("root")
indexes = hf.getIndexFile()
files = hf.readAnalysedFiles()

for index in indexes:
    if index["Filename"].startswith("ds") and index["Filename"].endswith(".i"):
        files.append(DataSet(hf.folder, index["Path"], indexes))

text_file = open("C:/Users/rick.winters/Desktop/tocompile_overview.txt", "a")
print("ANALYZING " + str(len(files)) + " FILES")
for file in tqdm(files):
    file.cleanUp()
    if not file.analysed:
        hf.getCode(file)
        file.getIncludes()
        file.checkToCompile()
    text_file.write(str(file))
    file.writexml(xml_doc)

text_file.close()

hf.prettify(xml_doc)
tree = ET.ElementTree(xml_doc)
tree.write("C:/Users/rick.winters/Desktop/tocompile_overview.xml", encoding="utf-8", xml_declaration=True)
