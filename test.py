from helperfunctions import Helperfunctions

hf = Helperfunctions()

files = hf.readAnalysedFiles()
totalnlines = 0

for file in files:
    totalnlines += len(file.lines)

print(totalnlines)
