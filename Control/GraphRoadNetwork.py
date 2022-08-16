from Model.DAO.LoadRoadNetwork import importRoadNetwork
import networkx as nx

class GraphRoadNetwork():
    def __init__(self, partners):
        self.partners = partners
        self.roadNetwork = importRoadNetwork(self.partners)
        self.graph = nx.DiGraph()
        self.graph.add_weighted_edges_from(self.roadNetwork.edges)
        
        self.undirectedGraph = self.graph.to_undirected()