from tqdm import tqdm
import xml.etree.ElementTree as ET
from helperfunctions import Helperfunctions
from FileDescriptors.ClassFile import Classfile
from FileDescriptors.ProcedureFile import Procedurefile

hf = Helperfunctions()

xml_doc = ET.Element("root")
text_file = open("C:/Users/rick.winters/Desktop/Documentation.txt", "w")
text_file.write("")
text_file.close()

files = hf.readAnalysedFiles()

text_file = open("C:/Users/rick.winters/Desktop/Documentation.txt", "a")
print("Printing files")
for file in tqdm(files):
    file.analyse()
    text_file.write(str(file))
    file.writexml(xml_doc)
    #file.clear()

text_file.close()

hf.prettify(xml_doc)
tree = ET.ElementTree(xml_doc)
tree.write("C:/Users/rick.winters/Desktop/Documentation.xml", encoding="utf-8", xml_declaration=True)
