from Model.DAO.Connection import Connection
from Model.RoadNetwork import Station, Node, RoadNetwork

def storeEdge(startNode, endNode, length, oneway, edges):
    edge = (startNode.location, endNode.location, length)
    #edges = np.vstack((edges, edge))
    edges.append(edge)
    #Whether the road segment isn't oneway, a second directed edge must be created
    if oneway != 1:
        edge = (endNode.location, startNode.location, length)
        #edges = np.vstack((edges, edge))
        edges.append(edge)
    return edges

def includeStationsIntoNetwork(rows, nodes, stationsCAOA, edges, isPartner=False):
    for row in rows:
        stationName, maxVehicles, zoneName, zoneProduction, zoneAttraction, zoneViagTotal, location1, locationCAOA, location2, dist1, dist2, oneway = row
        #Defining nodes
        startNode = nodes[location1]
        endNode = nodes[location2]
        stationNode = Node(locationCAOA)
        #Parameters to be really set after
        involvedUsersPos = []
        parkingUsersPos = []
        station = Station(stationNode, stationName, zoneName, zoneProduction, zoneAttraction, zoneViagTotal, involvedUsersPos, parkingUsersPos, int(maxVehicles), isPartner)
        stationNode.station = station
        nodes[stationNode.location] = stationNode
        stationsCAOA.append(stationNode)
        
        #Defining edges
        edges = storeEdge(startNode, stationNode, dist1, oneway, edges)
        edges = storeEdge(stationNode, endNode, dist2, oneway, edges)
    
    return nodes, stationsCAOA, edges

def importStations(conn, nodes, stationsCAOA, edges):
    print("Adding the Stations...")
    cur = conn.cursor()
    #get the closest edge to a Station station
    cur.execute("select Station.NOME||' - '||Station.RAZAOSOCIA, Station.VAGAS, ZONAS_ORIGENS.NOME_1, " +
                "    (ZONAS_ORIGENS.CONDAUTO + ZONAS_ORIGENS.PAXAUTO + ZONAS_ORIGENS.TAXI + ZONAS_ORIGENS.MOTO + ZONAS_ORIGENS.OUTROS)/st_area(ZONAS_ORIGENS.GEOM) as ORIGENS_PRODUCAO, " +
                "    (ZONAS_DESTINOS.CONDAUTO + ZONAS_DESTINOS.PAXAUTO + ZONAS_DESTINOS.TAXI + ZONAS_DESTINOS.MOTO + ZONAS_DESTINOS.OUTROS)/st_area(ZONAS_DESTINOS.GEOM) as DESTINOS_ATRACAO, " +
                "    (ZONAS_ORIGENS.CONDAUTO + ZONAS_ORIGENS.PAXAUTO + ZONAS_ORIGENS.TAXI + ZONAS_ORIGENS.MOTO + ZONAS_ORIGENS.OUTROS + ZONAS_DESTINOS.CONDAUTO + ZONAS_DESTINOS.PAXAUTO + ZONAS_DESTINOS.TAXI + ZONAS_DESTINOS.MOTO + ZONAS_DESTINOS.OUTROS)/st_area(ZONAS_ORIGENS.GEOM) as ORIGENS_DESTINOS_SOMA, "
                "    substr(st_astext(SOURCE_NODE.GEOM), 6), " +
                "    substr(st_astext(st_force2d(Station.GEOM)), 6), " +
                "    substr(st_astext(TARGET_NODE.GEOM), 6), " +
                "    st_length(geography(st_linesubstring(M.GEOM, " +
                "        st_linelocatepoint(M.GEOM, SOURCE_NODE.GEOM), " +
                "        st_linelocatepoint(M.GEOM, st_force2d(Station.GEOM)) " +
                "    ))), " +
                "    st_length(geography(st_linesubstring(M.GEOM, " +
                "        st_linelocatepoint(M.GEOM, st_force2d(Station.GEOM)), " +
                "        st_linelocatepoint(M.GEOM, TARGET_NODE.GEOM) " +
                "    ))), " +
                "    M.ONE_WAY " +
                "from WAYS as M, WAYS_VERTICES_PGR as SOURCE_NODE, WAYS_VERTICES_PGR as TARGET_NODE, CAOA_F as Station, " + #LOJAS_CAOA as Station, " +
                "    DISTRITOS_SP_ZONASOD2007_MODOSVIAGENSORIGENS ZONAS_ORIGENS, DISTRITOS_SP_ZONASOD2007_MODOSVIAGENSDESTINOS ZONAS_DESTINOS " +
                "where Station.VAGAS > 0 and " +
                "    M.SOURCE = SOURCE_NODE.ID and M.TARGET = TARGET_NODE.ID and " +
                "    ZONAS_ORIGENS.ID_1 = ZONAS_DESTINOS.ID_1 and " +
                "    st_contains(ZONAS_ORIGENS.GEOM, st_force2d(Station.GEOM)) and  " +
                "    M.GID = (select M2.GID " +
                "            from WAYS as M2 " +
                "            where st_dwithin(geography(M2.GEOM), geography(Station.GEOM), 50) " +
                "            order by st_distance(M2.GEOM, st_force2d(Station.GEOM), false) " +
                "            limit 1) " +
                "order by ZONAS_ORIGENS.POP2007 DESC, ORIGENS_PRODUCAO DESC, DESTINOS_ATRACAO DESC")
    rows = cur.fetchall()
    cur.close()
    
    nodes, stationsCAOA, edges = includeStationsIntoNetwork(rows, nodes, stationsCAOA, edges)
    
    return nodes, stationsCAOA, edges

def importParkingPartners(conn, nodes, stationsCAOA, edges):
    print("Adding the Parking Partners...")
    cur = conn.cursor()
    #get the closest edge to a Station station
    cur.execute("select Station.RAZAO||' - '||Station.BAIRRO, Station.VAGAS, ZONAS_ORIGENS.NOME_1, " +
                "    (ZONAS_ORIGENS.CONDAUTO + ZONAS_ORIGENS.PAXAUTO + ZONAS_ORIGENS.TAXI + ZONAS_ORIGENS.MOTO + ZONAS_ORIGENS.OUTROS)/st_area(ZONAS_ORIGENS.GEOM) as ORIGENS_PRODUCAO, " +
                "    (ZONAS_DESTINOS.CONDAUTO + ZONAS_DESTINOS.PAXAUTO + ZONAS_DESTINOS.TAXI + ZONAS_DESTINOS.MOTO + ZONAS_DESTINOS.OUTROS)/st_area(ZONAS_DESTINOS.GEOM) as DESTINOS_ATRACAO, " +
                "    (ZONAS_ORIGENS.CONDAUTO + ZONAS_ORIGENS.PAXAUTO + ZONAS_ORIGENS.TAXI + ZONAS_ORIGENS.MOTO + ZONAS_ORIGENS.OUTROS + ZONAS_DESTINOS.CONDAUTO + ZONAS_DESTINOS.PAXAUTO + ZONAS_DESTINOS.TAXI + ZONAS_DESTINOS.MOTO + ZONAS_DESTINOS.OUTROS)/st_area(ZONAS_ORIGENS.GEOM) as ORIGENS_DESTINOS_SOMA, "
                "    substr(st_astext(SOURCE_NODE.GEOM), 6), " +
                "    substr(st_astext(st_force2d(Station.GEOM)), 6), " +
                "    substr(st_astext(TARGET_NODE.GEOM), 6), " +
                "    st_length(geography(st_linesubstring(M.GEOM, " +
                "        st_linelocatepoint(M.GEOM, SOURCE_NODE.GEOM), " +
                "        st_linelocatepoint(M.GEOM, st_force2d(Station.GEOM)) " +
                "    ))), " +
                "    st_length(geography(st_linesubstring(M.GEOM, " +
                "        st_linelocatepoint(M.GEOM, st_force2d(Station.GEOM)), " +
                "        st_linelocatepoint(M.GEOM, TARGET_NODE.GEOM) " +
                "    ))), " +
                "    M.ONE_WAY " +
                "from WAYS as M, WAYS_VERTICES_PGR as SOURCE_NODE, WAYS_VERTICES_PGR as TARGET_NODE, ESTA_PAR as Station, " + 
                "    DISTRITOS_SP_ZONASOD2007_MODOSVIAGENSORIGENS ZONAS_ORIGENS, DISTRITOS_SP_ZONASOD2007_MODOSVIAGENSDESTINOS ZONAS_DESTINOS " +
                "where Station.VAGAS > 0 and " +
                "    M.SOURCE = SOURCE_NODE.ID and M.TARGET = TARGET_NODE.ID and " +
                "    ZONAS_ORIGENS.ID_1 = ZONAS_DESTINOS.ID_1 and " +
                "    st_contains(ZONAS_ORIGENS.GEOM, st_force2d(Station.GEOM)) and  " +
                "    M.GID = (select M2.GID " +
                "            from WAYS as M2 " +
                "            where st_dwithin(geography(M2.GEOM), geography(Station.GEOM), 100) " +
                "            order by st_distance(M2.GEOM, st_force2d(Station.GEOM), false) " +
                "            limit 1) " +
                "order by ZONAS_ORIGENS.POP2007 DESC, ORIGENS_PRODUCAO DESC, DESTINOS_ATRACAO DESC")
    rows = cur.fetchall()
    cur.close()
    
    nodes, stationsCAOA, edges = includeStationsIntoNetwork(rows, nodes, stationsCAOA, edges, True)
    
    return nodes, stationsCAOA, edges

def importRoadNetwork(partners):
    conn = Connection().conn
    
    cur = conn.cursor()
    #get the longitude and latitude of the start and end points from each road segment
    cur.execute("select substr(st_astext(SOURCE_NODE.GEOM), 6), " + 
                "    substr(st_astext(TARGET_NODE.GEOM), 6), " +
                "    st_length(geography(M.GEOM)), " +
                "    M.ONE_WAY " +
                "from WAYS M, WAYS_VERTICES_PGR as SOURCE_NODE, WAYS_VERTICES_PGR as TARGET_NODE " +
                "where M.SOURCE = SOURCE_NODE.ID and M.TARGET = TARGET_NODE.ID ")
    rows = cur.fetchall()
    cur.close()
    
    print("Building the Road Network...")
    nodes = {}
    edges = []
    for row in rows:
        location1, location2, length, oneway = row
        #Defining nodes
        startNode = Node(location1)
        nodes[location1] = startNode
        
        endNode = Node(location2)
        nodes[location2] = endNode

        #Defining edge
        edges = storeEdge(startNode, endNode, length, oneway, edges)
    

    stationsCAOA = []
    nodes, stationsCAOA, edges = importStations(conn, nodes, stationsCAOA, edges)
    
    if partners[0] == True:
        nodes, stationsCAOA, edges = importParkingPartners(conn, nodes, stationsCAOA, edges)
    
    conn.close()
    
    roadNetwork = RoadNetwork(nodes, edges, stationsCAOA)
    
    return roadNetwork
