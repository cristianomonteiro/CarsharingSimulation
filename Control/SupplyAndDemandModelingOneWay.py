from Model.User import User
from Control.SupplyAndDemandModeling import SupplyAndDemandModeling
from random import randint
from Utils.Methods import binarySearchAggregated
import networkx as nx
#import pickle
#from os import path
#from Model.DAO.UsersData import deleteUsersData, loadUsersData, persistUsersData

class SupplyAndDemandModelingOneWay(SupplyAndDemandModeling):
    def __init__(self, usersNumberDay, vehiclesNumberRange, timeRangeStation, timeDayRange, drivenDistanceLimits, usedTimeLimits, timeBetweenRents, graphSP, distribution, forceNewUsersData, addParkingConstraints, thresholdNearStations, secondsLimit, triesNumber):
        super(SupplyAndDemandModelingOneWay, self).__init__(usersNumberDay, vehiclesNumberRange, timeRangeStation, timeDayRange, drivenDistanceLimits, usedTimeLimits, timeBetweenRents, graphSP, distribution, forceNewUsersData, addParkingConstraints, thresholdNearStations, secondsLimit, triesNumber)
        self.carsharingMode = "OneWay"
    
    def adjustSumUsers(self, sumUsers, listUsersPerStation):
        if sumUsers >= self.usersNumberDay:
            #Add only the remaining
            #earlierSumUsers = sumUsers - usersPerStation
            #listUsersPerStation[-1] = (stationNode, self.usersNumberDay - earlierSumUsers)
            
            for i in range(sumUsers - self.usersNumberDay):
                #Reduces the lasts positions by one
                listUsersPerStation[-(i + 1)] = (listUsersPerStation[-(i + 1)][0], listUsersPerStation[-(i + 1)][1] - 1)
        else:
            #Add the users who left
            #leftUsers = self.usersNumberDay - sumUsers
            #listUsersPerStation[-1] = (stationNode, usersPerStation + leftUsers)
        
            for i in range(self.usersNumberDay - sumUsers):
                #Increases the lasts positions by one
                listUsersPerStation[-(i + 1)] = (listUsersPerStation[-(i + 1)][0], listUsersPerStation[-(i + 1)][1] + 1)
        
        listAggregated = []
        sumUsers = 0
        for x in listUsersPerStation:
            sumUsers += x[1]
            listAggregated.append(sumUsers)
        
        return listUsersPerStation, sumUsers, listAggregated
    
    def randomDestinyNode(self, sumUsersAttrac, listUsersPerStationAttracAggreg):
        #Scenario 2: the car is taken at one station and delivered at any station
        randomDestinyPos = randint(0, sumUsersAttrac)
        #Get the closest position in the aggregated list
        randomDestinyPos = binarySearchAggregated(randomDestinyPos, listUsersPerStationAttracAggreg)
        randomDestiny = self.stations[randomDestinyPos]
        
        return randomDestiny
    
    def simulateUsers(self):
        print("Simulating users...")
        
        listUsersPerStationProd = []
        listUsersPerStationAttrac = []
        listUsersPerStationAttracAggreg = []
        
        sumProdTotal = 0
        sumAttracTotal = 0
        for i, stationNode in enumerate(self.stations):
            if stationNode.station.maxVehicles != 0:    
                sumProdTotal += stationNode.station.zoneProduction
                sumAttracTotal += stationNode.station.zoneAttraction
        
        sumUsersProd = 0
        sumUsersAttrac = 0
        lastResidueIntProd = 0
        lastResidueIntAttrac = 0
        for stationNode in self.stations:
            if stationNode.station.maxVehicles != 0:
                usersPerStationProd = (stationNode.station.zoneProduction * self.usersNumberDay)/sumProdTotal
                usersPerStationAttrac = (stationNode.station.zoneAttraction * self.usersNumberDay)/sumAttracTotal
                #Don't truncate. Instead of it, round and cast to int
                #Residue after rounding
                residueProd = usersPerStationProd - int(round(usersPerStationProd, 0))
                usersPerStationProd = int(round(usersPerStationProd + max(0, lastResidueIntProd), 0))
                listUsersPerStationProd.append((stationNode, usersPerStationProd))
                lastResidueIntProd = residueProd
    
                residueAttrac = usersPerStationAttrac - int(round(usersPerStationAttrac, 0))
                usersPerStationAttrac = int(round(usersPerStationAttrac + max(0, lastResidueIntAttrac), 0))
                listUsersPerStationAttrac.append((stationNode, usersPerStationAttrac))
                lastResidueIntAttrac = residueAttrac
                
                sumUsersProd += usersPerStationProd
                sumUsersAttrac += usersPerStationAttrac
                listUsersPerStationAttracAggreg.append(sumUsersAttrac)
                
                #if sumUsersProd >= self.usersNumberDay:
                #    break
            
        usersPerStationProd, sumUsersProd, listUsersPerStationAttracAggreg = self.adjustSumUsers(sumUsersProd, listUsersPerStationProd)
        usersPerStationAttrac, sumUsersAttrac, listUsersPerStationAttracAggreg = self.adjustSumUsers(sumUsersAttrac, listUsersPerStationAttrac)

        if self.forceNewUsersData == True:
            self.deleteUsersData()

        #Old implementation for file
        #if path.exists(self.usersRandomParamsFilePath) == True:
        self.usersData = self.loadUsersData()
        if len(self.usersData) > 0:
            self.buildParams = False
            #self.paramsToPersist = self.loadParams()
        else:
            self.buildParams = True
            #self.paramsToPersist = []
        
        users = []
        idUser = 1
        stationPos = 0
        for stationNode, usersPerStationProd in listUsersPerStationProd:
            for i in range(0, usersPerStationProd):
                #Generate and build the parameters whether they don't exist yet
                if self.buildParams == True:
                    #Scenario 2: the car is taken at one station and delivered at any station
                    #Get the closest position in the aggregated list
                    randomDestiny = self.randomDestinyNode(sumUsersAttrac, listUsersPerStationAttracAggreg)
                    
                    try:
                        randomNodeDistance = nx.shortest_path_length(self.graphSP.graph, stationNode.location, randomDestiny.location, 'weight')
                    except Exception as e:
                        randomNodeDistance = self.drivenDistanceLimits[1]
                        print(e)
                    
                    #Whether the destiny station is the same of the start station
                    if randomDestiny == stationNode:
                        randomNodeDistance = self.drivenDistanceLimits[1]
                        
                    #Go from CAOA station to random destiny and back to the same CAOA station
                    raisingFactorShortestDistance = 1
                    drivenDistance = randomNodeDistance * raisingFactorShortestDistance
                    
                    #Adjust the driven distance to be between the limits
                    drivenDistance = max(drivenDistance, self.drivenDistanceLimits[0])
                    drivenDistance = min(drivenDistance, self.drivenDistanceLimits[1])
                
                    stationStartTimeRange = max(self.timeDayRange[0], self.timeRangeStation[stationPos][0])
                    stationEndTimeRange = min(self.timeDayRange[1], self.timeRangeStation[stationPos][1])
                    
                    timeStart = randint(stationStartTimeRange, stationEndTimeRange)
                    speed = 10
                    drivenTime = 60 * (drivenDistance/1000)/speed
                    randomTime = randint(0, 1 * 60)
                    elapsedTime = min(drivenTime + randomTime, self.usedTimeLimits[1])
                    timeEnd = min(timeStart + elapsedTime + self.timeBetweenRents, self.timeRangeStation[stationPos][2])
                    #Adjust elapsedTime based on time restrictions from end station
                    elapsedTime = timeEnd - timeStart
                    
                    #Now, checks restrictions about start time and driving distance
                    if elapsedTime < self.usedTimeLimits[0]:
                        timeStart = max(timeEnd - self.usedTimeLimits[0], self.timeRangeStation[stationPos][0])
                        elapsedTime = timeEnd - timeStart
                        
                        #If elapsedTime is still less than self.usedTimeLimits[0], is it needed to raise the end time
                        if elapsedTime < self.usedTimeLimits[0]:
                            timeEnd = min(timeStart + self.usedTimeLimits[0] + self.timeBetweenRents, self.timeRangeStation[stationPos][1])
                            elapsedTime = timeEnd - timeStart
                    
                    #self.paramsToPersist.append((drivenDistance, timeStart, speed, drivenTime, randomTime, timeEnd, randomDestiny, fareToBePaid))
                
                #Load the parameters whether they already exist
                else:
                    #(drivenDistance, timeStart, speed, drivenTime, randomTime, timeEnd, randomDestiny, fareToBePaid) = self.paramsToPersist[idUser - 1]
                
                    (idLoaded, endLocation, timeStart, timeEnd, drivenDistance) = self.usersData[idUser - 1]
                    #casting from Decimal to int of float
                    idLoaded = int(idLoaded)
                    idUser = idLoaded
                    timeStart = int(timeStart)
                    timeEnd = int(timeEnd)
                    drivenDistance = float(drivenDistance)
                    elapsedTime = timeEnd - timeStart
                    
                    try:
                        randomDestiny = self.graphSP.roadNetwork.nodes[endLocation]
                    except Exception:
                        randomDestiny = self.randomDestinyNode(sumUsersAttrac, listUsersPerStationAttracAggreg)
                        print("DESTINY STATION NOT FOUND!!!")
                    
                #Turbi
                #fareToBePaid = self.fareTurbi(elapsedTime, drivenDistance)

                #Zazcar
                fareToBePaid = self.fareZazcar(elapsedTime, drivenDistance)
                
                user = User(str(idUser) + '_' + str(i + 1), stationNode.station, randomDestiny.station, timeStart, timeEnd, randomDestiny, drivenDistance, fareToBePaid)
                
                #This user can be in a restriction among the others from that CAOA station
                stationNode.station.addInvolvedUsersPos(len(users))
                users.append(user)
                
                idUser += 1
            
            stationPos += 1
        
        self.users = users
        self.repeatNearestUsers()
        self.generateLeftAndGotVehicles()
        
        if self.buildParams == True:
            #self.persistParams()
            self.persistUsersData()
        
    #def persistParams(self):
    #    self.usersRandomParamsFile = open(self.usersRandomParamsFilePath, 'wb')
    #    pickle.dump(self.paramsToPersist, self.usersRandomParamsFile)
    #    self.usersRandomParamsFile.close()
    
    #def loadParams(self):
    #    self.usersRandomParamsFile = open(self.usersRandomParamsFilePath, 'rb')
    #    self.paramsToPersist = pickle.load(self.usersRandomParamsFile)
    #    self.usersRandomParamsFile.close()
        
    #    return self.paramsToPersist
    
    #def persistUsersData(self):
    #    persistUsersData(self.users, self.carsharingMode, self.usersNumberDay, self.distribution)
    
    #def loadUsersData(self):
    #    return loadUsersData(self.carsharingMode, self.usersNumberDay, self.distribution)
    
    #def deleteUsersData(self):
    #    return deleteUsersData(self.carsharingMode, self.usersNumberDay, self.distribution)
