import re

class Station():
    def __init__(self, node, name, zone, zoneProduction, zoneAttraction, zoneViagTotal, involvedUsersPos, parkingUsersPos, maxVehicles, isPartner=False):
        self.node = node
        self.name = name
        self.zone = zone
        self.zoneProduction = zoneProduction
        self.zoneAttraction = zoneAttraction
        self.zoneViagTotal = zoneViagTotal
        self.maxVehicles = maxVehicles
        
        self.involvedUsersPos = involvedUsersPos
        
        self.parkingUsersPos = parkingUsersPos
        
        self.nearStations = []
        self.isPartner = isPartner
    
    def addInvolvedUsersPos(self, posToAdd):
        self.involvedUsersPos.append(posToAdd)
    
    def addParkingUsersPos(self, posToAdd):
        self.parkingUsersPos.append(posToAdd)    
    
class Node():
    def __init__(self, location, stationStart=None):
        locations = re.findall('[+-]?[0-9]+[.]?[0-9]*', location)
        locations = [float(x) for x in locations]
        decimalDigitsPrecision = 6
        self.location = '(' + str(round(locations[0], decimalDigitsPrecision)) + ' ' + str(round(locations[1], decimalDigitsPrecision)) + ')'
        self.station = stationStart

#Edges are just tuples, a class is not needed
        
class RoadNetwork():
    def __init__(self, nodes, edges, stations):
        self.nodes = nodes
        self.edges = edges
        self.stations = stations
