import networkx as nx
from Control.GraphRoadNetwork import GraphRoadNetwork
from Control.SupplyAndDemandModeling import SupplyAndDemandModeling
from Control.SupplyAndDemandModelingOneWay import SupplyAndDemandModelingOneWay
from Control.Simulation import Simulation

from copy import deepcopy
from Model.DAO.GenerateSheet import generateSheet
from Model.DAO.GenerateCSVs import generateCSVs

for partners in [[True], [False]]:
#for partners in [[False], [True]]:
    graphSPOriginal = GraphRoadNetwork(partners)

    #for usersNumber in [500, 300, 100]:
    for usersNumber in [1000]:
        #for drivenDistance in [[5000, 50000], [1000, 10000]]:
        for drivenDistance in [[5000, 50000]]:
        #    for usedTime in [[45, 4 * 60], [20, 1 * 60]]:
            for usedTime in [[45, 4 * 60]]:
                #for walkingNearStations in [1000, 750, 500, 250, 0]:
                for walkingNearStations in [0, 250, 500]:
                    for parkingConstraints in [False, 'TrueForPartners', True]:
                    #for parkingConstraints in [True]:
                        #Can't add only the parking constraints for Partners, if there isn't Partners
                        if parkingConstraints == 'TrueForPartners' and partners == False:
                            continue
                        
                        graphSP = deepcopy(graphSPOriginal)
                        
                        #Parameters
                        usersNumberDay = usersNumber
                        vehiclesNumberRange = [1, 100]
                        
                        timeBetweenRents = 0 #Number of minutes between two consecutive rents (for cleaning, checking...)
                        
                        timeDayRange = [60*0, 60*24] #Number of minutes in a day that at maximum the Carsharing can work
                        
                        drivenDistanceLimits = drivenDistance
                        usedTimeLimits = usedTime
                        
                        distribution = "Uniforme"
                        
                        forceNewUsersData = False
                        
                        stationsNumber = len(graphSP.roadNetwork.stations)
                        thresholdNearStations = walkingNearStations
                        tolerance = 10
                        timeRangeStation = [[60*8, 60*21, (60*22) + tolerance] for i in range(stationsNumber)]
                        
                        addParkingConstraints = parkingConstraints
                        
                        #Number of seconds for each optimization
                        secondsLimit = 20 * 60
                        #Number of tries to improve the solution
                        triesNumber = 3
                        
                        demandSimulation = SupplyAndDemandModelingOneWay(usersNumberDay, vehiclesNumberRange, timeRangeStation, timeDayRange, drivenDistanceLimits, usedTimeLimits, timeBetweenRents, graphSP, distribution, forceNewUsersData, addParkingConstraints, thresholdNearStations, secondsLimit, triesNumber)
                        demandSimulation.simulateUsers()
                        
                        simulation = Simulation(demandSimulation)
                        simulation.simulate()

generateSheet('/Users/cristianomartinsm/Dropbox/UFMG/Cristiano/Doutorado/Projeto Montadora CAOA/Arquivos Problema Otimização/Resultados/')
generateCSVs('/Users/cristianomartinsm/Dropbox/UFMG/Cristiano/Doutorado/Projeto Montadora CAOA/Arquivos Problema Otimização/Resultados/')

