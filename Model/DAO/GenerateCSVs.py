import os

def generateCSVs(folderPath):
    for fileName in sorted(os.listdir(folderPath)):
        if fileName.endswith(".txt"):
            fileNameComplete = os.path.join(folderPath, fileName)
            
            createdFileName = fileName[:-4] + '.csv'
            createdFileNameComplete = os.path.join(folderPath, createdFileName)
            fileCreated = open(createdFileNameComplete, 'w+')
            fileCreated.write("Vehicles,Clients,Status\n")
            with open(fileNameComplete) as f:
                for line in list(f):
                    lineSplitted = line.split()
                    if len(lineSplitted) > 1 and lineSplitted[0] == "Status:":
                        status = ' '.join(str(e) for e in lineSplitted[1:])
                    if len(lineSplitted) > 2 and lineSplitted[0] == "Sum" and lineSplitted[1] == "F2:":
                        maxVehicles = round(float(lineSplitted[2]))
                    elif len(lineSplitted) > 3 and " ".join(lineSplitted[:4]) == "Number of Attended Users:":
                        maxClients = round(float(lineSplitted[4]))
                        fileCreated.write(str(maxVehicles) + ',' + str(maxClients) + ',' + status + '\n')
                        
            fileCreated.close()
            f.close()
                
#generateCSVs('/home/cristiano/Dropbox/UFMG/Cristiano/Doutorado/Projeto Montadora CAOA/Arquivos Problema Otimização/Resultados/')

