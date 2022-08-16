# -*- coding: utf-8 -*-

import os
import numpy as np
import matplotlib.pyplot as plt
from Utils.Methods import generateTicks

inputFolder = '/home/cristiano/Dropbox/UFMG/Cristiano/Doutorado/Projeto Montadora CAOA/Arquivos Problema Otimização/Resultados/'
outputFolder = '/home/cristiano/Dropbox/UFMG/Cristiano/Doutorado/Projeto Montadora CAOA/Arquivos Problema Otimização/Figuras/'

def loadData(inputFolder):
    data = {}
    for fileName in sorted(os.listdir(inputFolder)):
        if fileName.endswith('.txt') and int(fileName.split('_')[7]) > 0:
            fileNameComplete = os.path.join(inputFolder, fileName)

            status = []
            clients = []
            vehicles = []
            walkingPercentages = []
            try:
                with open(fileNameComplete) as f:
                    for line in list(f):
                        lineSplitted = line.split()
                        if len(lineSplitted) > 0 and lineSplitted[0] == 'Status:':
                            walkingClientsNumber = 0
                            statusText = ' '.join(str(e) for e in lineSplitted[1:])
                            status.append(True if statusText == 'Optimal' else False)
                        
                        if len(lineSplitted) > 0 and lineSplitted[0].startswith('f1_'):
                            almostIntThreshold = 0.8
                            if len(lineSplitted[0].split('_')) > 3 and float(lineSplitted[3][2:]) >= almostIntThreshold*float(lineSplitted[1]):
                                walkingClientsNumber += 1
                                            
                        elif len(lineSplitted) > 1 and lineSplitted[0] == 'Sum' and lineSplitted[1] == 'F2:':
                            vehicles.append(round(float(lineSplitted[2])))
                        
                        elif len(lineSplitted) > 3 and ' '.join(lineSplitted[:4]) == 'Number of Attended Users:':
                            numberAttendedClients = round(float(lineSplitted[4]))
                            clients.append(numberAttendedClients)
                            walkingPercentages.append((walkingClientsNumber*100)/numberAttendedClients)

                f.close()
                data[fileName[:-4]] = (np.asarray(status), np.asarray(walkingPercentages), np.asarray(vehicles))
            
            except Exception as e:
                print(e.message)
    
    return data

def printFigures(inputFolder, outputFolder):
    data = loadData(inputFolder)
    
    paramsParkingRestrictions = ['False', 'TrueForPartners', 'True']
    paramsMode = ['ResultsRoundTrip', 'ResultsOneWay']
    paramsWalkingDistance = [1000, 750, 500, 250]
    paramsPartners = ['[True]', '[False]']
    paramsClients = [500, 300, 100]
    paramsParkingNumber = [97, 93, 53, 49, 31, 27]
    #paramsParkingNumber = [31]

    plt.close('all')
    
    colorTo0_1 = {27:0, 31:17, 49:42, 53:62, 93:88, 97:100}
    tickColors = ['27', '31', '49', '53', '93', '97']
    ticksConverted = [colorTo0_1[x] for x in sorted(paramsParkingNumber)]
    
    i = 1
    for parkingRestrictions in paramsParkingRestrictions:
        for mode in paramsMode:
            if mode == 'ResultsRoundTrip' and parkingRestrictions != 'False':
                continue
            for walkingDistance in paramsWalkingDistance:
                plt.figure(i)
                plt.set_cmap('jet')
                
                posStartNumClientsTrue = []
                posStartNumClientsFalse = []
                numClientsStart = []
                
                vehiclesAccumlatedTrue = []
                walkingClientsNumberAccumlatedTrue = []
                colorsAccumulatedTrue = []
                vehiclesAccumlatedFalse = []
                walkingClientsNumberAccumlatedFalse = []
                colorsAccumulatedFalse = []
                                                
                for numClients in paramsClients:
                    for partners in paramsPartners:
                        for parkingNumber in paramsParkingNumber:
                            if (parkingNumber < 49 and partners == '[True]') or (parkingNumber > 31 and partners == '[False]'):
                                continue
                        
                            settingName = str(numClients) + '_[1,100]_' + partners + '_' + str(parkingNumber)
                            settingName += '_[10000,100000]_[90,480]_' if mode == 'ResultsRoundTrip' else '_[5000,50000]_[45,240]_'
                            settingName += parkingRestrictions + '_' + str(walkingDistance) + '_' + mode
                            print(settingName)
                            
                            try:
                                (status, walkingClientsNumber, vehicles) = data[settingName]
                                posTrue = np.where(status == True)
                                colorsArrayTrue = len(posTrue[0]) * [parkingNumber]
                                xTrue = vehicles[posTrue]
                                yTrue = walkingClientsNumber[posTrue]
                                posFalse = np.where(status == False)
                                colorsArrayFalse = len(posFalse[0]) * [parkingNumber]
                                xFalse = vehicles[posFalse]
                                yFalse = walkingClientsNumber[posFalse]
                                
                                #plt.plot(xTrue, yTrue, c=cmap.to_rgba(colorShape), marker=marker, markersize=10, linestyle='None')
                                #plt.plot(xFalse, yFalse, c=cmap.to_rgba(colorShape), markersize=10, linestyle='None')
                                
                                vehiclesAccumlatedTrue.extend(xTrue)
                                walkingClientsNumberAccumlatedTrue.extend(yTrue)
                                colorsAccumulatedTrue.extend(len(xTrue) * [colorTo0_1[parkingNumber]])
                                
                                vehiclesAccumlatedFalse.extend(xFalse)
                                walkingClientsNumberAccumlatedFalse.extend(yFalse)
                                colorsAccumulatedFalse.extend(len(xFalse) * [colorTo0_1[parkingNumber]])                        

                            except:
                                print(settingName)
                            
                    posStartNumClientsTrue.append(len(vehiclesAccumlatedTrue))
                    posStartNumClientsFalse.append(len(vehiclesAccumlatedFalse))
                    numClientsStart.append(numClients)
                        
                print(i)
                i += 1
                plt.xlabel('Vehicles', fontsize=16, style='italic')
                plt.ylabel('Walking Clients (%)', fontsize=16, style='italic')
                
                legendsTrue = [None, None, None]
                legendsFalse = [None, None, None]
                startPosTrue = 0
                startPosFalse = 0
                for count, walkingClientsNumber in enumerate(numClientsStart):
                    numClientsTrue = posStartNumClientsTrue[count] - startPosTrue
                    numClientsFalse = posStartNumClientsFalse[count] - startPosFalse
                    markerTrue = '.'
                    markerFalse = '+'
                    if walkingClientsNumber == 100:
                        posLegendClients = 2
                        pointSizeTrue = [50] * numClientsTrue
                        pointSizeFalse = [50] * numClientsFalse
                    elif walkingClientsNumber == 300:
                        posLegendClients = 1
                        markerTrue = '*'
                        markerFalse = '4'
                        pointSizeTrue = [75] * numClientsTrue
                        pointSizeFalse = [75] * numClientsFalse
                    elif walkingClientsNumber == 500:
                        posLegendClients = 0
                        pointSizeTrue = [200] * numClientsTrue
                        pointSizeFalse = [200] * numClientsFalse
                    
                    endPosTrue = startPosTrue + numClientsTrue
                    legendTrue = plt.scatter(vehiclesAccumlatedTrue[startPosTrue:endPosTrue], walkingClientsNumberAccumlatedTrue[startPosTrue:endPosTrue], s=pointSizeTrue, c=colorsAccumulatedTrue[startPosTrue:endPosTrue], marker=markerTrue)
                    #It is needed to set the min and max clim because are made more than one scatter                
                    plt.clim(min(ticksConverted), max(ticksConverted))
                    if len(vehiclesAccumlatedTrue[startPosTrue:endPosTrue]) > 0:
                        legendsTrue[posLegendClients] = legendTrue
                    startPosTrue = endPosTrue
                    
                    endPosFalse = startPosFalse + numClientsFalse
                    legendFalse = plt.scatter(vehiclesAccumlatedFalse[startPosFalse:endPosFalse], walkingClientsNumberAccumlatedFalse[startPosFalse:endPosFalse], s=pointSizeFalse, c=colorsAccumulatedFalse[startPosFalse:endPosFalse], marker=markerFalse)
                    #It is needed to set the min and max clim because are made more than one scatter                
                    plt.clim(min(ticksConverted), max(ticksConverted))
                    if len(vehiclesAccumlatedFalse[startPosFalse:endPosFalse]) > 0:
                        legendsFalse[posLegendClients] = legendFalse
                    startPosFalse = endPosFalse
                
                labels = ['500 clients, O. G.', '500 clients', '300 clients, O. G.', '300 clients', '100 clients, O. G.', '100 clients']
                legendsMerged = []
                for x, y in zip(legendsTrue, legendsFalse):
                    legendsMerged.append(x)
                    legendsMerged.append(y)
                    
                legendsUnited = []
                labelsUnited = []
                for marker, label in zip(legendsMerged, labels):
                    if marker is not None:
                        legendsUnited.append(marker)
                        labelsUnited.append(label)
                plt.legend((legendsUnited), (labelsUnited), loc=1)
                
                #plt.scatter(vehiclesAccumlatedTrue, walkingClientsNumberAccumlatedTrue, c=colorsAccumulatedTrue, marker='.')
                #plt.scatter(vehiclesAccumlatedFalse, walkingClientsNumberAccumlatedFalse, c=colorsAccumulatedFalse, marker='+')

                #It is needed to set the min and max clim because are made more than one scatter                
                #plt.clim(min(paramsParkingNumber), max(paramsParkingNumber))
                #plt.clim(min(ticksConverted), max(ticksConverted))
                #plt.xlim(xmin=0)
                #plt.ylim(ymin=0)

                xTicks = generateTicks(vehiclesAccumlatedTrue, vehiclesAccumlatedFalse)
                yTicks = generateTicks(walkingClientsNumberAccumlatedTrue, walkingClientsNumberAccumlatedFalse)
                plt.xticks(xTicks, fontsize=14)
                plt.yticks(yTicks, fontsize=14)
                plt.grid(True)
                cbar = plt.colorbar(ticks=ticksConverted)
                #cbar = plt.colorbar(ticks=paramsParkingNumber)
                #cbar = plt.colorbar(ticks=[colorTo0_1[x] for x in sorted(paramsParkingNumber)])
                #cbar.set_ticks(tickColors)
                cbar.ax.set_yticklabels(tickColors)
                cbar.set_label(label='Parking Slots', size=16, style='italic', rotation=270, labelpad=18)
                plt.savefig(outputFolder + 'WalkingPercentage_' + mode + '_' + str(parkingRestrictions) + '_' + str(walkingDistance) + '.png', bbox_inches='tight')
                plt.savefig(outputFolder + 'WalkingPercentage_' + mode + '_' + str(parkingRestrictions) + '_' + str(walkingDistance) + '.eps', bbox_inches='tight')
                
                plt.show()
                    
    plt.close('all')

printFigures(inputFolder, outputFolder)
