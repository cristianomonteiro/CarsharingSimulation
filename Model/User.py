class User():
    def __init__(self, idUser, stationStart, stationEnd, timeStart, timeEnd, destiny, drivenDistance, fareToBePaid):
        self.id = idUser
        self.stationStart = stationStart
        self.stationEnd = stationEnd
        self.timeStart = timeStart
        self.timeEnd = timeEnd
        self.destiny = destiny
        self.drivenDistance = drivenDistance
        self.fareToBePaid = fareToBePaid
        
        #Holds which user uses the vehicle after this user deliver at his end station
        self.leftVehicleOneWayToUser = []
        
        #The reverse. Holds which user delivered the vehicle after OneWay Carsharing
        self.gotVehicleOneWayFromUser = []
        
        self.copiedFrom = None
        self.copiedTo = []