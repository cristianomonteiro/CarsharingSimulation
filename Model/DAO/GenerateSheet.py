import os
import xlsxwriter

class ResultFile():
    def __init__(self, clientsNumber, usesParkingPartners, totalParkingNumber, usesParkingConstraints, minVehicles, maxVehicles, minClients, maxClients, minVehiclesTested, maxVehiclesTested, minRevenue, maxRevenue, walkingDistance, minTime, maxTime, minDistance, maxDistance, status, carsharingMode):
        self.clientsNumber = clientsNumber
        self.usesParkingPartners = usesParkingPartners
        self.totalParkingNumber = totalParkingNumber
        self.usesParkingConstraints = usesParkingConstraints
        self.minVehicles = minVehicles
        self.maxVehicles = maxVehicles
        self.minClients = minClients
        self.maxClients = maxClients
        self.minVehiclesTested = minVehiclesTested
        self.maxVehiclesTested = maxVehiclesTested
        self.minRevenue = minRevenue
        self.maxRevenue = maxRevenue
        self.walkingDistance = walkingDistance
        self.minTime = minTime
        self.maxTime = maxTime
        self.minDistance = minDistance
        self.maxDistance = maxDistance
        self.status = status
        self.carsharingMode = carsharingMode

def generateSheet(folderPath):
    #Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook(folderPath + '/Planilha dos Resultados.xlsx')
    worksheet = workbook.add_worksheet()
    row = 0
    worksheet.write(row, 0, "MODELO")
    worksheet.write(row, 1, "FÓRMULA DE FATURAMENTO")
    worksheet.write(row, 2, "CENÁRIOS")
    worksheet.write(row, 3, "USUÁRIOS")
    worksheet.write(row, 4, "VAGAS")
    worksheet.write(row, 5, "CARROS")
    worksheet.write(row, 6, "METROS CAMINHADOS")
    worksheet.write(row, 7, "KM (MÁX)")
    worksheet.write(row, 8, "KM (MÍN)")
    worksheet.write(row, 9, "MINUTOS (MÁX)")
    worksheet.write(row, 10, "MINUTOS (MÍN)")
    worksheet.write(row, 11, "STATUS")
    worksheet.write(row, 12, "FATURAMENTO (MÁX)")
    worksheet.write(row, 13, "FATURAMENTO (MÍN)")
    worksheet.write(row, 14, "Nº VEÍCULOS USADOS (MÁX)")
    worksheet.write(row, 15, "Nº VEÍCULOS USADOS (MÍN)")
    worksheet.write(row, 16, "Nº CLIENTES (MÁX)")
    worksheet.write(row, 17, "Nº CLIENTES (MÍN)")
    row += 1

    for fileName in sorted(os.listdir(folderPath)):
        if fileName.endswith(".txt"):
            fileNameComplete = os.path.join(folderPath, fileName)
            with open(fileNameComplete) as f:
                for line in reversed(list(f)):
                    lineSplitted = line.split()
                    if len(lineSplitted) > 3 and " ".join(lineSplitted[:4]) == "Number of Attended Users:":
                        maxClients = round(float(lineSplitted[4]))
                    elif len(lineSplitted) > 1 and lineSplitted[0] == "Sum" and lineSplitted[1] == "F2:":
                        maxVehicles = round(float(lineSplitted[2]))
                    elif len(lineSplitted) > 1 and lineSplitted[0] == "Sum" and lineSplitted[1] == "F1:":
                        maxRevenue = round(float(lineSplitted[2]))
                    elif len(lineSplitted) > 0 and lineSplitted[0] == "Status:":
                        status = ' '.join(str(e) for e in lineSplitted[1:])
                        break
            f.close()

            with open(fileNameComplete) as f:
                for line in list(f):
                    lineSplitted = line.split()
                    if len(lineSplitted) > 1 and lineSplitted[0] == "Sum" and lineSplitted[1] == "F1:":
                        minRevenue = round(float(lineSplitted[2]))
                    elif len(lineSplitted) > 1 and lineSplitted[0] == "Sum" and lineSplitted[1] == "F2:":
                        minVehicles = round(float(lineSplitted[2]))
                    elif len(lineSplitted) > 3 and " ".join(lineSplitted[:4]) == "Number of Attended Users:":
                        minClients = round(float(lineSplitted[4]))
                        break
            f.close()
            
            #File example
            #500_[1,100]_[True]_49_[5000,50000]_[45,240]_False_1000_ResultsOneWay
            fileNameParams = fileName.split("/")
            paramsFileName = fileNameParams[-1].split("_")
            clientsNumber = int(paramsFileName[0])
            minVehiclesTested = int(paramsFileName[1].replace("[", "").replace("]", "").split(",")[0])
            maxVehiclesTested = int(paramsFileName[1].replace("[", "").replace("]", "").split(",")[1])
            usesParkingPartners = paramsFileName[2].replace("[", "").replace("]", "").split(",")[0]
            if usesParkingPartners == 'True':
                usesParkingPartners = True
            else:
                usesParkingPartners = False
            totalParkingNumber = int(paramsFileName[3])
            minDistance = int(paramsFileName[4].replace("[", "").replace("]", "").split(",")[0])
            maxDistance = int(paramsFileName[4].replace("[", "").replace("]", "").split(",")[1])
            minTime = int(paramsFileName[5].replace("[", "").replace("]", "").split(",")[0])
            maxTime = int(paramsFileName[5].replace("[", "").replace("]", "").split(",")[1])
            usesParkingConstraints = paramsFileName[6]
            if usesParkingConstraints == 'True':
                usesParkingConstraints = True
            elif usesParkingConstraints == 'TrueForPartners':
                usesParkingConstraints = 'TrueForPartners'
            else:
                usesParkingConstraints = False
            walkingDistance = int(paramsFileName[7])
            carsharingMode = paramsFileName[8][7:-4]
            
            resultFile = ResultFile(clientsNumber, usesParkingPartners, totalParkingNumber, usesParkingConstraints, minVehicles, maxVehicles, minClients, maxClients, minVehiclesTested, maxVehiclesTested, minRevenue, maxRevenue, walkingDistance, minTime, maxTime, minDistance, maxDistance, status, carsharingMode)

            worksheet.write(row, 0, carsharingMode)
            worksheet.write(row, 1, 'Zazcar')
            if totalParkingNumber == 27:
                parkingScenario = 'LOJAS CAOA'
            elif totalParkingNumber == 31:
                parkingScenario = 'LOJAS CAOA LOJAS FAKES'
            elif totalParkingNumber == 49:
                parkingScenario = 'LOJAS CAOA ESTACIONAMENTOS'
            elif totalParkingNumber == 53:
                parkingScenario = 'LOJAS CAOA ESTACIONAMENTOS LOJAS FAKES'
            elif totalParkingNumber == 93:
                parkingScenario = 'LOJAS CAOA ESTACIONAMENTOS (3 VAGAS)'
            elif totalParkingNumber == 97:
                parkingScenario = 'LOJAS CAOA ESTACIONAMENTOS (3 VAGAS) LOJAS FAKES'
            
            if usesParkingConstraints == True:
                parkingScenario += ' (Vagas Restritas)'
            elif usesParkingConstraints == 'TrueForPartners':
                parkingScenario += ' (Vagas Restritas para Parceiros)'
            
            worksheet.write(row, 2, parkingScenario)
            worksheet.write(row, 3, clientsNumber)
            worksheet.write(row, 4, totalParkingNumber)
            worksheet.write(row, 5, maxVehiclesTested)
            worksheet.write(row, 6, walkingDistance)
            worksheet.write(row, 7, maxDistance)
            worksheet.write(row, 8, minDistance)
            worksheet.write(row, 9, maxTime)
            worksheet.write(row, 10, minTime)
            worksheet.write(row, 11, status)
            worksheet.write(row, 12, maxRevenue)
            worksheet.write(row, 13, minRevenue)
            worksheet.write(row, 14, maxVehicles)
            worksheet.write(row, 15, minVehicles)
            worksheet.write(row, 16, maxClients)
            worksheet.write(row, 17, minClients)
            
            row += 1
    
    workbook.close()
                
#generateSheet('/home/cristiano/Dropbox/UFMG/Cristiano/Doutorado/Projeto Montadora CAOA/Arquivos Problema Otimização/Resultados/')
