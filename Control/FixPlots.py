import numpy as np
import time
import matplotlib.pyplot as plt
from Model.DAO.GenerateSheet import generateSheet
from Model.DAO.GenerateCSVs import generateCSVs

def generateTicks(axisData):
    minValue = min(axisData)
    maxValue = max(axisData)
    
    numTicks = 6
    if maxValue < 100:
        numTicks = 12
    elif maxValue < 1000:
        numTicks = 10
    
    if len(axisData) < numTicks:
        ticks = [round(x) for x in axisData]
    else:
        #If all values are integers, arange distribute the integer values better
        if all(x == int(x) for x in axisData):
            rangeTicks = maxValue - minValue
            stepTicks = round(rangeTicks/numTicks)
            #If the number of ticks generated will be 30% greater than the expected
            if rangeTicks/stepTicks > numTicks * 1.3:
                stepTicks += 1
            ticks = list(np.arange(start=minValue, stop=maxValue, step=stepTicks))
            ticks.append(maxValue)
        else:
            ticks = np.linspace(start=minValue, stop=maxValue, num=numTicks, endpoint=True)
            ticks = [round(x) for x in ticks]

    #Remove the penultimate item if it is so close to the last
    if len(ticks) >= 3 and ticks[-1] - ticks[-2] <= (ticks[-2] - ticks[-3])/2:
        del ticks[-2]
    
    return ticks

def plotGraphs():
    resultsFilePath = '/home/cristiano/Dropbox/UFMG/Cristiano/Doutorado/Projeto Montadora CAOA/Arquivos Problema Otimização/Resultados/500_[1,100]_[True]_93_[5000,50000]_[45,240]_True_1000_ResultsOneWay.txt'
    
    graphFilePathRevenueVehicles = '/home/cristiano/Dropbox/UFMG/Cristiano/Doutorado/Projeto Montadora CAOA/Arquivos Problema Otimização/Resultados/500_[1,100]_[True]_93_[5000,50000]_[45,240]_True_1000_FigureOneWay_Revenue_Vehicles.png'
    graphFilePathRevenueClients = '/home/cristiano/Dropbox/UFMG/Cristiano/Doutorado/Projeto Montadora CAOA/Arquivos Problema Otimização/Resultados/500_[1,100]_[True]_93_[5000,50000]_[45,240]_True_1000_FigureOneWay_Revenue_Clients.png'
    graphFilePathVehiclesClients = '/home/cristiano/Dropbox/UFMG/Cristiano/Doutorado/Projeto Montadora CAOA/Arquivos Problema Otimização/Resultados/500_[1,100]_[True]_93_[5000,50000]_[45,240]_True_1000_FigureOneWay_Vehicles_Clients.png'
    
    f1 = np.array([])
    f2 = np.array([])
    numUsers = np.array([])
    with open(resultsFilePath, 'r') as fileResults:
        for line in fileResults:
            lineList = line.split()
            if len(lineList) == 3 and lineList[0] == 'Sum':
                if lineList[1] == 'F1:':
                    f1 = np.hstack(( f1, float(lineList[2]) ))
                elif lineList[1] == 'F2:':
                    f2 = np.hstack(( f2, float(lineList[2]) ))
            elif len(lineList) == 5 and lineList[3] == "Users:":
                numUsers = np.hstack(( numUsers, float(lineList[4]) ))
    
    axis = [[f1, f2], [f1, numUsers], [f2, numUsers]]
    textF1 = "Faturamento"
    textF2 = "Número de Veículos"
    textNumUsers = "Número de Clientes Atendidos"
    textAxis = [[textF1, textF2], [textF1, textNumUsers], [textF2, textNumUsers]]
    fileGraphs = [graphFilePathRevenueVehicles, graphFilePathRevenueClients, graphFilePathVehiclesClients]
    
    for i in range(len(axis)):
    #    plt.figure(i + 1)
        #ax = plt.figure(i + 1).gca()
    #    plt.plot(axis[i][0], axis[i][1], 'r.', markersize=10)
    #    plt.xlabel(textAxis[i][0], fontsize=16, style='italic')
    #    plt.ylabel(textAxis[i][1], fontsize=16, style='italic')
        xTicks = generateTicks(axis[i][0])
        yTicks = generateTicks(axis[i][1])
    #    plt.xticks(xTicks, fontsize=14)
    #    plt.yticks(yTicks, fontsize=14)
        #ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        #ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    #    plt.grid(True)
        
        millis = int(round(time.time() * 1000))
        plt.figure(millis + i + 1)
        #ax = plt.figure(i + 1).gca()
        plt.plot(axis[i][0], axis[i][1], 'r.', markersize=10)
        plt.xlabel(textAxis[i][0], fontsize=16, style='italic')
        plt.ylabel(textAxis[i][1], fontsize=16, style='italic')
        plt.xticks(xTicks, fontsize=14)
        plt.yticks(yTicks, fontsize=14)
        #ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        #ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.grid(True)
        plt.savefig(fileGraphs[i], bbox_inches='tight')
        
    #plt.show()
    plt.close('all')

plotGraphs()
generateSheet('/home/cristiano/Dropbox/UFMG/Cristiano/Doutorado/Projeto Montadora CAOA/Arquivos Problema Otimização/Resultados/')
generateCSVs('/home/cristiano/Dropbox/UFMG/Cristiano/Doutorado/Projeto Montadora CAOA/Arquivos Problema Otimização/Resultados/')
