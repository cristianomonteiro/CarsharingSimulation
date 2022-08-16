from pulp import LpProblem, LpMinimize, LpVariable, LpBinary, LpInteger, LpStatus, solvers
import numpy as np
#from bisect import bisect_left, insort_left
import matplotlib.pyplot as plt
#from sys import maxsize
#from matplotlib.ticker import MaxNLocator
from unidecode import unidecode
from math import floor
from Utils.Methods import generateTicks

import time

#from copy import deepcopy
#from sys import setrecursionlimit
#setrecursionlimit(9999999)

class Simulation():
    def __init__(self, demandSimulation):
        self.users = demandSimulation.users
        self.usersNumberDay = demandSimulation.usersNumberDay
        self.stations = demandSimulation.stations
        self.vehiclesNumberRange = demandSimulation.vehiclesNumberRange
        self.timeRangeStation = demandSimulation.timeRangeStation
        self.usedTimeLimits = demandSimulation.usedTimeLimits
        self.addParkingConstraints = demandSimulation.addParkingConstraints
        self.carsharingMode = demandSimulation.carsharingMode
        
        self.secondsLimit = demandSimulation.secondsLimit
        self.maxNotSolved = demandSimulation.triesNumber
        self.countNotSolved = 0
        
        self.timeBetweenRents = demandSimulation.timeBetweenRents
        
        self.stringParams = demandSimulation.paramsToString()
        print('Optimizing ' + self.stringParams + self.carsharingMode)
        
        self.multiplierGoAndBack = 1
        self.folderPath = '/Users/cristianomartinsm/Dropbox/UFMG/Cristiano/Doutorado/Projeto Montadora CAOA/Arquivos Problema Otimização/Resultados/'
        if self.carsharingMode == "RoundTrip":
            self.resultsFilePath = self.folderPath + self.stringParams + 'ResultsRoundTrip.txt'
            
            self.graphFilePathRevenueVehicles = self.folderPath + self.stringParams + 'FigureRoundTrip_Revenue_Vehicles.png'
            self.graphFilePathRevenueClients = self.folderPath + self.stringParams + 'FigureRoundTrip_Revenue_Clients.png'
            self.graphFilePathVehiclesClients = self.folderPath + self.stringParams + 'FigureRoundTrip_Vehicles_Clients.png'
            self.multiplierGoAndBack = 2
        else:
            self.resultsFilePath = self.folderPath + self.stringParams + 'ResultsOneWay.txt'
            
            self.graphFilePathRevenueVehicles = self.folderPath + self.stringParams + 'FigureOneWay_Revenue_Vehicles.png'
            self.graphFilePathRevenueClients = self.folderPath + self.stringParams + 'FigureOneWay_Revenue_Clients.png'
            self.graphFilePathVehiclesClients = self.folderPath + self.stringParams + 'FigureOneWay_Vehicles_Clients.png'
    
    def loadNextVehicleNumberToOptimize(self):
        nextVehicleNumberToOptimize = self.vehiclesNumberRange[0]
        objectiveValue = float("inf")
        status = 0
        
        with open(self.resultsFilePath) as f:
            for line in reversed(list(f)):
                lineSplitted = line.split()
                if len(lineSplitted) > 1 and lineSplitted[0] == 'Sum' and lineSplitted[1] == 'F2:':
                    nextVehicle = round(float(lineSplitted[2])) + 1
                    if nextVehicle > nextVehicleNumberToOptimize:
                        nextVehicleNumberToOptimize = nextVehicle
                        
                elif len(lineSplitted) > 1 and lineSplitted[0] == 'Objective' and lineSplitted[1] == 'Value:':
                    objectiveValue = float(lineSplitted[2])
                    
                elif len(lineSplitted) > 1 and lineSplitted[0] == 'Status:':
                    statusText = ' '.join(str(e) for e in lineSplitted[1:])
                    status = (1 if statusText == 'Optimal' else 0)
                    break
                
        f.close()
        
        return nextVehicleNumberToOptimize, objectiveValue, status
    
    def setDefaultLambdas(self):
        self.pLambda = 0.9
        self.lambdaF1 = 1 - self.pLambda
        self.lambdaF2 = self.pLambda
        
    def invertLambdas(self):
        self.lambdaF1, self.lambdaF2 = self.lambdaF2, self.lambdaF1
    
    def setProblem(self, invertLambdas=False):
        self.prob = LpProblem("The Carsharing Problem with PuLP ", LpMinimize)
        
        self.sumF1 = 0
        self.variablesF1 = np.array([])
        for user in self.users:
            variableF1 = LpVariable("f1_" + user.id, lowBound=0, upBound=1, cat=LpBinary)
            self.variablesF1 = np.hstack((self.variablesF1, variableF1))
            #self.sumF1 += user.fareToBePaid * variableF1
            #Maximizing just the number of attended users
            self.sumF1 += variableF1
        
        self.sumF2 = 0
        self.variablesF2 = np.array([])
        #self.variablesF2NonConflict = np.array([])
        for caoaNode in self.stations:
            variableF2 = LpVariable("f2_" + unidecode(caoaNode.station.name) + "_" + caoaNode.location, lowBound=0, upBound=None, cat=LpInteger)
            self.variablesF2 = np.hstack((self.variablesF2, variableF2))
            #second CAOA variable to hold the non-conflicting users
            #variableF2NonConflict = LpVariable("f2_non-conflict_" + caoaNode.station.name + "_" + caoaNode.location, lowBound=0, upBound=None, cat=LpBinary)
            #self.variablesF2NonConflict = np.hstack((self.variablesF2NonConflict, variableF2NonConflict))

            self.sumF2 += variableF2# + variableF2NonConflict
        
        self.setDefaultLambdas()
        if invertLambdas == True:
            self.invertLambdas()
            
        #Define the auxiliary variable to Minimize the Greatest number of vehicles among stations
        self.auxGreatestVariableF2 = LpVariable("f2_Aux_Greater_Variable", lowBound=0, upBound=None, cat=LpInteger)
        
        #F1 has maximization nature, that's why it is negative
        self.f1Objective = -1*(self.lambdaF1 * self.sumF1)
        
        #f2Objective = self.lambdaF2 * self.sumF2
        #F2 now is about minimization of the greater number of vehicles among stations
        self.parkingMax = []
        self.parkingsNumber = 0
        for node in self.stations:
            self.parkingMax.append(node.station.maxVehicles)
            self.parkingsNumber += node.station.maxVehicles
        self.parkingMax = max(self.parkingMax)
        
        numDigits = len(str(self.parkingMax))
        toBeRaised = 0.01
        #Get the lower number between self.lambdaF2 and the other calculated by the number of parkings
        self.lambdaF2 = min(pow(toBeRaised, numDigits), self.lambdaF2)
        self.f2Objective = self.lambdaF2 * self.auxGreatestVariableF2
        
        self.prob += self.f1Objective + self.f2Objective, "Plambda,epsilon minimizing the total vehicles number and maximizing the revenues"
        
        self.setRestrictions()
        
        print("Problem builded.")
    
    def setRestrictionsParkedOneWay(self, caoaNode, variableF2Pos, parkingUsersSorted, involvedUsersSorted):
        parkedUsersArriving = []
        for tup1 in parkingUsersSorted:
            userPos = tup1[1]
            parkedUsersArriving.append(self.variablesF1[userPos])
            
            earlierUsers = []
            for tup2 in involvedUsersSorted:
                userInvolvedPos = tup2[1]
                if self.users[userInvolvedPos].timeStart <= self.users[userPos].timeEnd:
                    earlierUsers.append(self.variablesF1[userInvolvedPos])
                else:
                    break
                    
            #Assures that on the OneWay, the number of vehicles parked in the station won't surpass its maximum allowed
            constraintF2 = self.variablesF2[variableF2Pos] + parkedUsersArriving - earlierUsers <= caoaNode.station.maxVehicles
            self.prob += constraintF2, "max vehicles parked allowed in station " + str(userPos)
    
    def convertOneWayReceivedToSent(self, posReceived):
        posSentListUniqueItems = []
        
        for received in posReceived:
            posSentListUniqueItems.extend(self.users[received].gotVehicleOneWayFromUser)
        
        posSentListUniqueItems = list(set(posSentListUniqueItems))
        return posSentListUniqueItems
    
    def setRestrictions(self):
        self.sentToReceivedOneWayRecorded = []
        
        #1 -> 10, 24 -> 87
        BIGM = 9999#maxsize
        for variableF2Pos, caoaNode in enumerate(self.stations):
            usersSorted = [(self.users[x].timeStart, x, self.users[x]) for x in caoaNode.station.involvedUsersPos]
            usersSorted.sort()
            
            parkingUsersSorted = [(self.users[x].timeEnd, x, self.users[x]) for x in caoaNode.station.parkingUsersPos]
            parkingUsersSorted.sort()
            
            if self.carsharingMode == "OneWay" and (self.addParkingConstraints == True or (self.addParkingConstraints == 'TrueForPartners' and caoaNode.station.isPartner == True)):
                self.setRestrictionsParkedOneWay(caoaNode, variableF2Pos, usersSorted, parkingUsersSorted)
            
            earlierUsers = []
            for tup in usersSorted:
                userPos = tup[1]
                    
                uniqueSentIntersectionConflicts = self.convertOneWayReceivedToSent([userPos])
                oneWayVariables = self.variablesF1[uniqueSentIntersectionConflicts]

                constraintF1 = self.variablesF1[userPos] <= self.variablesF2[variableF2Pos] + oneWayVariables - earlierUsers
                self.prob += constraintF1, "user conflicting order " + str(self.users[userPos].id)
                
                if len(self.users[userPos].copiedTo) > 0:
                    #The original user has preference
                    BIGM = caoaNode.station.maxVehicles + len(oneWayVariables)
                    constraintF1 = self.variablesF1[userPos] * BIGM >= self.variablesF2[variableF2Pos] + oneWayVariables - earlierUsers
                    self.prob += constraintF1, "user conflicting order BIGM original user has preference " + str(self.users[userPos].id)
                                        
                    copiedToPos = self.users[userPos].copiedTo
                    constraintF1 = self.variablesF1[userPos] + sum(self.variablesF1[copiedToPos]) <= 1
                    self.prob += constraintF1, "limiting user to one start and one end station " + str(self.users[userPos].id)
            
                    #usersCopiedFromThisStation = set([userPos] + self.users[userPos].copiedTo).intersection(set(self.stations[variableF2Pos].station.involvedUsersPos))
                    #usersCopiedFromThisStation = list(usersCopiedFromThisStation)

                    #constraintF1 = sum(self.variablesF1[usersCopiedFromThisStation]) <= self.variablesF2[variableF2Pos] + oneWayVariables - earlierUsers
                    #self.prob += constraintF1, "user conflicting order usersCopiedFromThisStation " + str(self.users[userPos].id)
                
                    #constraintF1 = sum(self.variablesF1[usersCopiedFromThisStation]) * BIGM >= self.variablesF2[variableF2Pos] + oneWayVariables - earlierUsers
                    #self.prob += constraintF1, "user conflicting order BIGM " + str(self.users[userPos].id)
                
                #If userPos doesn't have copies and isn't copied from other user
                #It is really needed when thresholdNearStations = 0
                elif self.users[userPos].copiedFrom == None:
                    BIGM = caoaNode.station.maxVehicles + len(oneWayVariables)
                    constraintF1 = self.variablesF1[userPos] * BIGM >= self.variablesF2[variableF2Pos] + oneWayVariables - earlierUsers
                    self.prob += constraintF1, "user conflicting order BIGM with no copies" + str(self.users[userPos].id)
                
                #If userPos was copied from other user
                elif self.users[userPos].copiedFrom != None:
                    copiedFrom = self.users[userPos].copiedFrom
                    copiedTogether = self.users[copiedFrom].copiedTo
                    
                    #If this station has a available vehicle, at least one user copiedTogether with userPos must have value 1
                    possiblesBIGM = []
                    possiblesUsers = [copiedFrom] + copiedTogether
                    for possibleUser in possiblesUsers:
                        uniqueSentIntersectionConflicts = self.convertOneWayReceivedToSent([possibleUser])
                        possiblesBIGM.append(self.users[possibleUser].stationStart.maxVehicles + len(uniqueSentIntersectionConflicts))

                    BIGM = max(possiblesBIGM)
                    constraintF1 = (self.variablesF1[copiedFrom] + sum(self.variablesF1[copiedTogether])) * BIGM >= self.variablesF2[variableF2Pos] + oneWayVariables - earlierUsers
                    self.prob += constraintF1, "user conflicting order BIGM with no copies" + str(self.users[userPos].id)

                earlierUsers.append(self.variablesF1[userPos])

            #Tries to speedup the optimization by restricting solutions by the number of attended users
            uniqueSentIntersectionConflicts = self.convertOneWayReceivedToSent(caoaNode.station.involvedUsersPos)
            oneWayVariables = self.variablesF1[uniqueSentIntersectionConflicts]
            constraintF1 = sum(self.variablesF1[caoaNode.station.involvedUsersPos]) <= self.variablesF2[variableF2Pos] + oneWayVariables
            self.prob += constraintF1, "total number of users allowed in the station " + unidecode(caoaNode.station.name) + " based on the number of vehicles "
            
            #Assures that the number of vehicles in the station won't surpass its maximum allowed
            constraintF2 = self.variablesF2[variableF2Pos] <= caoaNode.station.maxVehicles
            self.prob += constraintF2, "max vehicles allowed in station " + unidecode(caoaNode.station.name) + " " + caoaNode.location
            
            #Minimizes the Greatest number of vehicles among the stations
            constraintF2 = self.variablesF2[variableF2Pos] <= self.auxGreatestVariableF2
            self.prob += constraintF2, "minimizing the greatest number of vehicles at the station " + unidecode(caoaNode.station.name) + " " + caoaNode.location
        
        timeRange = []
        for listTimeRange in self.timeRangeStation:
            timeRange.append(listTimeRange[1] - listTimeRange[0])
        maxTimeRange = max(timeRange)

        maxClientsByVehicle = maxTimeRange / ((self.multiplierGoAndBack * self.usedTimeLimits[0]) + self.timeBetweenRents)
        #Checking if the last time to deliver will enable to rent one more time
        if maxClientsByVehicle != floor(maxClientsByVehicle):
            maxClientsByVehicle += floor(maxClientsByVehicle) + 1
        #Assures that the number of users won't surpass the number of users allowed
        constraintF1 = sum(self.variablesF1) <= sum(self.variablesF2) * maxClientsByVehicle
        self.prob += constraintF1, "total number of users allowed based on the number of vehicles "
        
        #Assures that the number of users won't surpass the number of users allowed
        constraintF1 = sum(self.variablesF1) <= self.usersNumberDay
        self.prob += constraintF1, "total number of users allowed "
            
        #Assures that the total sum of vehicles won't surpass the total maximum allowed
        constraintF2 = sum(self.variablesF2) <= self.vehiclesNumberRange[1]
        self.prob += constraintF2, "total max vehicles allowed "
        
    def runPLambdaEpsilon(self, solver=None, secondsLimit=600):
        print("Running optimization...")
        #Set the initial value for last result got
        #nextVehicleNumberToOptimize = 1
        #lastF1 = float("inf")
        #lastStatus = 0
        multiplePrint = 5
        nextVehicleNumberToOptimize, lastF1, lastStatus = self.loadNextVehicleNumberToOptimize()
        for i in range(nextVehicleNumberToOptimize, self.vehiclesNumberRange[1] + 1):
            ##First one iteration
            #if i == self.vehiclesNumberRange[0]:
            #    self.setProblem(invertLambdas=False)
            #    #self.originalProb = deepcopy(self.prob)
            #else:
            #    self.setProblem()
            #    #self.prob = deepcopy(self.originalProb)

            #If it is already being tested simulations with more vehicles than parking number
            if self.parkingsNumber < i:
                break
                
            constraintPEpsilon = sum(self.variablesF2) <= i
            self.prob.constraints["PEpsilon"] = constraintPEpsilon
        
            if solver != None:
                self.prob.solve(solver)
            else:
                self.prob.solve(solvers.PULP_CBC_CMD(maxSeconds=secondsLimit))
                #self.prob.solve(solvers.PULP_CBC_CMD())
            
            #constraintLBNextOptimization = sum(self.variablesF1) >= numAttendedLastOptimization
            #constraintLBNextOptimization = self.f1Objective + self.f2Objective <= self.prob.objective.value()
            #self.prob.constraints["LowerBoundNextOptimization"] = constraintLBNextOptimization
            
            if lastF1 >= self.prob.objective.value():
                if lastF1 != self.prob.objective.value():
                    self.printResults()
                lastF1 = self.prob.objective.value()
                
                self.countNotSolved = 0
            #Give more tries to solve
            elif self.prob.status == 0 and self.countNotSolved < self.maxNotSolved:
                self.countNotSolved += 1
                print("Try " + str(self.countNotSolved) + ", number of vehicles: " + str(i))

            elif self.prob.status == 1:
                lastF1 = self.prob.objective.value()
                self.countNotSolved = 0
                self.printResults()
            
            else:
                if self.prob.status == 0 or (self.prob.status == 1 and lastStatus != 1):
                    self.printResults()
                break
            
            lastStatus = self.prob.status
            
            if i % multiplePrint == 0:
                print("Up to " + str(i) + " vehicles optimized.")
        
    def printResults(self):
        decimalDigitsPrecision = 10
        self.stringToWriteInFile = ""
        self.stringToWriteInFile += "PLambda: " + str(round(self.pLambda, decimalDigitsPrecision)) + "\n"
        self.stringToWriteInFile += "LambdaF1: " + str(round(self.lambdaF1, decimalDigitsPrecision)) + "\n"
        self.stringToWriteInFile += "LambdaF2: " + str(round(self.lambdaF2, decimalDigitsPrecision)) + "\n"
        self.stringToWriteInFile += "Status: " + LpStatus[self.prob.status] + "\n"
        self.stringToWriteInFile += "Objective Value: " + str(round(self.prob.objective.value(), decimalDigitsPrecision)) + "\n\n"

        self.stringToWriteInFile += "Maximization of revenues (F1):\n"
        sumVar = 0
        i = 0
        sumF1 = 0
        for variable, user in zip(self.variablesF1, self.users):
            sumF1 += variable.varValue
            sumVar += user.fareToBePaid * variable.varValue
            varActivatedString = str(round(user.fareToBePaid * variable.varValue, 2))
            self.stringToWriteInFile += ("\t" + variable.name + ": " + str(round(user.fareToBePaid, 2)) + " -> R$" + varActivatedString +
                                   " ~ " + str(round(user.timeStart, 3)) + " " + str(round(user.timeEnd, 3)) )
            self.stringToWriteInFile += ": " + user.stationStart.name + " -> " + user.stationEnd.name
            if len(user.copiedTo) > 0:# and variable.varValue == 1:
                self.stringToWriteInFile += " ~ copied to " + ', '.join(str(e + 1) for e in user.copiedTo)

            if user.stationStart == user.stationEnd:
                self.stringToWriteInFile += " ~ back to station\n"
            else:
                self.stringToWriteInFile += "\n"
            
            #self.stringToWriteInFile += "\tAux variable " + variable.name + " value: " + str(self.variablesF1[int(user.id.split("_")[1]) + len(self.users)].varValue) + "\n"
            
            i += 1
        self.stringToWriteInFile += "Sum F1: " + str(sumVar) + "\n\n"
        
        self.stringToWriteInFile += "Minimization of total number of vehicles (F2):\n"
        sumVar = 0
        #for variable, variableNonConflict, caoaNode in zip(self.variablesF2, self.variablesF2NonConflict, self.stations):
        for variable, caoaNode in zip(self.variablesF2, self.stations):
            numVehicles = variable.varValue# + variableNonConflict.varValue
            sumVar += numVehicles
            #self.stringToWriteInFile += "\t" + caoaNode.station.name + " " + caoaNode.location + " " + str(variable.varValue) + " " + str(variableNonConflict.varValue) + " " + str(numVehicles) + "\n"
            self.stringToWriteInFile += "\t" + caoaNode.station.name + " " + caoaNode.location + " " + str(numVehicles) + "\n"
        self.stringToWriteInFile += "Sum F2: " + str(sumVar) + "\n"
        self.stringToWriteInFile += "Greatest F2: " + str(self.auxGreatestVariableF2.varValue) + "\n"
        self.stringToWriteInFile += "Number of Attended Users: " + str(sumF1) + "\n"
        self.stringToWriteInFile += "_______________________________________________________________\n\n"
        
        self.resultsFile.write(self.stringToWriteInFile)
    
    def plotGraphs(self):
        f1 = np.array([])
        f2 = np.array([])
        numUsers = np.array([])
        with open(self.resultsFilePath, 'r') as fileResults:
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
        fileGraphs = [self.graphFilePathRevenueVehicles, self.graphFilePathRevenueClients, self.graphFilePathVehiclesClients]
        
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
        
    def simulate(self):
        print("Building the optimization...")
        self.resultsFile = open(self.resultsFilePath, 'a+')
        
        #self.setProblem()
        #self.prob.solve(solvers.GLPK_CMD())
        #self.printResults()

        self.setProblem(invertLambdas=True)
        self.runPLambdaEpsilon(secondsLimit=self.secondsLimit)
        
        #self.setProblem(invertLambdas=True)
        #self.prob.solve(solvers.GLPK_CMD(msg=0))
        #self.printResults()

        self.resultsFile.close()
        self.plotGraphs()
        
