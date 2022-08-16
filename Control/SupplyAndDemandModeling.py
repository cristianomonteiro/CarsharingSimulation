from Model.User import User
from random import choice, randint
import networkx as nx
#import pickle
#from os import path
import copy
from Model.DAO.UsersData import deleteUsersData, loadUsersData, persistUsersData

class SupplyAndDemandModeling():
    def __init__(self, usersNumberDay, vehiclesNumberRange, timeRangeStation, timeDayRange, drivenDistanceLimits, usedTimeLimits, timeBetweenRents, graphSP, distribution, forceNewUsersData, addParkingConstraints, thresholdNearStations, secondsLimit, triesNumber):
        self.usersNumberDay = usersNumberDay
        self.vehiclesNumberRange = vehiclesNumberRange
        self.timeRangeStation = timeRangeStation
        self.timeDayRange = timeDayRange
        self.graphSP = graphSP
        self.stations = graphSP.roadNetwork.stations
        
        self.drivenDistanceLimits = drivenDistanceLimits
        self.usedTimeLimits = usedTimeLimits
        
        self.timeBetweenRents = timeBetweenRents
        
        self.distribution = distribution
        
        self.forceNewUsersData = forceNewUsersData
        
        self.addParkingConstraints = addParkingConstraints
        
        self.thresholdNearStations = thresholdNearStations
        
        self.secondsLimit = secondsLimit
        self.triesNumber = triesNumber
        
        self.folderPath = '/Server HD⁩/⁨Users⁩/⁨cristianomartinsm/Dropbox/UFMG/Cristiano/Doutorado/Projeto Montadora CAOA/Arquivos Problema Otimização/Usuários/'
    
        self.carsharingMode = "RoundTrip"
    
    def listToString(self, dataList):
        stringReturn = "[" + ','.join(str(e) for e in dataList) + "]"
        return stringReturn
    
    def paramsToString(self):
        multiplierGoAndBack = 1
        if self.carsharingMode == "RoundTrip":
            multiplierGoAndBack = 2
        
        parkingTotal = 0
        for node in self.stations:
            parkingTotal += node.station.maxVehicles
        
        stringReturn = str(self.usersNumberDay) + "_" + self.listToString(self.vehiclesNumberRange)
        stringReturn += "_" + self.listToString(self.graphSP.partners) + "_" + str(parkingTotal)
        stringReturn += "_" + self.listToString([x * multiplierGoAndBack for x in self.drivenDistanceLimits]) + "_" + self.listToString([x * multiplierGoAndBack for x in self.usedTimeLimits])
        if self.addParkingConstraints == 'TrueForPartners':
            stringReturn += "_TrueForPartners"
        else:
            stringReturn += "_" + str(self.addParkingConstraints)
        stringReturn += "_" + str(self.thresholdNearStations) + "_"
        return stringReturn
    
    def fareTurbi(self, elapsedTime, drivenDistance):
        fareToBePaid = (8 * elapsedTime/60) + (0.5 * drivenDistance/1000)
        
        return fareToBePaid
    
    def fareZazcar(self, elapsedTime, drivenDistance):
        fareToBePaid = max(20, (10 * elapsedTime/60) + (0.9 * drivenDistance/1000))
        
        return fareToBePaid
    
    def generateLeftAndGotVehicles(self):
        for stationNode in self.stations:
            for user1 in stationNode.station.involvedUsersPos:
                #Remove conflict in a station when a car is delivered to there from other station
                userDestinationStation = self.users[user1].stationEnd
                #Already added on method repeatNearestUsers
                #userDestinationStation.addParkingUsersPos(user1)
                if len(userDestinationStation.involvedUsersPos) > 0:
                    possibleRemoveConflict = []
                    for userDest in userDestinationStation.involvedUsersPos:
                        #Select possible users to remove conflict
                        if self.users[user1].timeEnd < self.users[userDest].timeStart:
                            possibleRemoveConflict.append((self.users[userDest].timeStart, userDest))
                        
                    if len(possibleRemoveConflict) > 0:
                        possibleRemoveConflict.sort()
                        for tup in possibleRemoveConflict:
                            self.users[user1].leftVehicleOneWayToUser.append(tup[1])
                            self.users[tup[1]].gotVehicleOneWayFromUser.append(user1)
    
    def initializeCopiedUser(self, newUser):
        newUser.copiedTo = []
        newUser.leftVehicleOneWayToUser = []
        newUser.gotVehicleOneWayFromUser = []
        
        return newUser
    
    def repeatNearestUsers(self):
        roundTrip = 0
        #To speedup the checking of carsharingMode
        if self.carsharingMode == "RoundTrip":
            roundTrip = 1
        #First repeats regarding the start station
        newUsersStartStation = []
        for i in range(0, len(self.stations) - 1):
            station1 = self.stations[i].station
            for j in range(i + 1, len(self.stations)):
                station2 = self.stations[j].station
                distance = nx.shortest_path_length(self.graphSP.undirectedGraph, station1.node.location, station2.node.location, weight='weight')
                
                if distance < self.thresholdNearStations:
                    station1.nearStations.append(station2)
                    station2.nearStations.append(station1)
                    for userPos in station1.involvedUsersPos:
                        newUser = copy.copy(self.users[userPos])
                        newUser.copiedFrom = userPos
                        newUser = self.initializeCopiedUser(newUser)
                        newUser.stationStart = station2
                        if roundTrip == 1:
                            newUser.stationEnd = newUser.stationStart
                        newUsersStartStation.append(newUser)
                    
                    for userPos in station2.involvedUsersPos:
                        newUser = copy.copy(self.users[userPos])
                        newUser.copiedFrom = userPos
                        newUser = self.initializeCopiedUser(newUser)
                        newUser.stationStart = station1
                        if roundTrip == 1:
                            newUser.stationEnd = newUser.stationStart
                        newUsersStartStation.append(newUser)
                        
        for user in newUsersStartStation:
            newUserPos = len(self.users)
            user.id += '_' + str(newUserPos + 1)
            user.stationStart.addInvolvedUsersPos(newUserPos)
            #user.stationEnd.addParkingUsersPos(newUserPos)
            self.users.append(user)
            self.users[user.copiedFrom].copiedTo.append(newUserPos)
        
        #Add the parkingUsersPos
        newUsersEndStation = []
        for station in self.stations:
            for userPos in station.station.involvedUsersPos:
                userDestinationStation = self.users[userPos].stationEnd
                userDestinationStation.addParkingUsersPos(userPos)
        
        #So, repeats regarding the end station
        #But just if the mode is OneWay
        if roundTrip == 0:
            for i in range(0, len(self.stations) - 1):
                station1 = self.stations[i].station
                for j in range(i + 1, len(self.stations)):
                    station2 = self.stations[j].station
                    distance = nx.shortest_path_length(self.graphSP.undirectedGraph, station1.node.location, station2.node.location, weight='weight')
                    
                    if distance < self.thresholdNearStations:        
                        for userPos in station1.parkingUsersPos:
                            newUser = copy.copy(self.users[userPos])
                            if newUser.copiedFrom == None:
                                newUser.copiedFrom = userPos
                            newUser = self.initializeCopiedUser(newUser)
                            newUser.stationEnd = station2
                            newUsersEndStation.append(newUser)
                    
                        for userPos in station2.parkingUsersPos:
                            newUser = copy.copy(self.users[userPos])
                            if newUser.copiedFrom == None:
                                newUser.copiedFrom = userPos
                            newUser = self.initializeCopiedUser(newUser)
                            newUser.stationEnd = station1
                            newUsersEndStation.append(newUser)
                        
            for user in newUsersEndStation:
                newUserPos = len(self.users)
                user.id += '_' + str(newUserPos + 1)
                user.stationStart.addInvolvedUsersPos(newUserPos)
                user.stationEnd.addParkingUsersPos(newUserPos)
                self.users.append(user)
                self.users[user.copiedFrom].copiedTo.append(newUserPos)
            
    def simulateUsers(self):
        print("Simulating users...")
        sumViagTotal = 0
        for i, caoaNode in enumerate(self.stations):
            if caoaNode.station.maxVehicles != 0:
                sumViagTotal += caoaNode.station.zoneViagTotal
        
        listUsersPerCAOA = []
        sumUsers = 0
        lastResidueInt = 0
        for caoaNode in self.stations:
            if caoaNode.station.maxVehicles != 0:
                usersPerStation = (caoaNode.station.zoneViagTotal * self.usersNumberDay)/sumViagTotal
                #Don't truncate. Instead of it, round and cast to int
                #Residue after rounding
                residue = usersPerStation - int(round(usersPerStation, 0))
                usersPerStation = int(round(usersPerStation + max(0, lastResidueInt), 0))
                listUsersPerCAOA.append((caoaNode, usersPerStation))
                lastResidueInt = residue
    
                sumUsers += usersPerStation
                #if sumUsers >= self.usersNumberDay:
                #    break
            
        if sumUsers >= self.usersNumberDay:
            #Add only the remaining
            #earlierSumUsers = sumUsers - usersPerStation
            #listUsersPerCAOA[-1] = (caoaNode, self.usersNumberDay - earlierSumUsers)
            
            for i in range(sumUsers - self.usersNumberDay):
                #Reduces the lasts positions by one
                listUsersPerCAOA[-(i + 1)] = (listUsersPerCAOA[-(i + 1)][0], listUsersPerCAOA[-(i + 1)][1] - 1)
        else:
            #Add the users who left
            #leftUsers = self.usersNumberDay - sumUsers
            #listUsersPerCAOA[-1] = (caoaNode, usersPerStation + leftUsers)
            
            for i in range(self.usersNumberDay - sumUsers):
                #Increases the lasts positions by one
                listUsersPerCAOA[-(i + 1)] = (listUsersPerCAOA[-(i + 1)][0], listUsersPerCAOA[-(i + 1)][1] + 1)
        
        sumUsers = 0
        for tup in listUsersPerCAOA:
            sumUsers += tup[1]
        
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
        caoaPos = 0
        for caoaNode, usersPerStation in listUsersPerCAOA:
            #Generate and build the parameters whether they don't exist yet
            if self.buildParams == True:
                randomDestinations = nx.single_source_dijkstra_path_length(self.graphSP.graph, caoaNode.station.node.location, self.drivenDistanceLimits[1], weight='weight')
                randomNodeDistances = list(randomDestinations.items())

            for i in range(0, usersPerStation):
                #Generate and build the parameters whether they don't exist yet
                if self.buildParams == True:
                    randomDestiny, randomNodeDistance = choice(randomNodeDistances)
                    #Scenario 1: the car is taken and delivered at the same CAOA station
                    #Multiplier go and back to the same station
                    multiplierGoAndBack = 2
                    #Go from CAOA station to random destiny and back to the same CAOA station
                    drivenDistance = multiplierGoAndBack * randomNodeDistance
                    
                    stationStartTimeRange = max(self.timeDayRange[0], self.timeRangeStation[caoaPos][0])
                    stationEndTimeRange = min(self.timeDayRange[1], self.timeRangeStation[caoaPos][1])
                    
                    #Adjust the driven distance to be between the limits
                    drivenDistance = max(drivenDistance, multiplierGoAndBack * self.drivenDistanceLimits[0])
                    drivenDistance = min(drivenDistance, multiplierGoAndBack * self.drivenDistanceLimits[1])
                    
                    timeStart = randint(stationStartTimeRange, stationEndTimeRange)
                    speed = 10
                    drivenTime = 60 * (drivenDistance/1000)/speed
                    randomTime = multiplierGoAndBack * randint(0, 1 * 60)
                    elapsedTime = min(drivenTime + randomTime, multiplierGoAndBack * self.usedTimeLimits[1])
                    timeEnd = min(timeStart + elapsedTime + self.timeBetweenRents, self.timeRangeStation[caoaPos][2])
                    #Adjust elapsedTime based on time restrictions from end station
                    elapsedTime = timeEnd - timeStart
                    
                    #Now, checks restrictions about start time and driving distance
                    if elapsedTime < multiplierGoAndBack * self.usedTimeLimits[0]:
                        timeStart = max(timeEnd - multiplierGoAndBack * self.usedTimeLimits[0], self.timeRangeStation[caoaPos][0])
                        elapsedTime = timeEnd - timeStart
                        
                        #If elapsedTime is still less than self.usedTimeLimits[0], is it needed to raise the end time
                        if elapsedTime < multiplierGoAndBack * self.usedTimeLimits[0]:
                            timeEnd = min(timeStart + multiplierGoAndBack * self.usedTimeLimits[0] + self.timeBetweenRents, self.timeRangeStation[caoaPos][1])
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
                        randomDestiny = self.graphSP.roadNetwork.nodes[caoaNode.location]
                        print("DESTINY STATION NOT FOUND!!!")
                    
                #Turbi
                #fareToBePaid = self.fareTurbi(elapsedTime, drivenDistance)

                #Zazcar
                fareToBePaid = self.fareZazcar(elapsedTime, drivenDistance)
                
                user = User(str(idUser) + '_' + str(i + 1), caoaNode.station, caoaNode.station, timeStart, timeEnd, randomDestiny, drivenDistance, fareToBePaid)
                
                #This user can be in a restriction among the others from that CAOA station
                caoaNode.station.addInvolvedUsersPos(len(users))
                users.append(user)
                
                idUser += 1
                
            caoaPos += 1
        
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
        
    def persistUsersData(self):
        usersToPersist = []
        for user in self.users:
            if user.copiedFrom == None:
                usersToPersist.append(user)
        
        persistUsersData(usersToPersist, self.carsharingMode, self.usersNumberDay, self.distribution, self.usedTimeLimits[0], self.usedTimeLimits[1], self.drivenDistanceLimits[0], self.drivenDistanceLimits[1], len(self.stations))
    
    def loadUsersData(self):
        return loadUsersData(self.carsharingMode, self.usersNumberDay, self.distribution, self.usedTimeLimits[0], self.usedTimeLimits[1], self.drivenDistanceLimits[0], self.drivenDistanceLimits[1], len(self.stations))
    
    def deleteUsersData(self):
        return deleteUsersData(self.carsharingMode, self.usersNumberDay, self.distribution, self.usedTimeLimits[0], self.usedTimeLimits[1], self.drivenDistanceLimits[0], self.drivenDistanceLimits[1], len(self.stations))

